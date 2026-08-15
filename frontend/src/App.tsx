import { useState, useCallback, useEffect } from 'react';
import './App.css';
import type { AnalysisResult } from './types/analysis';
import {
  extractAndAnalyzeDocuments,
  checkBackendHealth,
  type ExtractedDocument,
} from './services/api';

import Header from './components/Header';
import Hero from './components/Hero';
import UploadSection from './components/UploadSection';
import AnalyzeButton from './components/AnalyzeButton';
import LoadingState from './components/LoadingState';
import ResultsDashboard from './components/ResultsDashboard';
import InterviewCoach from './components/InterviewCoach';
import Footer from './components/Footer';

type AppState = 'upload' | 'loading' | 'results' | 'error';

export default function App() {
  // App state
  const [appState, setAppState] = useState<AppState>('upload');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [analysisMeta, setAnalysisMeta] = useState<{
    mode: 'bedrock_ai' | 'mock_preview';
    modelId?: string | null;
    resume?: ExtractedDocument;
    jd?: ExtractedDocument;
  } | null>(null);

  // Interview Coach practice state
  const [isPracticing, setIsPracticing] = useState<boolean>(false);

  // Backend status indicator
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  // Upload state
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState('');

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth()
      .then(() => setBackendOnline(true))
      .catch(() => setBackendOnline(false));
  }, []);

  // Can analyze?
  const hasResume = resumeFile !== null;
  const hasJd = jdFile !== null || jdText.trim().length > 30;
  const canAnalyze = hasResume && hasJd;

  // Load sample data for quick testing
  const handleLoadSample = useCallback(() => {
    // Construct a valid in-memory PDF that pypdf can parse
    const validPdfTemplate =
      '%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n' +
      '2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n' +
      '3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>\nendobj\n' +
      '4 0 obj\n<< /Length 280 >>\nstream\nBT\n/F1 12 Tf\n72 712 Td\n' +
      '(Alex Chen - Senior Full Stack Developer. Experienced with React, TypeScript, Node.js, REST APIs, Git, and PostgreSQL. Open source contributor.) Tj\n' +
      'ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000300 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n550\n%%EOF';

    const sampleBlob = new Blob([validPdfTemplate], { type: 'application/pdf' });
    const sampleResume = new File([sampleBlob], 'alex_chen_fullstack_resume.pdf', {
      type: 'application/pdf',
    });

    setResumeFile(sampleResume);
    setJdFile(null);
    setJdText(
      `Job Title: Senior Full-Stack Engineer\n\nAbout the Role:\nWe are seeking an experienced Full-Stack Software Engineer to build scalable web applications. You will design, develop, and maintain high-performance microservices and intuitive frontend user interfaces.\n\nKey Responsibilities:\n- Architect and implement user-facing features using React and TypeScript\n- Build high-throughput REST APIs and serverless microservices using Node.js and AWS Lambda\n- Maintain cloud infrastructure on AWS including S3, API Gateway, and CloudFront\n- Build containerized applications using Docker and configure automated CI/CD pipelines with GitHub Actions\n- Optimize PostgreSQL database schemas and query performance\n\nRequired Qualifications:\n- 3+ years of professional full-stack development experience\n- Strong proficiency in React, TypeScript, and modern JavaScript\n- Experience building backend services and RESTful APIs with Node.js\n- Hands-on experience with AWS cloud services (Lambda, S3, API Gateway)\n- Understanding of Docker containerization and CI/CD pipelines\n- Solid foundation in relational databases (PostgreSQL/MySQL)\n\nPreferred Qualifications:\n- Experience with GraphQL and Redis caching\n- Knowledge of automated testing (Jest, Cypress)\n- Excellent communication and collaboration skills`
    );
  }, []);

  // Real backend AI analysis (Phase 3)
  const handleAnalyze = useCallback(async () => {
    if (!resumeFile) return;

    setAppState('loading');
    setIsPracticing(false);
    setErrorMessage('');

    try {
      // Call FastAPI /api/analyze for PDF extraction and Amazon Bedrock AI analysis
      const response = await extractAndAnalyzeDocuments(resumeFile, jdFile, jdText);

      setAnalysisMeta({
        mode: response.mode,
        modelId: response.model_id,
        resume: response.resume,
        jd: response.job_description,
      });

      // Set the real structured AI analysis directly from Amazon Bedrock
      setResult(response.analysis);
      setAppState('results');

      // Scroll smoothly to results
      setTimeout(() => {
        document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' });
      }, 150);
    } catch (err: any) {
      console.error('AI Analysis failed:', err);
      setErrorMessage(
        err.detail ||
          err.message ||
          'Failed to complete AI analysis. Please check your network and configuration, then try again.'
      );
      setAppState('error');
    }
  }, [resumeFile, jdFile, jdText]);

  // Reset everything
  const handleReset = useCallback(() => {
    setAppState('upload');
    setResult(null);
    setAnalysisMeta(null);
    setIsPracticing(false);
    setResumeFile(null);
    setJdFile(null);
    setJdText('');
    setErrorMessage('');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  return (
    <div className="app">
      <Header backendOnline={backendOnline} />

      <main className="app-main">
        {/* Hero Section */}
        {appState === 'upload' && <Hero />}

        {/* Upload Section */}
        {appState === 'upload' && (
          <>
            <UploadSection
              resumeFile={resumeFile}
              jdFile={jdFile}
              jdText={jdText}
              onResumeSelect={setResumeFile}
              onResumeRemove={() => setResumeFile(null)}
              onJdFileSelect={setJdFile}
              onJdFileRemove={() => setJdFile(null)}
              onJdTextChange={setJdText}
              onLoadSample={handleLoadSample}
            />
            <AnalyzeButton
              disabled={!canAnalyze}
              loading={false}
              onClick={handleAnalyze}
            />
          </>
        )}

        {/* Loading State */}
        {appState === 'loading' && <LoadingState />}

        {/* Results Dashboard or Interview Coach Practice Studio */}
        {appState === 'results' && result && (
          <div>
            {/* Top Analysis Meta Badge */}
            {analysisMeta && (
              <div
                className="result-card"
                style={{
                  background:
                    analysisMeta.mode === 'bedrock_ai'
                      ? 'rgba(99, 102, 241, 0.1)'
                      : 'rgba(16, 185, 129, 0.08)',
                  borderColor:
                    analysisMeta.mode === 'bedrock_ai'
                      ? 'rgba(99, 102, 241, 0.3)'
                      : 'rgba(16, 185, 129, 0.25)',
                  marginBottom: 'var(--space-xl)',
                  fontSize: '0.85rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: 'var(--space-md)',
                }}
              >
                <div>
                  <span
                    style={{
                      color:
                        analysisMeta.mode === 'bedrock_ai'
                          ? 'var(--primary-light)'
                          : 'var(--success-light)',
                      fontWeight: 700,
                    }}
                  >
                    {analysisMeta.mode === 'bedrock_ai'
                      ? '🧠 Amazon Bedrock AI Analysis'
                      : '⚡ Career Analysis Engine'}
                    :
                  </span>{' '}
                  Resume ({analysisMeta.resume?.text_length} chars
                  {analysisMeta.resume?.page_count
                    ? `, ${analysisMeta.resume.page_count} page(s)`
                    : ''}
                  ) & Job Description ({analysisMeta.jd?.text_length} chars,{' '}
                  {analysisMeta.jd?.source.toUpperCase()})
                </div>
                <span
                  style={{
                    background:
                      analysisMeta.mode === 'bedrock_ai'
                        ? 'linear-gradient(135deg, var(--primary), var(--secondary))'
                        : 'rgba(16, 185, 129, 0.2)',
                    color: 'white',
                    padding: '3px 12px',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    letterSpacing: '0.02em',
                  }}
                >
                  {analysisMeta.modelId || 'Bedrock Converse API'}
                </span>
              </div>
            )}

            {/* Mode Toggle: Practice Interview Studio vs. Full Results Dashboard */}
            {isPracticing ? (
              <InterviewCoach
                questions={result.interview_questions}
                jobDescriptionText={jdText}
                onExit={() => setIsPracticing(false)}
              />
            ) : (
              <ResultsDashboard
                result={result}
                onReset={handleReset}
                onStartPractice={() => {
                  setIsPracticing(true);
                  window.scrollTo({ top: 200, behavior: 'smooth' });
                }}
              />
            )}
          </div>
        )}

        {/* Error State */}
        {appState === 'error' && (
          <div className="loading-overlay">
            <div style={{ fontSize: '3rem', marginBottom: 'var(--space-lg)' }}>
              ⚠️
            </div>
            <div className="loading-message">Analysis Error</div>
            <div
              className="loading-sub"
              style={{
                maxWidth: '540px',
                margin: '0 auto',
                lineHeight: 1.6,
                color: 'var(--danger-light)',
              }}
            >
              {errorMessage}
            </div>
            <div style={{ marginTop: 'var(--space-xl)' }}>
              <button className="analyze-btn" onClick={handleReset}>
                🔄 Try Again
              </button>
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
