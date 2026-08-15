import { useState, useEffect } from 'react';

const STEPS = [
  'Extracting resume content...',
  'Parsing job description...',
  'Analyzing skill alignment...',
  'Identifying gaps & strengths...',
  'Building preparation roadmap...',
  'Generating interview questions...',
];

export default function LoadingState() {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < STEPS.length - 1) return prev + 1;
        return prev;
      });
    }, 500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="loading-overlay">
      <div className="loading-spinner" />
      <div className="loading-message">Analyzing your profile...</div>
      <div className="loading-sub">
        This usually takes a few seconds
      </div>
      <div className="loading-steps">
        {STEPS.map((step, i) => (
          <div
            key={step}
            className={`loading-step ${i < currentStep ? 'done' : ''} ${i === currentStep ? 'active' : ''}`}
          >
            <span className="loading-step-icon">
              {i < currentStep ? '✓' : i === currentStep ? '◉' : '○'}
            </span>
            {step}
          </div>
        ))}
      </div>
    </div>
  );
}
