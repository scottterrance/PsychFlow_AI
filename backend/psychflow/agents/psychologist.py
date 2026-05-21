"""Agent 2: Interviewer Psychologist - profiles the recruiter/interviewer."""

from __future__ import annotations

import json
from typing import Any

from ..llm import generate

SYSTEM_PROMPT = """You are a world-class industrial-organizational psychologist specializing in US tech interviews (FAANG, startups, Big Tech).
Given the recruiter's name, company, public clues, and US software culture:
- Build a short psychological profile (communication style, what they value, likely personality)
- Note if they seem senior/junior, technical vs people-oriented
- Predict how they react to humor, conciseness, or stories
- Focus on US norms (direct, positive, growth-mindset)
Keep it 4-6 bullet points. Be professional but insightful."""


async def run(parsed_data: dict[str, Any]) -> str:
    user_prompt = (
        "Here is the structured data extracted so far:\n"
        f"{json.dumps(parsed_data, indent=2)}\n\n"
        "Profile the interviewer."
    )
    return await generate(SYSTEM_PROMPT, user_prompt, temperature=0.7)
