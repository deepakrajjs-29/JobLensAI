"""Interview Coach API router for real-time answer evaluation."""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    InterviewEvaluateRequest,
    InterviewEvaluateResponse,
)
from app.services.bedrock_service import (
    evaluate_answer_with_bedrock,
    generate_fallback_interview_evaluation,
    is_bedrock_configured,
    get_bedrock_config,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Interview Coach"])


@router.post(
    "/evaluate",
    response_model=InterviewEvaluateResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Candidate Interview Answer with Amazon Bedrock AI"
)
async def evaluate_interview_answer(request: InterviewEvaluateRequest):
    """
    Evaluates a candidate's answer to an interview question:
    1. Validates minimum response content.
    2. Invokes Amazon Bedrock Converse API with Nova 2 Lite to evaluate the answer across 4 rubric dimensions.
    3. Returns structured feedback: overall score (0-10), sub-scores, strengths, missing points, improvement tips, and a suggested model answer.
    """
    # Validation
    cleaned_answer = request.answer.strip()
    if len(cleaned_answer) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a little more detail before submitting your answer (minimum 10 characters)."
        )

    mode = "bedrock_ai"
    model_used: Optional[str] = None

    if is_bedrock_configured():
        try:
            evaluation, model_used = evaluate_answer_with_bedrock(request)
        except Exception as e:
            logger.warning(f"Bedrock answer evaluation failed ({e}). Falling back to preview evaluation.")
            evaluation = generate_fallback_interview_evaluation(
                question=request.question,
                category=request.category,
                answer=cleaned_answer
            )
            mode = "mock_preview"
            model_used = None
    else:
        logger.info("AWS credentials not configured. Generating preview interview evaluation.")
        evaluation = generate_fallback_interview_evaluation(
            question=request.question,
            category=request.category,
            answer=cleaned_answer
        )
        mode = "mock_preview"
        _, default_model = get_bedrock_config()
        model_used = f"{default_model} (Preview)"

    return InterviewEvaluateResponse(
        success=True,
        message="Interview answer evaluated successfully.",
        mode=mode,
        model_id=model_used,
        evaluation=evaluation
    )
