import { useEffect, useState } from 'react';

interface MatchScoreProps {
  score: number;
  category: string;
  summary: string;
}

export default function MatchScore({ score, category, summary }: MatchScoreProps) {
  const [animatedScore, setAnimatedScore] = useState(0);

  // Animate the score counting up
  useEffect(() => {
    let start = 0;
    const duration = 1500;
    const startTime = performance.now();

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out
      const eased = 1 - Math.pow(1 - progress, 3);
      start = Math.round(eased * score);
      setAnimatedScore(start);
      if (progress < 1) requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
  }, [score]);

  // SVG circle math
  const radius = 78;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (animatedScore / 100) * circumference;

  const getScoreColor = () => {
    if (score >= 90) return '#10b981';
    if (score >= 75) return '#6366f1';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  const getCategoryClass = () => {
    if (score >= 90) return 'match-category-excellent';
    if (score >= 75) return 'match-category-strong';
    if (score >= 60) return 'match-category-moderate';
    return 'match-category-needs-improvement';
  };

  return (
    <div className="match-score-section">
      <div className="match-score-ring">
        <svg viewBox="0 0 180 180">
          <circle className="ring-bg" cx="90" cy="90" r={radius} />
          <circle
            className="ring-progress"
            cx="90"
            cy="90"
            r={radius}
            stroke={getScoreColor()}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="match-score-value">
          <div className="match-score-number" style={{ color: getScoreColor() }}>
            {animatedScore}
          </div>
          <div className="match-score-percent">/ 100</div>
        </div>
      </div>

      <div className={`match-score-category ${getCategoryClass()}`}>
        {score >= 90 ? '🌟' : score >= 75 ? '💪' : score >= 60 ? '📈' : '🎯'}{' '}
        {category}
      </div>

      <p className="match-score-summary">{summary}</p>
      <p className="match-score-disclaimer">
        ⓘ This is an AI-generated compatibility estimate and should not be
        treated as a definitive assessment. Always verify requirements
        independently.
      </p>
    </div>
  );
}
