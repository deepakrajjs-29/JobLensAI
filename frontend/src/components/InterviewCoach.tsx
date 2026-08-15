import { useState, useCallback } from 'react';
import type { InterviewQuestion, InterviewEvaluation } from '../types/analysis';
import { evaluateInterviewAnswer } from '../services/api';

interface InterviewCoachProps {
  questions: InterviewQuestion[];
  jobDescriptionText?: string;
  resumeContextText?: string;
  onExit: () => void;
}

export default function InterviewCoach({
  questions,
  jobDescriptionText,
  resumeContextText,
  onExit,
}: InterviewCoachProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState('');
  const [evaluating, setEvaluating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showHint, setShowHint] = useState(false);

  // Store completed evaluations
  const [evaluations, setEvaluations] = useState<Record<number, InterviewEvaluation>>({});
  const [completedSession, setCompletedSession] = useState(false);

  const currentQuestion = questions[currentIndex] || questions[0];
  const currentEval = evaluations[currentIndex] || null;

  // Calculate difficulty dynamically
  const getDifficulty = (q: InterviewQuestion): 'Easy' | 'Medium' | 'Hard' => {
    if (q.category === 'technical') return 'Hard';
    if (q.category === 'job-specific') return 'Medium';
    if (q.category === 'resume') return 'Medium';
    return 'Easy';
  };

  const difficulty = getDifficulty(currentQuestion);

  // Handle answer submission to Bedrock
  const handleSubmitAnswer = useCallback(async () => {
    const trimmed = answer.trim();
    if (trimmed.length < 10) {
      setErrorMessage('Please provide a little more detail before submitting (minimum 10 characters).');
      return;
    }

    setEvaluating(true);
    setErrorMessage(null);

    try {
      const response = await evaluateInterviewAnswer({
        question: currentQuestion.question,
        category: currentQuestion.category,
        answer: trimmed,
        job_description: jobDescriptionText,
        resume_context: resumeContextText,
      });

      setEvaluations((prev) => ({
        ...prev,
        [currentIndex]: response.evaluation,
      }));
    } catch (err: any) {
      console.error('Answer evaluation failed:', err);
      setErrorMessage(err.detail || err.message || 'Failed to evaluate answer. Please try again.');
    } finally {
      setEvaluating(false);
    }
  }, [answer, currentQuestion, currentIndex, jobDescriptionText, resumeContextText]);

  // Next question handler
  const handleNextQuestion = useCallback(() => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
      setAnswer('');
      setShowHint(false);
      setErrorMessage(null);
    } else {
      setCompletedSession(true);
    }
  }, [currentIndex, questions.length]);

  // Restart practice session
  const handleRestart = useCallback(() => {
    setCurrentIndex(0);
    setAnswer('');
    setEvaluations({});
    setCompletedSession(false);
    setShowHint(false);
    setErrorMessage(null);
  }, []);

  // Calculate aggregate stats for final summary
  const completedList = Object.values(evaluations);
  const avgScore =
    completedList.length > 0
      ? (
          completedList.reduce((acc, curr) => acc + curr.overall_score, 0) /
          completedList.length
        ).toFixed(1)
      : '0.0';

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'var(--success-light)';
    if (score >= 6) return 'var(--primary-light)';
    return 'var(--warning-light)';
  };

  return (
    <div className="interview-coach-container">
      {/* ------------------------------------------------------------- */}
      {/* 1. Final Summary View                                          */}
      {/* ------------------------------------------------------------- */}
      {completedSession ? (
        <div className="result-card interview-summary-card">
          <div style={{ textAlign: 'center', marginBottom: 'var(--space-xl)' }}>
            <div style={{ fontSize: '3rem', marginBottom: 'var(--space-sm)' }}>🎉</div>
            <h2 style={{ fontSize: '1.8rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
              Interview Practice Complete!
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
              Great job preparing for your upcoming interviews. Here is your overall session performance.
            </p>
          </div>

          <div className="interview-summary-grid">
            <div className="summary-stat-box">
              <div className="summary-stat-num" style={{ color: 'var(--primary-light)' }}>
                {completedList.length} / {questions.length}
              </div>
              <div className="summary-stat-label">Questions Practiced</div>
            </div>

            <div className="summary-stat-box">
              <div
                className="summary-stat-num"
                style={{ color: getScoreColor(Number(avgScore)) }}
              >
                {avgScore} <span style={{ fontSize: '1rem', color: 'var(--text-dim)' }}>/ 10</span>
              </div>
              <div className="summary-stat-label">Average Score</div>
            </div>

            <div className="summary-stat-box">
              <div className="summary-stat-num" style={{ color: 'var(--success-light)' }}>
                {Number(avgScore) >= 7 ? 'Strong' : 'Developing'}
              </div>
              <div className="summary-stat-label">Readiness Level</div>
            </div>
          </div>

          <div className="interview-advice-box">
            <h4>💡 Final Coaching Guidance:</h4>
            <p>
              {Number(avgScore) >= 8
                ? 'Your answers demonstrate strong technical depth and clear structure. Continue refining your real-world STAR stories to provide quantifiable impact in your final rounds.'
                : 'Focus on connecting your answers directly to project examples. Elaborate on error recovery, system tradeoffs, and measurable outcomes to maximize your interview scores.'}
            </p>
          </div>

          <div style={{ display: 'flex', gap: 'var(--space-md)', justifyContent: 'center', marginTop: 'var(--space-2xl)' }}>
            <button className="analyze-btn" onClick={handleRestart}>
              🔄 Practice Again
            </button>
            <button className="new-analysis-btn" onClick={onExit}>
              📊 Back to Analysis
            </button>
          </div>
        </div>
      ) : (
        /* ------------------------------------------------------------- */
        /* 2. Interactive Practice Studio                                */
        /* ------------------------------------------------------------- */
        <div className="interview-studio-card">
          {/* Header Bar */}
          <div className="interview-studio-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', flexWrap: 'wrap' }}>
              <span className="interview-progress-pill">
                Question {currentIndex + 1} of {questions.length}
              </span>
              <span className={`iq-category-badge ${currentQuestion.category}`}>
                {currentQuestion.category.toUpperCase()}
              </span>
              <span className={`difficulty-badge ${difficulty.toLowerCase()}`}>
                {difficulty}
              </span>
            </div>

            <button className="interview-exit-btn" onClick={onExit} title="Exit interview and return to analysis">
              ✕ Exit Practice
            </button>
          </div>

          {/* Question Display */}
          <div className="interview-question-box">
            <div className="interview-q-label">Interview Question:</div>
            <h3 className="interview-q-text">{currentQuestion.question}</h3>

            {currentQuestion.hint && (
              <div style={{ marginTop: 'var(--space-md)' }}>
                <button
                  type="button"
                  className="hint-toggle-btn"
                  onClick={() => setShowHint(!showHint)}
                >
                  {showHint ? 'Hide Hint ▴' : '💡 Show Hint ▾'}
                </button>
                {showHint && (
                  <div className="iq-hint" style={{ marginTop: 'var(--space-sm)' }}>
                    {currentQuestion.hint}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* ----------------------------------------------------------- */}
          {/* 3. Answer Studio / Evaluation View                          */}
          {/* ----------------------------------------------------------- */}
          {!currentEval ? (
            <div className="answer-input-container">
              <div className="answer-input-header">
                <label htmlFor="interview-answer" className="answer-label">
                  ✍️ Your Answer:
                </label>
                <span className="char-count">{answer.length} characters</span>
              </div>

              <textarea
                id="interview-answer"
                className="interview-textarea"
                rows={6}
                value={answer}
                onChange={(e) => {
                  setAnswer(e.target.value);
                  if (errorMessage) setErrorMessage(null);
                }}
                onKeyDown={(e) => {
                  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                    handleSubmitAnswer();
                  }
                }}
                placeholder="Type your response here... (Tip: Structure your thoughts clearly, describe real project experience, mention specific technologies, and discuss measurable outcomes. Press Ctrl+Enter to submit)"
                disabled={evaluating}
              />

              {errorMessage && (
                <div className="file-error" style={{ marginBottom: 'var(--space-md)' }}>
                  <span>⚠️</span> {errorMessage}
                </div>
              )}

              <div className="answer-actions">
                <button
                  className="analyze-btn"
                  onClick={handleSubmitAnswer}
                  disabled={evaluating || answer.trim().length < 10}
                >
                  {evaluating ? (
                    <>
                      <span className="btn-icon">⏳</span> Evaluating with Bedrock...
                    </>
                  ) : (
                    <>
                      <span className="btn-icon">🚀</span> Submit Answer for Evaluation
                    </>
                  )}
                </button>
              </div>
            </div>
          ) : (
            /* ----------------------------------------------------------- */
            /* 4. Feedback View after Evaluation                          */
            /* ----------------------------------------------------------- */
            <div className="evaluation-results-container">
              <div className="eval-score-hero">
                <div className="eval-score-circle" style={{ borderColor: getScoreColor(currentEval.overall_score) }}>
                  <span className="eval-score-num" style={{ color: getScoreColor(currentEval.overall_score) }}>
                    {currentEval.overall_score}
                  </span>
                  <span className="eval-score-denom">/ 10</span>
                </div>
                <div className="eval-hero-info">
                  <div className="eval-hero-title">
                    {currentEval.overall_score >= 8
                      ? '🌟 Excellent Response!'
                      : currentEval.overall_score >= 6
                      ? '💪 Solid Foundation'
                      : '📈 Needs Expansion'}
                  </div>
                  <p className="eval-hero-desc">{currentEval.final_feedback}</p>
                </div>
              </div>

              {/* 4-Bar Metric Rubric */}
              <div className="rubric-grid">
                <div className="rubric-item">
                  <div className="rubric-header">
                    <span>Relevance</span>
                    <span className="rubric-score">{currentEval.relevance_score}/10</span>
                  </div>
                  <div className="rubric-bar-bg">
                    <div
                      className="rubric-bar-fill"
                      style={{ width: `${currentEval.relevance_score * 10}%`, background: 'var(--primary)' }}
                    />
                  </div>
                </div>

                <div className="rubric-item">
                  <div className="rubric-header">
                    <span>Technical Depth</span>
                    <span className="rubric-score">{currentEval.technical_score}/10</span>
                  </div>
                  <div className="rubric-bar-bg">
                    <div
                      className="rubric-bar-fill"
                      style={{ width: `${currentEval.technical_score * 10}%`, background: 'var(--secondary)' }}
                    />
                  </div>
                </div>

                <div className="rubric-item">
                  <div className="rubric-header">
                    <span>Clarity & Structure</span>
                    <span className="rubric-score">{currentEval.clarity_score}/10</span>
                  </div>
                  <div className="rubric-bar-bg">
                    <div
                      className="rubric-bar-fill"
                      style={{ width: `${currentEval.clarity_score * 10}%`, background: 'var(--accent)' }}
                    />
                  </div>
                </div>

                <div className="rubric-item">
                  <div className="rubric-header">
                    <span>Completeness</span>
                    <span className="rubric-score">{currentEval.completeness_score}/10</span>
                  </div>
                  <div className="rubric-bar-bg">
                    <div
                      className="rubric-bar-fill"
                      style={{ width: `${currentEval.completeness_score * 10}%`, background: 'var(--success)' }}
                    />
                  </div>
                </div>
              </div>

              {/* Strengths & Missing Points */}
              <div className="sw-grid" style={{ marginTop: 'var(--space-lg)' }}>
                <div className="sw-column">
                  <h4>
                    <span style={{ color: 'var(--success)' }}>✓</span> What You Did Well
                  </h4>
                  <ul className="sw-list">
                    {currentEval.strengths.map((s, i) => (
                      <li key={i} className="sw-item strength">
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="sw-column">
                  <h4>
                    <span style={{ color: 'var(--warning)' }}>⚠️</span> What Was Missing
                  </h4>
                  <ul className="sw-list">
                    {currentEval.missing_points.map((m, i) => (
                      <li key={i} className="sw-item weakness">
                        {m}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Improvement Tips */}
              {currentEval.improvement_tips && currentEval.improvement_tips.length > 0 && (
                <div className="eval-tips-box" style={{ marginTop: 'var(--space-lg)' }}>
                  <h4>💡 How To Improve:</h4>
                  <ul>
                    {currentEval.improvement_tips.map((tip, i) => (
                      <li key={i}>{tip}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Suggested Better Answer */}
              <div className="suggested-answer-box" style={{ marginTop: 'var(--space-lg)' }}>
                <div className="suggested-header">
                  <span>📝 Exemplary Model Answer:</span>
                </div>
                <div className="suggested-body">{currentEval.suggested_better_answer}</div>
              </div>

              {/* Next Question Navigation */}
              <div className="feedback-nav-actions" style={{ marginTop: 'var(--space-2xl)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <button
                  className="new-analysis-btn"
                  onClick={() => {
                    setEvaluations((prev) => {
                      const copy = { ...prev };
                      delete copy[currentIndex];
                      return copy;
                    });
                  }}
                >
                  🔄 Retry Question
                </button>

                <button className="analyze-btn" onClick={handleNextQuestion}>
                  {currentIndex < questions.length - 1 ? 'Next Question →' : 'Finish Interview 🎉'}
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
