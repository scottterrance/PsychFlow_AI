"""Agent 3: Company & JD Analyst - extracts company values and skill priorities.

Now augmented with live DuckDuckGo web search so the analysis is grounded
in current, real information about the company (recent news, engineering
blog posts, culture signals) rather than just the LLM's training data.

Web search is best-effort: if it fails for any reason the agent falls
back to its old JD-only behavior.
"""

from __future__ import annotations

from ..llm import generate
from ..web import format_for_prompt, search

SYSTEM_PROMPT = """You are a senior tech recruiter analyst.
Analyze the job description and company.
List:
- Top 5 technical skills they care about
- Top 3 behavioral/cultural values
- Any recent company news or culture clues (US tech context)

Use the WEB CONTEXT (if provided) to ground your analysis in current,
real information. When you cite a fact from WEB CONTEXT, mention it
naturally (e.g. "they recently announced a $5M Series A round" or
"their engineering blog emphasizes async remote-first work"). If
WEB CONTEXT is empty or unhelpful, fall back to the JD only.

Output in clear bullet points."""


async def run(job_description: str, company_hint: str = "") -> str:
    web_context_text = "(no web search performed - company name unknown)"
    if company_hint:
        results = await search(
            f"{company_hint} engineering culture recent news",
            max_results=5,
        )
        web_context_text = format_for_prompt(results)

    user_prompt = (
        f"COMPANY HINT: {company_hint or '(unknown)'}\n\n"
        "WEB CONTEXT:\n"
        f"{web_context_text}\n\n"
        "JOB DESCRIPTION:\n"
        f"{job_description}\n"
    )
    return await generate(SYSTEM_PROMPT, user_prompt, temperature=0.5)
