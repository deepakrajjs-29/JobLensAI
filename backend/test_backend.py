"""Comprehensive automated test suite for JobLens AI FastAPI Backend, Bedrock AI Analysis & Interview Coach."""
import io
import sys
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.utils.text_cleaner import clean_text, is_meaningful_text
from app.services.document_parser import parse_pdf_bytes, DocumentParsingError
from app.services.bedrock_service import (
    build_system_prompt,
    build_user_prompt,
    build_evaluation_system_prompt,
    build_evaluation_user_prompt,
    extract_json_from_response,
    analyze_with_bedrock,
    evaluate_answer_with_bedrock,
    generate_fallback_preview,
    generate_fallback_interview_evaluation,
)
from app.models.schemas import (
    AnalysisResultSchema,
    InterviewEvaluationSchema,
    InterviewEvaluateRequest,
)

client = TestClient(app)


def create_sample_pdf_bytes(text_content: str) -> bytes:
    """Helper to generate a minimal valid PDF containing text operators."""
    pdf_template = (
        f"%PDF-1.4\n"
        f"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        f"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        f"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>\nendobj\n"
        f"4 0 obj\n<< /Length {len(text_content) + 50} >>\nstream\n"
        f"BT\n/F1 12 Tf\n72 712 Td\n({text_content}) Tj\nET\n"
        f"endstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000300 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n450\n%%EOF"
    )
    return pdf_template.encode("latin-1")


# Sample valid AI analysis JSON
MOCK_BEDROCK_ANALYSIS_OUTPUT = {
    "match_score": 85,
    "match_category": "Strong Match",
    "summary": "Candidate exhibits strong experience in React and Python with minor gaps in AWS deployment.",
    "matching_skills": ["React", "Python", "REST APIs", "SQL"],
    "skill_gaps": [
        {
            "skill": "AWS Lambda",
            "priority": "high",
            "reason": "Required for serverless microservice execution."
        }
    ],
    "strengths": [
        "Proven expertise in Python backend services",
        "Experience building frontend interfaces in React"
    ],
    "weaknesses": [
        "No demonstrated hands-on experience with AWS cloud deployments"
    ],
    "important_requirements": [
        "3+ years experience with modern web frameworks",
        "Experience with cloud architectures"
    ],
    "priority_gaps": [
        {
            "skill": "AWS Lambda",
            "priority": "high",
            "reason": "Critical component of target architecture."
        }
    ],
    "learning_roadmap": [
        {
            "day": 1,
            "topic": "AWS Serverless Basics",
            "priority": "high",
            "activity": "Deploy first Lambda function using Python runtime.",
            "effort": "2-3 hours",
            "reason": "Directly targets high priority requirement."
        }
    ],
    "interview_questions": [
        {
            "category": "technical",
            "question": "How do you handle state management across complex React components?",
            "hint": "Discuss Context API, Redux/Zustand, and state colocation."
        }
    ]
}

# Sample valid AI interview evaluation JSON
MOCK_BEDROCK_EVAL_OUTPUT = {
    "overall_score": 8,
    "relevance_score": 9,
    "technical_score": 8,
    "clarity_score": 9,
    "completeness_score": 7,
    "strengths": [
        "Clearly explained component modularity and unidirectional data flow.",
        "Demonstrated familiarity with React hooks and Context API."
    ],
    "missing_points": [
        "Could mention performance profiling using React DevTools.",
        "Did not discuss asynchronous state handling with React Query or SWR."
    ],
    "improvement_tips": [
        "Frame your answer with a concrete project example where state optimization reduced re-renders.",
        "Discuss trade-offs between local state and global store solutions."
    ],
    "suggested_better_answer": "In React applications, state management depends on scope: local state via useState/useReducer, lifted state via Context for compound components, and dedicated libraries like Zustand for complex cross-cutting domain state. In my past role, adopting this taxonomy improved rendering performance by 35%.",
    "final_feedback": "Great technical clarity and structure! Bringing in quantifiable impact metrics will make this answer exemplary."
}


def test_text_cleaner():
    """Test text cleaner normalization rules."""
    print("Testing text_cleaner utility...")
    raw = "  •  React.js   \r\n\r\n\r\n\r\n  ● TypeScript   \n  ▪ Node.js  \t  \n\n\n  "
    cleaned = clean_text(raw)
    assert "- React.js" in cleaned
    assert "- TypeScript" in cleaned
    assert "- Node.js" in cleaned
    assert "\r" not in cleaned
    assert is_meaningful_text(cleaned, min_chars=10) is True
    print("  [OK] text_cleaner passed.")


