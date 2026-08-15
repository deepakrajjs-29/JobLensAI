"""Analysis API router for document uploads, text extraction, and Amazon Bedrock AI analysis."""
import logging
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.models.schemas import AnalyzeResponse, ExtractedDocument, HealthResponse
from app.services.document_parser import DocumentParsingError, parse_pdf_bytes
from app.services.bedrock_service import (
    analyze_with_bedrock,
    generate_fallback_preview,
    is_bedrock_configured,
    get_bedrock_config,
)
from app.utils.text_cleaner import clean_text, is_meaningful_text

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Analysis"])

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Service health check endpoint."""
    return HealthResponse(
        status="ok",
        service="JobLens AI backend",
        version="0.1.0",
        bedrock_configured=is_bedrock_configured()
    )


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload Resume & Job Description for Amazon Bedrock AI Analysis"
)
async def analyze_documents(
    resume: UploadFile = File(..., description="Resume PDF file (required, max 10MB)"),
    jd_file: Optional[UploadFile] = File(None, description="Job Description PDF file (optional, max 10MB)"),
    jd_text: Optional[str] = Form(None, description="Pasted Job Description text (optional)")
):
    """
    Phase 3 AI Analysis Pipeline:
    1. Validates the Resume PDF & extracts clean text.
    2. Validates the Job Description (PDF or text) & extracts clean text.
    3. Invokes Amazon Bedrock Converse API to perform evidence-based career analysis.
    4. Validates and returns structured AI career action plan.
    """
    # -------------------------------------------------------------
    # 1. Validate and Parse Resume PDF
    # -------------------------------------------------------------
    if not resume or not resume.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A resume file is required. Please upload a PDF resume."
        )

    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid resume file '{resume.filename}'. Only PDF files (.pdf) are supported."
        )

    resume_bytes = await resume.read()
    if len(resume_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Resume file '{resume.filename}' exceeds the maximum allowed size of 10 MB."
        )

    try:
        resume_cleaned_text, resume_pages = parse_pdf_bytes(
            resume_bytes,
            filename=resume.filename
        )
    except DocumentParsingError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{e.message} {e.detail}".strip()
        )

    # -------------------------------------------------------------
    # 2. Validate and Parse Job Description (PDF or Text)
    # -------------------------------------------------------------
    jd_cleaned_text: str = ""
    jd_filename: Optional[str] = None
    jd_source: str = "text"
    jd_pages: Optional[int] = None

    # Case A: JD uploaded as PDF
    if jd_file and jd_file.filename and jd_file.filename.strip():
        if not jd_file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid job description file '{jd_file.filename}'. Only PDF files are supported."
            )

        jd_bytes = await jd_file.read()
        if len(jd_bytes) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Job description file '{jd_file.filename}' exceeds the maximum allowed size of 10 MB."
            )

        try:
            jd_cleaned_text, jd_pages = parse_pdf_bytes(
                jd_bytes,
                filename=jd_file.filename
            )
            jd_filename = jd_file.filename
            jd_source = "pdf"
        except DocumentParsingError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{e.message} {e.detail}".strip()
            )

    # Case B: JD provided as pasted text
    elif jd_text and jd_text.strip():
        jd_cleaned_text = clean_text(jd_text)
        if not is_meaningful_text(jd_cleaned_text, min_chars=30):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The provided job description text is too short or empty. Please provide a detailed job description."
            )
        jd_source = "text"

    # Neither was provided
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A job description is required. Please either upload a PDF or paste the job description text."
        )

    # -------------------------------------------------------------
    # 3. Amazon Bedrock AI Analysis
    # -------------------------------------------------------------
    mode = "bedrock_ai"
    model_used: Optional[str] = None

    if is_bedrock_configured():
        try:
            analysis_result, model_used = analyze_with_bedrock(
                resume_text=resume_cleaned_text,
                jd_text=jd_cleaned_text
            )
        except Exception as e:
            logger.warning(f"Bedrock invocation failed ({e}). Falling back to structured preview mode.")
            analysis_result = generate_fallback_preview(
                resume_text=resume_cleaned_text,
                jd_text=jd_cleaned_text
            )
            mode = "mock_preview"
            model_used = None
    else:
        logger.info("AWS credentials not detected. Generating structured preview analysis.")
        analysis_result = generate_fallback_preview(
            resume_text=resume_cleaned_text,
            jd_text=jd_cleaned_text
        )
        mode = "mock_preview"
        _, default_model = get_bedrock_config()
        model_used = f"{default_model} (Preview)"

    # -------------------------------------------------------------
    # 4. Construct Response
    # -------------------------------------------------------------
    resume_extracted_doc = ExtractedDocument(
        filename=resume.filename,
        source="pdf",
        page_count=resume_pages,
        text_length=len(resume_cleaned_text),
        text=None  # Do not return heavy raw text unnecessarily
    )

    jd_extracted_doc = ExtractedDocument(
        filename=jd_filename,
        source=jd_source,  # type: ignore
        page_count=jd_pages,
        text_length=len(jd_cleaned_text),
        text=None
    )

    return AnalyzeResponse(
        success=True,
        message="AI career fit analysis completed successfully.",
        mode=mode,
        model_id=model_used,
        resume=resume_extracted_doc,
        job_description=jd_extracted_doc,
        analysis=analysis_result
    )
