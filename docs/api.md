# JobLens AI — API Reference

The JobLens AI backend exposes three primary REST endpoints for health monitoring, document analysis, and interactive interview coaching.

---

## 1. Health Check Endpoint

### `GET /api/health`

Verifies that the backend service is operational and checks if Amazon Bedrock credentials and region are detected.

#### Request
```http
GET /api/health HTTP/1.1
Host: f31wzguidd.execute-api.us-east-1.amazonaws.com
Accept: application/json
```

#### Response (200 OK)
```json
{
  "status": "ok",
  "service": "JobLens AI backend",
  "version": "0.1.0",
  "bedrock_configured": true
}
```

---

## 2. Document Extraction & Career Analysis Endpoint

### `POST /api/analyze`

Accepts a candidate's resume PDF and a target job description (as a PDF file or text string). Extracts and cleans document text in memory, invokes Amazon Bedrock Nova 2 Lite, and returns a structured career action plan.

#### Request Headers
```http
Content-Type: multipart/form-data
```

#### Form Data Parameters
| Parameter | Type | Required | Description |
|---|---|---|---|
| `resume` | `File` (PDF) | Yes | Candidate resume in PDF format (max 10MB) |
| `jd_file` | `File` (PDF) | No* | Target job description PDF (max 10MB) |
| `jd_text` | `string` | No* | Target job description text (min 30 characters) |

*\* Either `jd_file` or `jd_text` must be provided.*

#### Response (200 OK)
```json
{
  "success": true,
  "message": "Analysis completed successfully.",
  "mode": "bedrock_ai",
  "model_id": "us.amazon.nova-2-lite-v1:0",
  "resume": {
    "filename": "alex_chen_resume.pdf",
    "source": "pdf",
    "page_count": 1,
    "text_length": 1420
  },
  "job_description": {
    "filename": null,
    "source": "text",
    "page_count": null,
    "text_length": 1280
  },
  "analysis": {
    "match_score": 85,
    "match_category": "Strong Match",
    "summary": "Alex Chen demonstrates strong alignment with the Senior Full-Stack Engineer role...",
    "matching_skills": [
      "React",
      "TypeScript",
      "Node.js",
      "PostgreSQL",
      "REST APIs"
    ],
    "skill_gaps": [
      {
        "skill": "AWS Cloud Architecture (Lambda, S3, API Gateway)",
        "priority": "high",
        "reason": "Core requirement for building serverless backend microservices."
      },
      {
        "skill": "Docker Containerization",
        "priority": "medium",
        "reason": "Required for automated deployment pipelines."
      }
    ],
    "strengths": [
      "Proven frontend proficiency with React and TypeScript",
      "Solid database modeling experience with PostgreSQL"
    ],
    "weaknesses": [
      "No direct evidence of AWS cloud service deployments in resume"
    ],
    "important_requirements": [
      "3+ years professional full-stack development experience",
      "Hands-on experience with AWS cloud services",
      "Understanding of Docker and CI/CD pipelines"
    ],
    "priority_gaps": [
      {
        "skill": "AWS Cloud Architecture",
        "priority": "high",
        "reason": "Address first to satisfy core infrastructure requirements."
      }
    ],
    "learning_roadmap": [
      {
        "day": 1,
        "topic": "AWS Serverless Fundamentals",
        "priority": "high",
        "activity": "Deploy a Lambda function behind API Gateway using Boto3.",
        "effort": "3 hours",
        "reason": "Directly targets high priority requirement."
      },
      {
        "day": 2,
        "topic": "Docker Containerization",
        "priority": "medium",
        "activity": "Create a multi-stage Dockerfile for a FastAPI service.",
        "effort": "2 hours",
        "reason": "Prepares for container deployment discussions."
      }
    ],
    "interview_questions": [
      {
        "category": "technical",
        "question": "How would you architect a serverless API with FastAPI and AWS Lambda?",
        "hint": "Discuss ASGI adapters like Mangum, cold start mitigation, and API Gateway payload versions."
      },
      {
        "category": "behavioral",
        "question": "Describe a time when you received constructive feedback on your code architecture.",
        "hint": "Use the STAR method: Situation, Task, Action, and measurable Result."
      }
    ]
  }
}
```

---

## 3. AI Answer Evaluation Endpoint

### `POST /api/interview/evaluate`

Evaluates a candidate's answer to an interview question across four rubric dimensions (Relevance, Technical Depth, Clarity, Completeness) on a 0–10 scale using Amazon Bedrock Nova 2 Lite.

#### Request Headers
```http
Content-Type: application/json
```

#### Request Body
```json
{
  "question": "How do you manage state across large React applications?",
  "category": "technical",
  "answer": "In large React applications, I structure state by keeping local state in useState, compound component state in React Context, and shared cross-cutting application state in Zustand stores to prevent unnecessary re-renders.",
  "job_description": "Senior Full-Stack Engineer position"
}
```

#### Response (200 OK)
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
      "Correctly distinguishes between local component state and global store state.",
      "Clear explanation of state scoping principles to minimize re-renders."
    ],
    "missing_points": [
      "Could mention server state caching tools like React Query or SWR.",
      "Did not mention profiling tools such as React DevTools Profiler."
    ],
    "improvement_tips": [
      "Include a brief real-world project example showing measurable performance gains.",
      "Mention asynchronous data synchronization strategies."
    ],
    "suggested_better_answer": "In React applications, state management depends on scope: local state via useState/useReducer, lifted state via Context for compound components, and dedicated libraries like Zustand for complex cross-cutting domain state. In my past role, adopting this taxonomy improved rendering performance by 35%.",
    "final_feedback": "Great technical clarity and structure! Bringing in quantifiable impact metrics will make this answer exemplary."
  }
}
```

---

## 4. Error Responses

All error responses adhere to standard HTTP status codes and return structured JSON error envelopes:

```json
{
  "success": false,
  "error": "Validation Error",
  "detail": "Please provide a little more detail before submitting your answer (minimum 10 characters)."
}
```

| HTTP Status | Meaning | Scenario |
|---|---|---|
| `400 Bad Request` | Client validation failure | Short answer (<10 chars), missing required fields |
| `422 Unprocessable Entity` | Schema validation error | Invalid JSON types or missing parameters |
| `500 Internal Server Error` | Server execution failure | Unexpected runtime exception |
