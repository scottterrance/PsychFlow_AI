"""Thin wrapper around Groq's chat completions API.

Uses the free `groq` SDK. Get a free API key at:
https://console.groq.com/keys (sign up with any email, no credit card)
"""

from __future__ import annotations

import os
from functools import lru_cache

from groq import AsyncGroq


@lru_cache(maxsize=1)
def _client() -> AsyncGroq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy backend/.env.example to "
            "backend/.env and paste your free key from "
            "https://console.groq.com/keys"
        )
    return AsyncGroq(api_key=api_key)


def _model() -> str:
    return os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")


async def generate(
    system_prompt: str,
    user_prompt: str,
    *,
    json_mode: bool = False,
    temperature: float = 0.7,
) -> str:
    """Run a single Groq chat completion with a system prompt + user prompt."""

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

    response = await _client().chat.completions.create(**kwargs)
    return (response.choices[0].message.content or "").strip()