def test_health_endpoint():
    """Test GET /api/health."""
    print("Testing GET /api/health...")
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "bedrock_configured" in data
    print("  [OK] GET /api/health returned 200 OK.")


def test_bedrock_prompts():
    """Test Bedrock system and user prompt creation."""
    print("Testing Bedrock analysis prompt formatting...")
    sys_prompt = build_system_prompt()
    assert "JobLens AI" in sys_prompt
    assert "EVIDENCE-BASED" in sys_prompt
    
    user_prompt = build_user_prompt("Resume Text", "JD Text")
    assert "<resume>" in user_prompt
    assert "<job_description>" in user_prompt
    print("  [OK] Bedrock analysis prompts formatted correctly.")


def test_json_extraction_from_markdown():
    """Test extracting JSON from various raw LLM output shapes."""
    print("Testing JSON extraction & markdown code fence stripping...")
    
    pure_json_str = json.dumps(MOCK_BEDROCK_ANALYSIS_OUTPUT)
    parsed = extract_json_from_response(pure_json_str)
    assert parsed["match_score"] == 85
    
    fenced_json_str = f"Here is the evaluation:\n```json\n{json.dumps(MOCK_BEDROCK_ANALYSIS_OUTPUT)}\n```\nHope this helps!"
    parsed_fenced = extract_json_from_response(fenced_json_str)
    assert parsed_fenced["match_score"] == 85
    
    try:
        extract_json_from_response("Not a JSON object at all")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
        
    print("  [OK] JSON extraction handles raw, fenced, and invalid strings.")


def test_bedrock_schema_validation():
    """Test validating parsed AI output against Pydantic schema."""
    print("Testing AnalysisResultSchema validation...")
    schema = AnalysisResultSchema(**MOCK_BEDROCK_ANALYSIS_OUTPUT)
    assert schema.match_score == 85
    assert schema.match_category == "Strong Match"
    assert len(schema.matching_skills) == 4
    print("  [OK] AnalysisResultSchema validates structure correctly.")


