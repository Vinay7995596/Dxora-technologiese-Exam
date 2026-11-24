from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.schemas import LinkAnalysisRequest, LinkAnalysisResponse
from app.services.analysis_service import run_link_analysis

app = FastAPI(
    title=settings.app_name,
    description="Analyze a public website and generate AI-powered business, competitor, SEO, service, and audience insights.",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {
        "message": "AI Website Link Analysis API is running.",
        "docs": "/docs",
        "endpoint": "POST /link-analysis",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/link-analysis", response_model=LinkAnalysisResponse)
async def link_analysis(payload: LinkAnalysisRequest):
    try:
        return await run_link_analysis(str(payload.url))
    except HTTPException:
        raise
    except Exception:
        # Do not expose secrets, stack traces, or provider internals to clients.
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred while analyzing the website."},
        )
