# JobLens AI 🔍

> **Know your fit. Find your gaps. Get interview-ready.**

JobLens AI is an AI-powered career assistant built for the **AWS Weekend Creative Challenge**. It compares a job seeker's resume with a target job description and generates a personalized action plan with match scoring, skill gap priorities, a 5-day preparation roadmap, and **an interactive AI Interview Coach** powered by **Amazon Bedrock** (Amazon Nova 2 Lite: `us.amazon.nova-2-lite-v1:0`).

---

## 🏗️ Architecture

```text
                            USER (Browser)
                                  │
                                  ▼
                   ┌─────────────────────────────┐
                   │    React + Vite Frontend    │
                   │    TypeScript + Modern CSS   │
                   └──────────────┬──────────────┘
                                  │
                                  ▼ (HTTP / Multipart / JSON)
                   ┌─────────────────────────────┐
                   │    FastAPI Python Backend   │
                   │    In-Memory pypdf Parser   │
                   └──────────────┬──────────────┘
                                  │
                                  ▼ (Boto3 Converse API)
                   ┌─────────────────────────────┐
                   │       Amazon Bedrock        │
                   │  us.amazon.nova-2-lite-v1:0 │
                   └─────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Node.js** (v18+) & **npm**
- **Python** (v3.10+)
- **AWS Account** with Amazon Bedrock access (Amazon Nova 2 Lite)

---

### 2. Start the FastAPI Backend

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Backend runs at: **`http://localhost:8000`** (Swagger docs at `/docs`)

---

### 3. Start the React Frontend

In a new terminal:

```powershell
cd frontend
npm install
npm run dev
```
Frontend runs at: **`http://localhost:5173`**

---

## 🧪 Development Phases

- [x] **Phase 1 — Foundation + UI**: React + Vite + TypeScript frontend, glassmorphism design system, drag & drop uploads, mock results dashboard, responsive layout.
- [x] **Phase 2 — Document Processing + Backend**: FastAPI backend, in-memory PDF extraction with `pypdf`, text cleaner, input validation, structured JSON responses, live frontend integration.
- [x] **Phase 3 — Amazon Bedrock AI Analysis**: Bedrock Converse API integration via Boto3, `us.amazon.nova-2-lite-v1:0` in `us-east-1`, evidence-based system prompt engineering, Pydantic schema validation, live end-to-end inference in UI.
- [x] **Phase 4 — Career Intelligence + AI Interview Coach**: Interactive real-time interview simulator, 4-bar metric scoring rubric (0-10), strengths, missing points, actionable tips, exemplary model answers, and completion summary.
- [ ] **Phase 5 — AWS Deployment + Submission**: AWS Lambda, Amplify, S3, Builder Center article.

---

## 🔒 Security & Privacy

- Documents are processed exclusively in memory and **never saved permanently to disk**.
- No AWS credentials or secrets are stored in client-side code.
- Strict 10MB upload limits and input sanitization.
- Safe AWS CLI login credential provider chain.

---

## 🏆 Hackathon Submission

- **Challenge**: AWS Weekend Creative Challenge
- **Tag**: `#creative-expression`
- **Article Title**: *Weekend Creative Challenge: JobLens AI*
