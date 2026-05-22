"""Agent 4: Question Predictor - lists most likely interview questions.

Now augmented with live DuckDuckGo web search so we can pull real
reported interview questions from sources like Glassdoor, LeetCode
discussions, Reddit, etc.

Web search is best-effort: if it fails for any reason the agent falls
back to its old behavior (LLM-only prediction).
"""

from __future__ import annotations

import json
from typing import Any

from ..llm import generate
from ..web import format_for_prompt, search

SYSTEM_PROMPT = """You are an expert at predicting software engineering interview questions.
Using the psychology profile, company analysis, resume, and JD:
- Predict the 8-10 most likely questions (mix of technical + behavioral)
- Rank them by probability (High/Medium)
- For each question, note why this interviewer would ask it

If WEB CONTEXT contains real reported interview questions for this
company (from Glassdoor, LeetCode, Reddit, blog posts, etc.), give
those the highest weight - they are the strongest signal. Mark them
clearly with "(reported)" so the candidate knows it is grounded in
real data, not inference."""


async def run(
    parsed_data: dict[str, Any],
    psychology_profile: str,
    company_analysis: str,
    job_description: str,
    resume: str,
) -> str:
    company = (
        parsed_data.get("company_name")
        or parsed_data.get("company")
        or ""
    )
    job_title = (
        parsed_data.get("job_title")
        or parsed_data.get("title")
        or "software engineer"
    )

    web_context_text = "(no web search performed - company name unknown)"
    if company:
        results = await search(
            f'"{company}" "{job_title}" interview questions experience',
            max_results=5,
        )
        web_context_text = format_for_prompt(results)

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
        f"{resume}\n\n"
        "WEB CONTEXT (real reported interview questions, if found):\n"
        f"{web_context_text}\n"
    )
    return await generate(SYSTEM_PROMPT, user_prompt, temperature=0.6)
