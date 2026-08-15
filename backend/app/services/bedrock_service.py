"""Amazon Bedrock AI career intelligence analysis service using Boto3 Converse API."""
import os
import re
import json
import logging
from typing import Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError

from app.models.schemas import (
    AnalysisResultSchema,
    SkillGapSchema,
    RoadmapItemSchema,
    InterviewQuestionSchema,
    InterviewEvaluationSchema,
    InterviewEvaluateRequest,
)

# Load environment variables from backend/.env or current directory
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)
else:
    load_dotenv()

logger = logging.getLogger(__name__)

# Default model ID: Amazon Nova Lite is fast, cost-effective, and highly capable for text analysis
DEFAULT_MODEL_ID = "amazon.nova-lite-v1:0"
DEFAULT_REGION = "us-east-1"


def get_bedrock_config() -> Tuple[str, str]:
    """Retrieve the configured AWS Region and Bedrock Model ID."""
    region = os.getenv("AWS_REGION", DEFAULT_REGION).strip()
    model_id = os.getenv("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID).strip()
    return region, model_id


def is_bedrock_configured() -> bool:
    """Check whether AWS credentials and region are configured."""
    try:
        session = boto3.Session(region_name=os.getenv("AWS_REGION", DEFAULT_REGION))
        credentials = session.get_credentials()
        return credentials is not None
    except Exception:
        return False


def get_bedrock_client():
    """
    Initialize a Bedrock Runtime client using standard AWS credential provider chain.
    Configured with sensible timeouts and retry settings.
    """
    region, _ = get_bedrock_config()

    retry_config = Config(
        region_name=region,
        retries={
            "max_attempts": 3,
            "mode": "standard"
        },
        connect_timeout=10,
        read_timeout=60,
    )

    # If explicit credentials exist in environment, boto3 picks them up automatically.
    # Otherwise, it falls back to standard ~/.aws/credentials or IAM role.
    return boto3.client("bedrock-runtime", config=retry_config)


def build_system_prompt() -> str:
    """Construct the system prompt for Amazon Bedrock."""
    return """You are JobLens AI, an objective, expert career intelligence assistant and technical recruiter.
Your purpose is to analyze a candidate's resume against a specific target job description to evaluate fit, identify verified strengths, surface skill gaps, construct an actionable day-by-day preparation roadmap, and generate curated interview questions.

CRITICAL RULES:
1. EVIDENCE-BASED ANALYSIS:
   - Base your evaluation strictly on the text provided in the resume and job description.
   - If a requirement is not demonstrated in the resume, treat it as "not demonstrated in the provided resume", NOT as an absolute certainty that the candidate lacks the skill.
   - Never invent or fabricate qualifications, past roles, or experience.
2. OBJECTIVITY & NON-DISCRIMINATION:
   - Base evaluation solely on technical requirements, relevant experience, projects, skills, and qualifications.
   - NEVER use, evaluate, or penalize protected characteristics such as age, gender, race, ethnicity, religion, disability, or nationality. Ignore any such details if they appear.
3. OUTPUT FORMAT:
   - You MUST output ONLY a single, valid JSON object matching the exact schema specified below.
   - Do NOT include conversational greetings, preamble, markdown commentary outside the JSON, or closing remarks.
   - Ensure the JSON is completely parseable by standard JSON decoders.

JSON SCHEMA:
{
  "match_score": <integer from 0 to 100, representing estimated fit>,
  "match_category": "<'Excellent Match' (90-100) | 'Strong Match' (75-89) | 'Moderate Match' (60-74) | 'Needs Improvement' (0-59)>",
  "summary": "<2-4 sentences summarizing candidate fit, primary alignments, and key focus areas>",
  "matching_skills": ["<skill1>", "<skill2>", ...],
  "skill_gaps": [
    {
      "skill": "<name of required skill/concept missing or weak>",
      "priority": "<'high' | 'medium' | 'low'>",
      "reason": "<clear explanation of why this is important for the role and what is missing in the resume>"
    }
  ],
  "strengths": [
    "<specific verified strength demonstrating alignment with job requirements>"
  ],
  "weaknesses": [
    "<area where the resume provides insufficient evidence for the job requirements>"
  ],
  "important_requirements": [
    "<key requirement or responsibility extracted from the job description>"
  ],
  "priority_gaps": [
    {
      "skill": "<highest priority skill to address first>",
      "priority": "<'high' | 'medium'>",
      "reason": "<why this should be tackled immediately>"
    }
  ],
  "learning_roadmap": [
    {
      "day": 1,
      "topic": "<focus topic>",
      "priority": "<'high' | 'medium' | 'low'>",
      "activity": "<concrete actionable study task, mini-project, or tutorial to build this skill>",
      "effort": "<estimated time, e.g., '2-3 hours'>",
      "reason": "<why this activity addresses the primary gap>"
    }
  ],
  "interview_questions": [
    {
      "category": "<'technical' | 'resume' | 'behavioral' | 'job-specific'>",
      "question": "<realistic, insightful interview question>",
      "hint": "<guidance or answering framework, e.g. STAR method or key technical points to cover>"
    }
  ]
}"""


def build_user_prompt(resume_text: str, jd_text: str) -> str:
    """Construct the user prompt containing the cleaned documents."""
    return f"""Please perform an in-depth career fit analysis for the following candidate and job description:

<resume>
{resume_text}
</resume>

<job_description>
{jd_text}
</job_description>

Remember: Output ONLY the requested JSON object conforming to the schema. Do not wrap in commentary."""


def extract_json_from_response(raw_text: str) -> dict:
    """
    Safely extract and parse JSON from the model's text output,
    handling markdown code blocks and surrounding whitespace.
    """
    text = raw_text.strip()

    # 1. Remove markdown code fences if present (```json ... ``` or ``` ... ```)
    if "```" in text:
        # Match ```json ... ``` or ``` ... ```
        pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            text = match.group(1).strip()

    # 2. Extract outermost JSON object if additional text surrounds it
    json_match = re.search(r"\{[\s\S]*\}", text)
    if json_match:
        text = json_match.group(0)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse model JSON: {e}\nRaw text was:\n{raw_text[:500]}...")
        raise ValueError(f"Model response was not valid JSON: {str(e)}")


def analyze_with_bedrock(resume_text: str, jd_text: str) -> Tuple[AnalysisResultSchema, str]:
    """
    Invoke Amazon Bedrock Converse API to perform career analysis.
    
    Returns:
        Tuple[AnalysisResultSchema, str]: (Parsed and validated analysis schema, Model ID used)
    """
    region, model_id = get_bedrock_config()
    client = get_bedrock_client()

    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(resume_text, jd_text)

    logger.info(f"Invoking Amazon Bedrock Converse API with model: '{model_id}' in region: '{region}'")

    try:
        response = client.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"text": user_prompt}
                    ]
                }
            ],
            system=[
                {"text": system_prompt}
            ],
            inferenceConfig={
                "temperature": 0.2,
                "maxTokens": 4096,
                "topP": 0.9
            }
        )

        # Extract text content from Converse API response
        output_message = response.get("output", {}).get("message", {})
        content_list = output_message.get("content", [])
        if not content_list or "text" not in content_list[0]:
            raise ValueError("Bedrock Converse response did not contain expected text content.")

        raw_output_text = content_list[0]["text"]
        parsed_json = extract_json_from_response(raw_output_text)

        # Validate with Pydantic schema
        validated_schema = AnalysisResultSchema(**parsed_json)
        return validated_schema, model_id

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_msg = e.response.get("Error", {}).get("Message", str(e))
        logger.error(f"AWS Bedrock ClientError [{error_code}]: {error_msg}")
        raise e
    except (NoCredentialsError, EndpointConnectionError) as e:
        logger.error(f"AWS Credential / Connection Error: {e}")
        raise e


