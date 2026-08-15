import type { RoadmapItem } from '../types/analysis';

interface RoadmapProps {
  items: RoadmapItem[];
}

export default function Roadmap({ items }: RoadmapProps) {
  return (
    <div className="result-card">
      <div className="result-card-header">
        <span
          className="result-card-icon"
          style={{ background: 'rgba(6, 182, 212, 0.15)' }}
        >
          🗺️
        </span>
        <h3>Preparation Roadmap</h3>
      </div>
      <div className="roadmap-timeline">
        {items.map((item) => (
          <div key={item.day} className="roadmap-item">
            <div className="roadmap-day">
              📅 Day {item.day}
              <span className={`priority-badge ${item.priority}`}>
                {item.priority}
              </span>
            </div>
            <div className="roadmap-topic">{item.topic}</div>
            <div className="roadmap-activity">{item.activity}</div>
            <div className="roadmap-meta">
              <span>⏱️ {item.effort}</span>
              <span>💡 {item.reason}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
