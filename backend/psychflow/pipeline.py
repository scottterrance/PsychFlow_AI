"""Orchestrates the 6 agents into a single end-to-end run.

Flow:
    1. parser
    2. psychologist  + 3. company_analyst   (in parallel)
    4. question_predictor
    5. answer_crafter
    6. airflow_strategist
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from .agents import (
    airflow_strategist,
    answer_crafter,
    company_analyst,
    parser,
    psychologist,
    question_predictor,
)


async def run_pipeline(
    recruiter_message: str,
    job_description: str,
    resume: str,
) -> dict[str, Any]:
    # Step 1: parse
    parsed_data = await parser.run(recruiter_message, job_description, resume)

    company_hint = ""
    if isinstance(parsed_data, dict):
        company_hint = str(parsed_data.get("company_name") or parsed_data.get("company") or "")

    # Steps 2 + 3: run in parallel
    psychology_profile, company_analysis = await asyncio.gather(
        psychologist.run(parsed_data),
        company_analyst.run(job_description, company_hint=company_hint),
    )

    # Step 4: predict questions
    predicted_questions = await question_predictor.run(
        parsed_data, psychology_profile, company_analysis, job_description, resume
    )

    # Steps 5 + 6: run in parallel - both depend only on stages 1-4
    crafted_answers, airflow_strategy = await asyncio.gather(
        answer_crafter.run(predicted_questions, resume, job_description),
        airflow_strategist.run(
            parsed_data, psychology_profile, company_analysis, predicted_questions
        ),
    )

    markdown_report = _build_markdown(
        parsed_data,
        psychology_profile,
        company_analysis,
        predicted_questions,
        crafted_answers,
        airflow_strategy,
    )

    return {
        "parsed_data": parsed_data,
        "psychology_profile": psychology_profile,
        "company_analysis": company_analysis,
        "predicted_questions": predicted_questions,
        "crafted_answers": crafted_answers,
        "airflow_strategy": airflow_strategy,
        "markdown_report": markdown_report,
    }


def _build_markdown(
    parsed_data: dict[str, Any],
    psychology_profile: str,
    company_analysis: str,
    predicted_questions: str,
    crafted_answers: str,
    airflow_strategy: str,
) -> str:
    return (
        "# PsychFlow AI - Interview Prep Report\n\n"
        "## 1. Extracted Data\n\n"
        "```json\n"
        f"{json.dumps(parsed_data, indent=2)}\n"
        "```\n\n"
        "## 2. Interviewer Psychology Profile\n\n"
        f"{psychology_profile}\n\n"
        "## 3. Company & JD Analysis\n\n"
        f"{company_analysis}\n\n"
        "## 4. Predicted Questions\n\n"
        f"{predicted_questions}\n\n"
        "## 5. Crafted Answers\n\n"
        f"{crafted_answers}\n\n"
        "## 6. Airflow Strategy\n\n"
        f"{airflow_strategy}\n"
    )