def generate_fallback_preview(resume_text: str, jd_text: str) -> AnalysisResultSchema:
    """
    Generates a realistic, dynamic fallback analysis when Bedrock credentials are not yet configured.
    Used for local evaluation and testing before AWS keys are added.
    """
    # Identify basic matching keywords dynamically
    common_skills = [
        "React", "TypeScript", "JavaScript", "Python", "FastAPI", "Node.js",
        "AWS", "Docker", "PostgreSQL", "SQL", "Git", "REST APIs", "GraphQL", "CI/CD"
    ]
    
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()

    matching = [s for s in common_skills if s.lower() in resume_lower and s.lower() in jd_lower]
    gaps = [s for s in common_skills if s.lower() in jd_lower and s.lower() not in resume_lower]

    if not matching:
        matching = ["REST APIs", "Git & GitHub", "Problem Solving"]
    if not gaps:
        gaps = ["AWS Cloud Infrastructure", "Docker Containerization", "Automated CI/CD"]

    skill_gaps_list = [
        SkillGapSchema(
            skill=gap,
            priority="high" if i == 0 else "medium",
            reason=f"Required by the job description but not explicitly evidenced in the submitted resume."
        )
        for i, gap in enumerate(gaps[:4])
    ]

    score = max(50, min(95, int(60 + (len(matching) * 6) - (len(gaps) * 4))))
    category = (
        "Excellent Match" if score >= 90
        else "Strong Match" if score >= 75
        else "Moderate Match" if score >= 60
        else "Needs Improvement"
    )

    return AnalysisResultSchema(
        match_score=score,
        match_category=category,
        summary=(
            f"Candidate demonstrates alignment with {len(matching)} key requirements including {', '.join(matching[:3])}. "
            f"Addressing gaps in {', '.join(gaps[:2])} will substantially strengthen candidacy for this role."
        ),
        matching_skills=matching,
        skill_gaps=skill_gaps_list,
        strengths=[
            f"Demonstrated experience with {matching[0]}" if matching else "Solid foundational software engineering skillset",
            "Clear understanding of modern development best practices and collaborative workflows",
            "Strong alignment with key job responsibilities outlined in the job description"
        ],
        weaknesses=[
            f"Limited evidence of {gaps[0]} in recent projects" if gaps else "Resume could benefit from more quantified impact metrics",
            "Cloud deployment experience could be highlighted more prominently"
        ],
        important_requirements=[
            "Hands-on full-stack development experience",
            "Proficiency in core modern web technologies",
            "Familiarity with cloud and deployment pipelines",
            "Strong communication and cross-functional team collaboration"
        ],
        priority_gaps=skill_gaps_list[:2],
        learning_roadmap=[
            RoadmapItemSchema(
                day=1,
                topic=gaps[0] if gaps else "Cloud Fundamentals",
                priority="high",
                activity=f"Review official documentation and complete a hands-on tutorial for {gaps[0] if gaps else 'Cloud Architecture'}.",
                effort="3 hours",
                reason=f"Addresses the most critical priority gap required for this role."
            ),
            RoadmapItemSchema(
                day=2,
                topic="Architecture & Design",
                priority="high",
                activity="Build a small end-to-end prototype integrating frontend and backend components.",
                effort="3-4 hours",
                reason="Demonstrates practical applied knowledge in interview discussions."
            ),
            RoadmapItemSchema(
                day=3,
                topic="Automated CI/CD & Testing",
                priority="medium",
                activity="Set up unit tests and GitHub Actions workflow for automated test execution.",
                effort="2 hours",
                reason="Reinforces code quality standards expected for this role."
            ),
            RoadmapItemSchema(
                day=4,
                topic="Deep Dive & Edge Cases",
                priority="medium",
                activity="Practice answering system design questions related to scalability and reliability.",
                effort="2-3 hours",
                reason="Prepares for technical round deep dives."
            ),
            RoadmapItemSchema(
                day=5,
                topic="Mock Interview & Resume Polish",
                priority="high",
                activity="Rehearse behavioral STAR stories and update resume project bullet points.",
                effort="2 hours",
                reason="Consolidates preparation for the final interview loop."
            )
        ],
        interview_questions=[
            InterviewQuestionSchema(
                category="technical",
                question=f"Can you explain how you would architect a scalable system using {matching[0] if matching else 'modern web frameworks'}?",
                hint="Focus on modularity, error boundaries, state management, and latency."
            ),
            InterviewQuestionSchema(
                category="technical",
                question=f"How would you approach learning and implementing {gaps[0] if gaps else 'cloud deployment'} in a production environment?",
                hint="Describe your learning methodology, starting from docs to sandbox environments and progressive rollouts."
            ),
            InterviewQuestionSchema(
                category="resume",
                question="Walk me through the most technically challenging problem you solved in your past project.",
                hint="Use the STAR method: Situation, Task, Action, and measurable Result."
            ),
            InterviewQuestionSchema(
                category="behavioral",
                question="Tell me about a time when you received constructive feedback on your code or design. How did you adapt?",
                hint="Demonstrate a growth mindset, humility, and willingness to collaborate."
            ),
            InterviewQuestionSchema(
                category="job-specific",
                question="What steps would you take in your first 30 days to onboard and deliver value in this role?",
                hint="Highlight codebase exploration, team alignment, tooling familiarization, and small quick wins."
            )
        ]
    )


