"""Agent 4: Question Predictor - lists most likely interview questions."""

from __future__ import annotations

import json
from typing import Any

from ..llm import generate

SYSTEM_PROMPT = """You are an expert at predicting software engineering interview questions.
Using the psychology profile, company analysis, resume, and JD:
- Predict the 8-10 most likely questions (mix of technical + behavioral)
- Rank them by probability (High/Medium)
- For each question, note why this interviewer would ask it"""


async def run(
    parsed_data: dict[str, Any],
    psychology_profile: str,
    company_analysis: str,
    job_description: str,
    resume: str,
) -> str:
    user_prompt = (
        "STRUCTURED DATA:\n"
        f"{json.dumps(parsed_data, indent=2)}\n\n"
        "PSYCHOLOGY PROFILE:\n"
        f"{psychology_profile}\n\n"
        "COMPANY ANALYSIS:\n"
        f"{company_analysis}\n\n"
        "JOB DESCRIPTION:\n"
        f"{job_description}\n\n"
        "RESUME:\n"
        f"{resume}\n"
    )
    return await generate(SYSTEM_PROMPT, user_prompt, temperature=0.6)
