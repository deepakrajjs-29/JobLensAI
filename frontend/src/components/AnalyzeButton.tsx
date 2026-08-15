interface AnalyzeButtonProps {
  disabled: boolean;
  loading: boolean;
  onClick: () => void;
}

export default function AnalyzeButton({
  disabled,
  loading,
  onClick,
}: AnalyzeButtonProps) {
  return (
    <div className="analyze-section">
      <button
        className="analyze-btn"
        disabled={disabled || loading}
        onClick={onClick}
        id="analyze-btn"
      >
        {loading ? (
          <>
            <span className="btn-icon">⏳</span>
            Analyzing...
          </>
        ) : (
          <>
            <span className="btn-icon">🚀</span>
            Analyze My Fit
          </>
        )}
      </button>
      {disabled && !loading && (
        <p className="analyze-hint">
          Upload your resume and provide a job description to get started
        </p>
      )}
    </div>
  );
}