# =====================================================================
# Phase 4 — AI Interview Coach Evaluation Logic
# =====================================================================

def build_evaluation_system_prompt() -> str:
    """Construct the system prompt for evaluating candidate interview answers."""
    return """You are JobLens AI, an expert technical interviewer and executive career coach.
Your job is to objectively evaluate a candidate's answer to an interview question for a target job role.

CRITICAL RULES:
1. EVIDENCE-BASED EVALUATION:
   - Evaluate only what the candidate actually wrote in their answer.
   - Distinguish between points explicitly demonstrated vs. points omitted or unclear.
   - Do NOT invent or assume skills or experience that are not mentioned.
2. OBJECTIVITY & NON-DISCRIMINATION:
   - Base all scores and feedback purely on technical accuracy, relevance to the question, structure, clarity, and depth.
   - NEVER consider or penalize protected characteristics (gender, age, race, nationality, religion, disability).
3. SCORING RUBRIC (0 to 10 Scale):
   - overall_score: Weighted composite score (0-10) reflecting readiness for this question.
   - relevance_score: Directness in addressing the prompt without wandering (0-10).
   - technical_score: Depth, architectural understanding, and precision (0-10).
   - clarity_score: Structure (e.g. STAR method for behavioral, modular flow for technical), conciseness, readability (0-10).
   - completeness_score: Thoroughness in covering key tradeoffs, edge cases, or real-world outcomes (0-10).
4. OUTPUT FORMAT:
   - Output ONLY a single, valid JSON object conforming to the schema below.
   - Do NOT include markdown commentary or conversational filler outside the JSON.

JSON SCHEMA:
{
  "overall_score": <integer from 0 to 10>,
  "relevance_score": <integer from 0 to 10>,
  "technical_score": <integer from 0 to 10>,
  "clarity_score": <integer from 0 to 10>,
  "completeness_score": <integer from 0 to 10>,
  "strengths": [
    "<specific strong point demonstrated in the candidate's answer>"
  ],
  "missing_points": [
    "<important concept, tradeoff, or detail omitted from the answer>"
  ],
  "improvement_tips": [
    "<concrete, actionable tip to elevate this answer to top-tier status>"
  ],
  "suggested_better_answer": "<an exemplary, polished model answer illustrating best practices for this question>",
  "final_feedback": "<2-3 sentence encouraging, constructive summary from the coach>"
}"""


