"""FastAPI entry point for PsychFlow AI.

Run with:
    uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import RateLimitError

load_dotenv()  # picks up backend/.env

from psychflow.llm import _parse_retry_after  # noqa: E402
from psychflow.pipeline import run_pipeline  # noqa: E402
from psychflow.schemas import AnalyzeRequest, AnalyzeResponse  # noqa: E402

app = FastAPI(
    title="PsychFlow AI",
    description="6-agent interview prep pipeline powered by Groq.",
    version="0.1.0",
)

allowed_origin = os.environ.get("ALLOWED_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    try:
        result = await run_pipeline(
            recruiter_message=req.recruiter_message,
            job_description=req.job_description,
            resume=req.resume,
        )
    except RuntimeError as exc:
        # Missing API key etc.
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except RateLimitError as exc:
        # All retries exhausted - tell the client clearly so it can show
        # a friendly message (and so the user knows to switch models).
        wait = _parse_retry_after(exc)
        wait_hint = f"~{int(wait + 1)}s" if wait else "a minute"
        raise HTTPException(
            status_code=429,
            detail=(
                "Groq free-tier rate limit hit even after retries. "
                f"Wait {wait_hint} and try again, or switch to a smaller "
                "model like 'llama-3.3-70b-versatile' in backend/.env."
            ),
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"pipeline error: {exc}") from exc

    return AnalyzeResponse(**result)
