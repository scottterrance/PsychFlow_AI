"""Agent 3: Company & JD Analyst - extracts company values and skill priorities."""

from __future__ import annotations

from ..llm import generate

SYSTEM_PROMPT = """You are a senior tech recruiter analyst.
Analyze the job description and company.
List:
- Top 5 technical skills they care about
- Top 3 behavioral/cultural values
- Any recent company news or culture clues (US tech context)
Output in clear bullet points."""


async def run(job_description: str, company_hint: str = "") -> str:
    user_prompt = (
        f"COMPANY HINT (optional): {company_hint}\n\n"
        "JOB DESCRIPTION:\n"
        f"{job_description}\n"
    )
    return await generate(SYSTEM_PROMPT, user_prompt, temperature=0.5)
