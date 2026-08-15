import { useState } from 'react';
import type { InterviewQuestion } from '../types/analysis';

interface InterviewQuestionsProps {
  questions: InterviewQuestion[];
  onStartPractice?: (startIdx?: number) => void;
}

const CATEGORY_LABELS: Record<InterviewQuestion['category'], string> = {
  technical: '💻 Technical',
  resume: '📋 Resume-Based',
  behavioral: '🤝 Behavioral',
  'job-specific': '🎯 Job-Specific',
};

export default function InterviewQuestions({
  questions,
  onStartPractice,
}: InterviewQuestionsProps) {
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  // Group by category
  const grouped = questions.reduce(
    (acc, q) => {
      if (!acc[q.category]) acc[q.category] = [];
      acc[q.category].push(q);
      return acc;
    },
    {} as Record<string, InterviewQuestion[]>
  );

  let globalIdx = 0;

  return (
    <div className="result-card">
      <div className="result-card-header" style={{ justifyContent: 'space-between', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
          <span
            className="result-card-icon"
            style={{ background: 'rgba(245, 158, 11, 0.15)' }}
          >
            ❓
          </span>
          <h3>Interview Questions</h3>
        </div>

        {onStartPractice && (
          <button
            type="button"
            className="practice-interview-cta-btn"
            onClick={() => onStartPractice(0)}
            title="Launch interactive AI Interview Coach"
          >
            🎤 Practice Interview
          </button>
        )}
      </div>

      {Object.entries(grouped).map(([category, catQuestions]) => (
        <div key={category} className="iq-category-group">
          <div className="iq-category-title">
            <span className={`iq-category-badge ${category}`}>
              {CATEGORY_LABELS[category as InterviewQuestion['category']] || category}
            </span>
            <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>
              {catQuestions.length} questions
            </span>
          </div>
          <div className="iq-list">
            {catQuestions.map((q) => {
              const idx = globalIdx++;
              return (
                <div
                  key={idx}
                  className="iq-item"
                  onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ')
                      setExpandedIdx(expandedIdx === idx ? null : idx);
                  }}
                >
                  <div className="iq-question" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ display: 'flex', gap: 'var(--space-sm)', flex: 1 }}>
                      <span className="iq-number">Q{idx + 1}.</span>
                      <span>{q.question}</span>
                    </div>

                    {onStartPractice && (
                      <button
                        type="button"
                        className="iq-practice-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          onStartPractice(idx);
                        }}
                        title="Practice this question"
                      >
                        🎤 Practice
                      </button>
                    )}
                  </div>
                  {expandedIdx === idx && q.hint && (
                    <div className="iq-hint">
                      💡 <strong>Hint:</strong> {q.hint}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
