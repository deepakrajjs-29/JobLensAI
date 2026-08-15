interface StrengthsWeaknessesProps {
  strengths: string[];
  weaknesses: string[];
}

export default function StrengthsWeaknesses({
  strengths,
  weaknesses,
}: StrengthsWeaknessesProps) {
  return (
    <div className="result-card">
      <div className="result-card-header">
        <span
          className="result-card-icon"
          style={{ background: 'rgba(139, 92, 246, 0.15)' }}
        >
          ⚖️
        </span>
        <h3>Strengths & Weaknesses</h3>
      </div>
      <div className="sw-grid">
        <div className="sw-column">
          <h4>
            <span style={{ color: 'var(--success)' }}>💪</span> Strengths
          </h4>
          <ul className="sw-list">
            {strengths.map((s, i) => (
              <li key={i} className="sw-item strength">
                <span className="sw-item-icon" style={{ color: 'var(--success)' }}>
                  ✓
                </span>
                {s}
              </li>
            ))}
          </ul>
        </div>
        <div className="sw-column">
          <h4>
            <span style={{ color: 'var(--warning)' }}>⚠️</span> Areas to
            Improve
          </h4>
          <ul className="sw-list">
            {weaknesses.map((w, i) => (
              <li key={i} className="sw-item weakness">
                <span className="sw-item-icon" style={{ color: 'var(--warning)' }}>
                  △
                </span>
                {w}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
