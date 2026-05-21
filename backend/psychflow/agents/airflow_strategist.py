"""Agent 6: Airflow Strategist - the 'killer feature' conversation control playbook."""

from __future__ import annotations

import json
from typing import Any

from ..llm import generate

SYSTEM_PROMPT = """You are the Interview Airflow Master for US software engineering interviews.
Your job is to teach the candidate how to CONTROL the conversation flow.

Given everything:
1. How to steer from technical -> behavioral questions naturally
2. Exact phrases to recover if the interviewer seems bored ("I notice we're deep in tech - would you like me to walk through a real customer impact story instead?")
3. How to use the interviewer's psychology to build rapport
4. Timing tips (when to ask questions back, when to keep short)

Give 4-6 actionable "Airflow Moves" with exact scripts the user can say."""


async def run(
    parsed_data: dict[str, Any],
    psychology_profile: str,
    company_analysis: str,
    predicted_questions: str,
) -> str:
    user_prompt = (
        "STRUCTURED DATA:\n"
        f"{json.dumps(parsed_data, indent=2)}\n\n"
        "PSYCHOLOGY PROFILE:\n"
        f"{psychology_profile}\n\n"
        "COMPANY ANALYSIS:\n"
        f"{company_analysis}\n\n"
        "PREDICTED QUESTIONS:\n"
        f"{predicted_questions}\n"
    )
    return await generate(SYSTEM_PROMPT, user_prompt, temperature=0.75)
