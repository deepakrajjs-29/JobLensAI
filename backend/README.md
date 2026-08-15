# JobLens AI — Backend Service

Lightweight, high-performance Python **FastAPI** backend with **Amazon Bedrock AI** integration for document ingestion, PDF text extraction, evidence-based career intelligence, preparation roadmaps, and **interactive AI interview coaching**.

---

## 🎯 Architecture Overview

```text
Uploaded Resume (PDF) + Job Description (PDF/Text)
                    │
                    ▼
          FastAPI Router (/api/analyze)
                    │
                    ▼
       In-Memory Parser (pypdf)
       - Page-by-page extraction
       - Zero disk persistence
                    │
                    ▼
         Text Cleaning Pipeline
       - Whitespace normalization
       - Markdown bullet standardization
       - Line break consolidation
                    │
                    ▼
       Amazon Bedrock Converse API
       (US Amazon Nova 2 Lite: us.amazon.nova-2-lite-v1:0)
       - Evidence-based prompt engineering
       - Zero protected characteristic bias
       - Structured JSON schema enforcement
                    │
                    ▼
          Structured JSON Response
          (Score, Gaps, Roadmap, Questions)
                    │
                    ▼
      Interactive AI Interview Coach
         (/api/interview/evaluate)
       - 4-Bar Metric Rubric (0-10)
       - Strengths & Missing Points
       - Actionable Improvement Tips
       - Exemplary Model Answers
```

---

## 🛠️ Tech Stack

- **Python 3.10+ / 3.14**
- **FastAPI**: Modern, asynchronous web framework for building APIs.
- **Uvicorn**: Lightning-fast ASGI web server.
- **Amazon Bedrock**: AWS foundation model service using the unified **Converse API** and **Amazon Nova 2 Lite** (`us.amazon.nova-2-lite-v1:0`).
- **Boto3 & botocore[crt]**: Official AWS SDK with AWS CLI login credential provider.
- **pypdf**: Pure-Python PDF extraction library operating entirely in memory.
- **Pydantic v2**: Data validation and type safety.

---

## 🚀 Getting Started

### 1. Create and Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure AWS Environment Variables

Create or update your `.env` file (based on `.env.example`):

```bash
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.amazon.nova-2-lite-v1:0
```

### 4. Run the Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at: **`http://localhost:8000`**
Interactive Swagger Documentation: **`http://localhost:8000/docs`**

---

## 📡 API Endpoints

### 1. `GET /api/health`
Check if backend service is running and if Bedrock credentials are detected.

---

### 2. `POST /api/analyze`
Upload a resume PDF and a job description for validation, text extraction, and Amazon Bedrock AI career analysis.

---

### 3. `POST /api/interview/evaluate`
Submit a candidate's answer to an interview question for live AI evaluation across 4 rubric dimensions.

**Request Payload (JSON):**
```json
{
  "question": "How do you design a RESTful API?",
  "category": "technical",
  "answer": "I design RESTful APIs by identifying domain resources, using standard HTTP verbs, returning proper status codes, and structuring JSON responses.",
  "job_description": "Senior Full-Stack Engineer role"
}
```

**Response Payload (JSON):**
```json
{
  "success": true,
  "message": "Interview answer evaluated successfully.",
  "mode": "bedrock_ai",
  "model_id": "us.amazon.nova-2-lite-v1:0",
  "evaluation": {
    "overall_score": 8,
    "relevance_score": 9,
    "technical_score": 8,
    "clarity_score": 9,
    "completeness_score": 7,
    "strengths": [
      "Candidate correctly identifies core RESTful principles and status codes."
    ],
    "missing_points": [
      "No mention of authentication/authorization mechanisms (OAuth2/JWT)."
    ],
    "improvement_tips": [
      "Expand on security patterns and pagination strategies."
    ],
    "suggested_better_answer": "To design a scalable RESTful API, identify domain resources with nouns in URIs...",
    "final_feedback": "Solid answer! Adding security patterns and pagination will elevate this to senior level."
  }
}
```

---

## 🧪 Running Automated Tests

Run the full automated test suite (11 tests) without incurring live AWS charges:

```powershell
.\.venv\Scripts\python.exe test_backend.py
```

Tests verify:
- Text cleaner normalization rules
- Health check endpoint
- Bedrock analysis prompt building & JSON extraction
- AnalysisResultSchema & InterviewEvaluationSchema validation
- Mocked Bedrock analysis & evaluation endpoints
- Short/empty answer validation
- Dynamic fallback evaluators

---

## 🔒 Security & Privacy

1. **Zero Permanent Storage**: Uploaded files are processed in memory and discarded immediately.
2. **Standard AWS Credential Chain**: Credentials are never hardcoded and are loaded securely from the AWS CLI login provider.
3. **Evidence-Based & Unbiased**: System prompts strictly forbid discrimination based on protected characteristics.
