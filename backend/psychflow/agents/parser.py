"""Agent 1: Data Parser - extracts structured info from raw inputs."""

from __future__ import annotations

import json
from typing import Any

from ..llm import generate

SYSTEM_PROMPT = """You are an expert data extractor for software engineering interviews.
Extract cleanly:
- Recruiter full name
- Company name
- Job title
- Any clues about interviewer (years of experience, university, previous companies, location)
- Resume highlights (top 5 skills/projects)
Output only in JSON format. Be precise."""


async def run(recruiter_message: str, job_description: str, resume: str) -> dict[str, Any]:
    user_prompt = (
        "RECRUITER MESSAGE:\n"
        f"{recruiter_message}\n\n"
        "JOB DESCRIPTION:\n"
        f"{job_description}\n\n"
        "RESUME:\n"
        f"{resume}\n"
    )
    raw = await generate(
        SYSTEM_PROMPT, user_prompt, json_mode=True, temperature=0.2
    )
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fall back to wrapping the raw text so the pipeline keeps moving.
        return {"raw": raw, "warning": "model did not return valid JSON"}
