"""Thin wrapper around Google's Gemini API.

Uses the free `google-genai` SDK. Get a free API key at:
https://aistudio.google.com/apikey
"""

from __future__ import annotations

import asyncio
import os
from functools import lru_cache

from google import genai
from google.genai import types


@lru_cache(maxsize=1)
def _client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Copy backend/.env.example to "
            "backend/.env and paste your free key from "
            "https://aistudio.google.com/apikey"
        )
    return genai.Client(api_key=api_key)


def _model() -> str:
    return os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")


async def generate(
    system_prompt: str,
    user_prompt: str,
    *,
    json_mode: bool = False,
    temperature: float = 0.7,
) -> str:
    """Run a single Gemini call with a system prompt + user prompt.

    Runs the blocking SDK call in a worker thread so the FastAPI event loop
    stays free.
    """

    config_kwargs = {
        "system_instruction": system_prompt,
        "temperature": temperature,
    }
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"

    config = types.GenerateContentConfig(**config_kwargs)

    def _call() -> str:
        response = _client().models.generate_content(
            model=_model(),
            contents=user_prompt,
            config=config,
        )
        return (response.text or "").strip()

    return await asyncio.to_thread(_call)