def build_evaluation_user_prompt(
    question: str,
    category: str,
    answer: str,
    job_description: Optional[str] = None,
    resume_context: Optional[str] = None,
) -> str:
    """Construct the user prompt for evaluating an interview answer."""
    jd_block = f"\n<target_job_context>\n{job_description}\n</target_job_context>" if job_description else ""
    resume_block = f"\n<candidate_resume_context>\n{resume_context}\n</candidate_resume_context>" if resume_context else ""

    return f"""Please evaluate the candidate's interview answer for the following question:

<interview_question category="{category}">
{question}
</interview_question>

<candidate_answer>
{answer}
</candidate_answer>{jd_block}{resume_block}

Remember: Output ONLY the requested JSON object conforming to the schema."""


def evaluate_answer_with_bedrock(
    request: InterviewEvaluateRequest
) -> Tuple[InterviewEvaluationSchema, str]:
    """
    Invoke Amazon Bedrock Converse API to evaluate a candidate's interview answer.
    
    Returns:
        Tuple[InterviewEvaluationSchema, str]: (Parsed evaluation schema, Model ID used)
    """
    region, model_id = get_bedrock_config()
    client = get_bedrock_client()

    system_prompt = build_evaluation_system_prompt()
    user_prompt = build_evaluation_user_prompt(
        question=request.question,
        category=request.category,
        answer=request.answer,
        job_description=request.job_description,
        resume_context=request.resume_context,
    )

    logger.info(f"Invoking Amazon Bedrock Converse API for Interview Evaluation using model: '{model_id}' in region: '{region}'")

    try:
        response = client.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"text": user_prompt}
                    ]
                }
            ],
            system=[
                {"text": system_prompt}
            ],
            inferenceConfig={
                "temperature": 0.2,
                "maxTokens": 3000,
                "topP": 0.9
            }
        )

        output_message = response.get("output", {}).get("message", {})
        content_list = output_message.get("content", [])
        if not content_list or "text" not in content_list[0]:
            raise ValueError("Bedrock Converse response did not contain expected text content.")

        raw_output_text = content_list[0]["text"]
        parsed_json = extract_json_from_response(raw_output_text)

        validated_schema = InterviewEvaluationSchema(**parsed_json)
        return validated_schema, model_id

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_msg = e.response.get("Error", {}).get("Message", str(e))
        logger.error(f"AWS Bedrock ClientError during evaluation [{error_code}]: {error_msg}")
        raise e
    except (NoCredentialsError, EndpointConnectionError) as e:
        logger.error(f"AWS Credential / Connection Error during evaluation: {e}")
        raise e


