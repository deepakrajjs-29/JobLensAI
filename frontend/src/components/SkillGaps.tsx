import type { SkillGap } from '../types/analysis';

interface SkillGapsProps {
  gaps: SkillGap[];
  title?: string;
  icon?: string;
}

export default function SkillGaps({
  gaps,
  title = 'Skill Gaps',
  icon = '🔍',
}: SkillGapsProps) {
  return (
    <div className="result-card">
      <div className="result-card-header">
        <span
          className="result-card-icon"
          style={{ background: 'rgba(239, 68, 68, 0.12)' }}
        >
          {icon}
        </span>
        <h3>{title}</h3>
      </div>
      <div className="skill-gap-list">
        {gaps.map((gap) => (
          <div
            key={gap.skill}
            className={`skill-gap-item priority-${gap.priority}`}
          >
            <div>
              <div className="skill-gap-header">
                <span className="skill-gap-name">{gap.skill}</span>
                <span className={`priority-badge ${gap.priority}`}>
                  {gap.priority}
                </span>
              </div>
              <div className="skill-gap-reason">{gap.reason}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