def test_analyze_endpoint_e2e_mocked_bedrock():
    """Test full POST /api/analyze route with mocked Bedrock."""
    print("Testing full POST /api/analyze with Bedrock...")
    
    resume_pdf_bytes = create_sample_pdf_bytes("Alex Chen - Python, React, PostgreSQL Engineer.")
    jd_text = "Looking for a Python & React Engineer with AWS Lambda experience."
    
    mock_schema = AnalysisResultSchema(**MOCK_BEDROCK_ANALYSIS_OUTPUT)
    
    with patch("app.routes.analysis.is_bedrock_configured", return_value=True), \
         patch("app.routes.analysis.analyze_with_bedrock", return_value=(mock_schema, "us.amazon.nova-2-lite-v1:0")):
        
        response = client.post(
            "/api/analyze",
            files={
                "resume": ("resume.pdf", resume_pdf_bytes, "application/pdf")
            },
            data={
                "jd_text": jd_text
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["mode"] == "bedrock_ai"
        assert data["model_id"] == "us.amazon.nova-2-lite-v1:0"
        assert data["analysis"]["match_score"] == 85
        
    print("  [OK] POST /api/analyze returned complete AI analysis JSON payload.")


# =====================================================================
# Phase 4 — Interview Coach Tests
# =====================================================================

def test_interview_evaluation_schema_validation():
    """Test InterviewEvaluationSchema validation with valid and invalid data."""
    print("Testing InterviewEvaluationSchema validation...")
    schema = InterviewEvaluationSchema(**MOCK_BEDROCK_EVAL_OUTPUT)
    assert schema.overall_score == 8
    assert schema.relevance_score == 9
    assert schema.technical_score == 8
    assert len(schema.strengths) == 2
    assert len(schema.missing_points) == 2
    assert "React" in schema.suggested_better_answer
    print("  [OK] InterviewEvaluationSchema validation passed.")


def test_interview_prompts():
    """Test Interview Coach system and user prompt formatting."""
    print("Testing Interview Coach prompt formatting...")
    sys_prompt = build_evaluation_system_prompt()
    assert "expert technical interviewer" in sys_prompt
    assert "SCORING RUBRIC" in sys_prompt
    
    user_prompt = build_evaluation_user_prompt(
        question="How do you handle state?",
        category="technical",
        answer="I use Redux and Context API.",
        job_description="React developer role",
        resume_context="3 years React experience"
    )
    assert "<interview_question" in user_prompt
    assert "<candidate_answer>" in user_prompt
    assert "<target_job_context>" in user_prompt
    print("  [OK] Interview Coach prompts formatted correctly.")


def test_interview_evaluate_endpoint_mocked():
    """Test POST /api/interview/evaluate endpoint with mocked Bedrock."""
    print("Testing POST /api/interview/evaluate with mocked Bedrock...")
    
    mock_eval_schema = InterviewEvaluationSchema(**MOCK_BEDROCK_EVAL_OUTPUT)
    
    with patch("app.routes.interview.is_bedrock_configured", return_value=True), \
         patch("app.routes.interview.evaluate_answer_with_bedrock", return_value=(mock_eval_schema, "us.amazon.nova-2-lite-v1:0")):
        
        payload = {
            "question": "How do you manage component state across large React applications?",
            "category": "technical",
            "answer": "In large React applications, I structure state by keeping local state in useState and lifting shared state into Context or Zustand stores.",
            "job_description": "Senior React Engineer position"
        }
        
        response = client.post("/api/interview/evaluate", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["success"] is True
        assert data["mode"] == "bedrock_ai"
        assert data["model_id"] == "us.amazon.nova-2-lite-v1:0"
        assert data["evaluation"]["overall_score"] == 8
        assert data["evaluation"]["relevance_score"] == 9
        assert len(data["evaluation"]["strengths"]) > 0
        assert len(data["evaluation"]["missing_points"]) > 0
        
    print("  [OK] POST /api/interview/evaluate returned complete structured evaluation.")


def test_interview_evaluate_short_answer_validation():
    """Test POST /api/interview/evaluate rejects answers shorter than 10 characters."""
    print("Testing answer length validation (< 10 chars)...")
    
    payload = {
        "question": "Explain how you design a RESTful API.",
        "category": "technical",
        "answer": "Too short"
    }
    
    response = client.post("/api/interview/evaluate", json=payload)
    assert response.status_code == 422 or response.status_code == 400
    print("  [OK] Short answer rejected with validation error.")


def test_fallback_interview_evaluation_generator():
    """Test dynamic fallback interview evaluation generator."""
    print("Testing generate_fallback_interview_evaluation...")
    
    fallback_eval = generate_fallback_interview_evaluation(
        question="How do you architect a scalable microservice?",
        category="technical",
        answer="We implemented Docker containers behind an AWS API Gateway with caching in Redis and PostgreSQL as the primary database."
    )
    assert fallback_eval.overall_score > 0
    assert fallback_eval.relevance_score > 0
    assert len(fallback_eval.strengths) > 0
    assert len(fallback_eval.improvement_tips) > 0
    assert len(fallback_eval.suggested_better_answer) > 20
    print("  [OK] generate_fallback_interview_evaluation produces rich structured feedback.")


# =====================================================================
# Phase 5A — AWS Lambda Adapter Tests
# =====================================================================

def test_mangum_lambda_handler():
    """Test AWS Lambda handler invocation with simulated API Gateway HTTP API event."""
    print("Testing AWS Lambda Mangum handler (lambda_handler.handler)...")
    from lambda_handler import handler
    
    # API Gateway HTTP API v2 event payload
    event = {
        "version": "2.0",
        "routeKey": "GET /api/health",
        "rawPath": "/api/health",
        "rawQueryString": "",
        "headers": {
            "accept": "application/json",
            "host": "test.execute-api.us-east-1.amazonaws.com"
        },
        "requestContext": {
            "http": {
                "method": "GET",
                "path": "/api/health",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "pytest"
            }
        },
        "isBase64Encoded": False
    }
    
    response = handler(event, {})
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "ok"
    assert "bedrock_configured" in body
    print("  [OK] Mangum Lambda handler processed simulated API Gateway event successfully.")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RUNNING JOBLENS AI PHASE 5A TEST SUITE (12 TESTS)")
    print("=" * 60 + "\n")
    
    try:
        test_text_cleaner()
        test_health_endpoint()
        test_bedrock_prompts()
        test_json_extraction_from_markdown()
        test_bedrock_schema_validation()
        test_analyze_endpoint_e2e_mocked_bedrock()
        test_interview_evaluation_schema_validation()
        test_interview_prompts()
        test_interview_evaluate_endpoint_mocked()
        test_interview_evaluate_short_answer_validation()
        test_fallback_interview_evaluation_generator()
        test_mangum_lambda_handler()
        
        print("\n" + "=" * 60)
        print("ALL PHASE 5A TESTS PASSED SUCCESSFULLY! (12/12)")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}", file=sys.stderr)
        sys.exit(1)