def generate_fallback_interview_evaluation(
    question: str,
    category: str,
    answer: str
) -> InterviewEvaluationSchema:
    """
    Generates a dynamic, intelligent evaluation for offline / preview mode.
    """
    word_count = len(answer.split())
    has_example = any(k in answer.lower() for k in ["for example", "instance", "in my project", "we implemented", "specifically"])
    has_technical_terms = any(k in answer.lower() for k in ["api", "react", "state", "database", "latency", "async", "cache", "scale", "component", "cloud", "aws", "docker"])

    first_word = question.split()[0].lower() if question.split() else ""
    rel_score = min(10, max(6, 7 + (1 if first_word and first_word in answer.lower() else 0)))
    tech_score = min(10, max(5, 6 + (2 if has_technical_terms else 0) + (1 if word_count > 60 else 0)))
    clarity_score = min(10, max(6, 7 + (2 if word_count in range(40, 250) else 0)))
    comp_score = min(10, max(5, 5 + (2 if has_example else 0) + (2 if word_count > 80 else 1)))
    overall = int(round((rel_score + tech_score + clarity_score + comp_score) / 4))

    return InterviewEvaluationSchema(
        overall_score=overall,
        relevance_score=rel_score,
        technical_score=tech_score,
        clarity_score=clarity_score,
        completeness_score=comp_score,
        strengths=[
            "Answer directly addresses the core objective of the question.",
            "Demonstrated practical familiarity with relevant concepts." if has_technical_terms else "Clear and concise communication style.",
            "Structured response with a logical sequence of ideas."
        ],
        missing_points=[
            "Could include a concrete, quantifiable project example (e.g. STAR method metrics)." if not has_example else "Could explain architectural tradeoffs and error handling strategies more explicitly.",
            "Consider mentioning edge cases or scalability implications in production environments."
        ],
        improvement_tips=[
            "Use the STAR method (Situation, Task, Action, Result) to frame real-world stories with measurable impact.",
            "Deepen technical terminology by discussing performance optimizations and failure recovery.",
            "Conclude with a brief summary statement linking your answer back to the target role."
        ],
        suggested_better_answer=(
            f"When addressing this in a senior interview, start with the core architecture: "
            f"'In my recent project, we designed a solution to handle this by separating concerns across modular layers. "
            f"Specifically, we established clear data contracts, implemented robust error boundaries, and monitored latency. "
            f"This resulted in a 40% reduction in response times and zero production regressions during deployment.'"
        ),
        final_feedback="Solid foundational answer! Adding a specific real-world example with quantifiable results will make your response truly stand out."
    )
