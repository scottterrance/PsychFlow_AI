"""FastAPI entry point for PsychFlow AI.

Run with:
    uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()  # picks up backend/.env

from psychflow.pipeline import run_pipeline  # noqa: E402
from psychflow.schemas import AnalyzeRequest, AnalyzeResponse  # noqa: E402

app = FastAPI(
    title="PsychFlow AI",
    description="6-agent interview prep pipeline powered by Gemini.",
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
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"pipeline error: {exc}") from exc

    return AnalyzeResponse(**result)
