import type { AnalysisResult } from '../types/analysis';
import MatchScore from './MatchScore';
import SkillsList from './SkillsList';
import SkillGaps from './SkillGaps';
import StrengthsWeaknesses from './StrengthsWeaknesses';
import Roadmap from './Roadmap';
import InterviewQuestions from './InterviewQuestions';

interface ResultsDashboardProps {
  result: AnalysisResult;
  onReset: () => void;
  onStartPractice?: (startIdx?: number) => void;
}

export default function ResultsDashboard({
  result,
  onReset,
  onStartPractice,
}: ResultsDashboardProps) {
  return (
    <section className="results-dashboard" id="results">
      <div className="results-header">
        <h2>📊 Your Career Analysis</h2>
        <p>Here's how you match up — and how to get even stronger.</p>
      </div>

      {/* Match Score */}
      <MatchScore
        score={result.match_score}
        category={result.match_category}
        summary={result.summary}
      />

      {/* Quick Launch Interview Coach Banner */}
      {onStartPractice && (
        <div className="interview-coach-launch-card">
          <div className="launch-card-left">
            <div className="launch-card-icon">🎤</div>
            <div>
              <h3 className="launch-card-title">Ready to test your knowledge?</h3>
              <p className="launch-card-desc">
                Practice answering these role-tailored questions and get instant, multi-dimensional feedback from our AI Interview Coach.
              </p>
            </div>
          </div>
          <button
            type="button"
            className="launch-practice-btn"
            onClick={() => onStartPractice(0)}
          >
            Start Practice Interview →
          </button>
        </div>
      )}

      <hr className="results-divider" />

      {/* Important Requirements */}
      <div className="result-card">
        <div className="result-card-header">
          <span
            className="result-card-icon"
            style={{ background: 'rgba(99, 102, 241, 0.15)' }}
          >
            📌
          </span>
          <h3>Important Job Requirements</h3>
        </div>
        <div className="requirements-list">
          {result.important_requirements.map((req, i) => (
            <div key={i} className="requirement-item">
              <span className="requirement-icon">▸</span>
              {req}
            </div>
          ))}
        </div>
      </div>

      {/* Matching Skills */}
      <SkillsList skills={result.matching_skills} />

      {/* Skill Gaps */}
      <SkillGaps gaps={result.skill_gaps} />

      {/* Strengths & Weaknesses */}
      <StrengthsWeaknesses
        strengths={result.strengths}
        weaknesses={result.weaknesses}
      />

      {/* Priority Gaps */}
      <SkillGaps
        gaps={result.priority_gaps}
        title="Priority Action Items"
        icon="🎯"
      />

      {/* Preparation Roadmap */}
      <Roadmap items={result.learning_roadmap} />

      {/* Interview Questions */}
      <InterviewQuestions
        questions={result.interview_questions}
        onStartPractice={onStartPractice}
      />

      {/* New Analysis */}
      <div className="new-analysis-section">
        <button className="new-analysis-btn" onClick={onReset}>
          🔄 Start New Analysis
        </button>
      </div>
    </section>
  );
}
