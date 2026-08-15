interface SkillsListProps {
  skills: string[];
}

export default function SkillsList({ skills }: SkillsListProps) {
  return (
    <div className="result-card">
      <div className="result-card-header">
        <span
          className="result-card-icon"
          style={{ background: 'rgba(16, 185, 129, 0.15)' }}
        >
          ✅
        </span>
        <h3>Matching Skills</h3>
      </div>
      <div className="skills-grid">
        {skills.map((skill) => (
          <span key={skill} className="skill-chip matching">
            ✓ {skill}
          </span>
        ))}
      </div>
    </div>
  );
}
