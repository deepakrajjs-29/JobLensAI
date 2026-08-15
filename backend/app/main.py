"""JobLens AI FastAPI Application Entrypoint."""
import os
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes.analysis import router as analysis_router
from app.routes.interview import router as interview_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("joblens.backend")

# Initialize FastAPI application
app = FastAPI(
    title="JobLens AI Backend",
    description="Backend API for document ingestion, PDF text extraction, and career intelligence analysis.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS origins
env_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").strip()

if env_origins == "*":
    allow_origins = ["*"]
    allow_credentials = False
else:
    allow_origins = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Fallback handler to ensure the API always returns structured JSON errors instead of HTML stack traces."""
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "An unexpected server error occurred while processing your request.",
            "detail": str(exc) if os.getenv("ENVIRONMENT") == "development" else None
        }
    )


# Include API routes under /api
app.include_router(analysis_router, prefix="/api")
app.include_router(interview_router, prefix="/api/interview")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint providing service metadata."""
    return {
        "service": "JobLens AI Backend",
        "version": "0.1.0",
        "status": "running",
        "health": "/api/health",
        "docs": "/docs"
    }
