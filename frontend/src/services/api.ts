/**
 * JobLens AI Frontend API Service
 * Connects the React client to the FastAPI backend and Bedrock AI services.
 */

import type { AnalysisResult, InterviewEvaluation } from '../types/analysis';

const rawBaseUrl =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  'http://127.0.0.1:8000';

// Sanitize URL by removing trailing slashes to prevent double slashes (e.g. //api/health)
const API_BASE_URL = rawBaseUrl.replace(/\/+$/, '');

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  bedrock_configured: boolean;
}

export interface ExtractedDocument {
  filename?: string | null;
  source: 'pdf' | 'text';
  page_count?: number | null;
  text_length: number;
  text?: string | null;
}

export interface AnalyzeDocumentsResponse {
  success: boolean;
  message: string;
  mode: 'bedrock_ai' | 'mock_preview';
  model_id?: string | null;
  resume: ExtractedDocument;
  job_description: ExtractedDocument;
  analysis: AnalysisResult;
}

export interface InterviewEvaluateResponse {
  success: boolean;
  message: string;
  mode: 'bedrock_ai' | 'mock_preview';
  model_id?: string | null;
  evaluation: InterviewEvaluation;
}

export class ApiError extends Error {
  statusCode?: number;
  detail?: string;

  constructor(message: string, statusCode?: number, detail?: string) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.detail = detail;
  }
}

/**
 * Check backend health status and whether Amazon Bedrock is configured.
 */
export async function checkBackendHealth(): Promise<HealthResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      throw new ApiError(
        `Backend returned status ${response.status}`,
        response.status
      );
    }

    return await response.json();
  } catch (error: any) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(
      'Unable to connect to JobLens AI backend. Please ensure the backend server is running.',
      0,
      error.message
    );
  }
}

/**
 * Upload resume and job description to FastAPI for extraction and Amazon Bedrock AI analysis.
 */
export async function extractAndAnalyzeDocuments(
  resumeFile: File,
  jdFile: File | null,
  jdText: string
): Promise<AnalyzeDocumentsResponse> {
  const formData = new FormData();
  formData.append('resume', resumeFile);

  if (jdFile) {
    formData.append('jd_file', jdFile);
  } else if (jdText.trim()) {
    formData.append('jd_text', jdText.trim());
  } else {
    throw new ApiError(
      'Please provide a job description (either upload a PDF or paste text).'
    );
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      const errorMessage =
        data.detail || data.error || 'Failed to process and analyze documents.';
      throw new ApiError(errorMessage, response.status, data.detail);
    }

    return data as AnalyzeDocumentsResponse;
  } catch (error: any) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(
      'Network error: could not reach backend server. Please check your connection.',
      0,
      error.message
    );
  }
}

/**
 * Submit an interview answer to Amazon Bedrock AI for evaluation.
 */
export async function evaluateInterviewAnswer(params: {
  question: string;
  category: string;
  answer: string;
  job_description?: string;
  resume_context?: string;
}): Promise<InterviewEvaluateResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/interview/evaluate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(params),
    });

    const data = await response.json();

    if (!response.ok) {
      const errorMessage =
        data.detail || data.error || 'Failed to evaluate your interview answer.';
      throw new ApiError(errorMessage, response.status, data.detail);
    }

    return data as InterviewEvaluateResponse;
  } catch (error: any) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(
      'Network error: could not reach backend server to evaluate interview answer.',
      0,
      error.message
    );
  }
}
