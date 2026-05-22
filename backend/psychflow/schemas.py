"""Request and response schemas for the API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    recruiter_message: str = Field(
        ...,
        description="Raw text of the recruiter's email or LinkedIn message.",
        min_length=1,
    )
    job_description: str = Field(
        ...,
        description="Full job description text.",
        min_length=1,
    )
    resume: str = Field(
        ...,
        description="Candidate's resume as plain text.",
        min_length=1,
    )


class AnalyzeResponse(BaseModel):
    parsed_data: dict
    psychology_profile: str
    company_analysis: str
    predicted_questions: str
    crafted_answers: str
    airflow_strategy: str
    markdown_report: str
