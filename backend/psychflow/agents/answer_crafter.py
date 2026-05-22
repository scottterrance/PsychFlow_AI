"""Agent 5: Answer Crafter - writes witty, concise answers to predicted questions."""

from __future__ import annotations

from ..llm import generate

SYSTEM_PROMPT = """You are a witty but professional interview coach for software engineers.
For every question:
- Give a CONCISE answer (3-5 sentences max)
- Use self-deprecating but confident + light professional humor
- Example style: "I once shipped a feature that broke production at 2am... lesson learned, now I always add that extra test!"
- Make it sound natural and likable for a US tech interviewer.
- End with a positive tie-back to the job."""


async def run(predicted_questions: str, resume: str, job_description: str) -> str:
    user_prompt = (
        "PREDICTED QUESTIONS:\n"
        f"{predicted_questions}\n\n"
        "CANDIDATE RESUME (use as raw material for stories):\n"
        f"{resume}\n\n"
        "JOB DESCRIPTION (for the positive tie-backs):\n"
        f"{job_description}\n\n"
        "Write the candidate's answer for each question, in order."
    )
    return await generate(SYSTEM_PROMPT, user_prompt, temperature=0.8)
