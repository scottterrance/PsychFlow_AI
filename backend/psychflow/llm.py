"""Thin wrapper around Groq's chat completions API.

Uses the free `groq` SDK. Get a free API key at:
https://console.groq.com/keys (sign up with any email, no credit card)
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from functools import lru_cache

from groq import APIConnectionError, AsyncGroq, RateLimitError

logger = logging.getLogger("psychflow.llm")

# How many times we retry a single agent call on rate-limit errors before
# giving up. The Groq SDK already retries internally for short blips; this
# is the outer loop that respects the long waits Groq sometimes requests
# (e.g. "try again in 11.985s").
MAX_RATE_LIMIT_ATTEMPTS = 4

# Hard cap on any single sleep so a misparsed value can't hang the request.
MAX_SLEEP_SECONDS = 30.0


@lru_cache(maxsize=1)
def _client() -> AsyncGroq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy backend/.env.example to "
            "backend/.env and paste your free key from "
            "https://console.groq.com/keys"
        )
    # max_retries=2 covers transient 5xx / connection blips. Rate limits are
    # handled by our explicit retry loop below so we can wait the full time
    # Groq tells us to wait.
    return AsyncGroq(api_key=api_key, max_retries=2)


def _model() -> str:
    return os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")


def _parse_retry_after(error: RateLimitError) -> float:
    """Extract the wait time Groq suggests, in seconds.

    Groq returns messages like:
        "Rate limit reached ... Please try again in 11.985s."
    """
    message = str(error)
    match = re.search(r"try again in\s+(\d+(?:\.\d+)?)\s*s", message, re.IGNORECASE)
    if match:
        return float(match.group(1))
    # Fall back to the standard HTTP Retry-After header if present.
    response = getattr(error, "response", None)
    if response is not None:
        retry_after = response.headers.get("retry-after") if hasattr(response, "headers") else None
        if retry_after:
            try:
                return float(retry_after)
            except (TypeError, ValueError):
                pass
    return 0.0


async def generate(
    system_prompt: str,
    user_prompt: str,
    *,
    json_mode: bool = False,
    temperature: float = 0.7,
) -> str:
    """Run a single Groq chat completion with a system prompt + user prompt.

    Retries automatically on rate-limit errors, respecting the wait time
    Groq suggests. Raises the underlying error if all attempts are exhausted.
    """

    kwargs: dict = {
        "model": _model(),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
    }
    if json_mode:
        # Groq supports OpenAI-style JSON mode. The prompt must mention "JSON"
        # (our parser system prompt already does).
        kwargs["response_format"] = {"type": "json_object"}

    last_error: Exception | None = None
    for attempt in range(1, MAX_RATE_LIMIT_ATTEMPTS + 1):
        try:
            response = await _client().chat.completions.create(**kwargs)
            return (response.choices[0].message.content or "").strip()
        except RateLimitError as exc:
            last_error = exc
            suggested = _parse_retry_after(exc)
            # If Groq gave us a wait time, respect it (plus a small buffer).
            # Otherwise fall back to exponential backoff: 4s, 8s, 16s.
            wait = suggested + 1.0 if suggested else 2.0 ** (attempt + 1)
            wait = min(wait, MAX_SLEEP_SECONDS)
            if attempt >= MAX_RATE_LIMIT_ATTEMPTS:
                logger.warning(
                    "Groq rate limit hit, all %d attempts exhausted",
                    MAX_RATE_LIMIT_ATTEMPTS,
                )
                break
            logger.info(
                "Groq rate limit hit (attempt %d/%d), waiting %.1fs",
                attempt,
                MAX_RATE_LIMIT_ATTEMPTS,
                wait,
            )
            await asyncio.sleep(wait)
        except APIConnectionError as exc:
            # Bubble up — the SDK already retried these.
            raise exc

    assert last_error is not None
    raise last_error
