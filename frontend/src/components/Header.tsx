interface HeaderProps {
  backendOnline?: boolean | null;
}

export default function Header({ backendOnline }: HeaderProps) {
  return (
    <header className="header">
      <div className="header-inner">
        <a href="/" className="header-logo">
          <span className="logo-icon">🔍</span>
          <span>
            Job<span className="logo-accent">Lens</span> AI
          </span>
        </a>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
          {backendOnline === true && (
            <span
              style={{
                fontSize: '0.72rem',
                color: 'var(--success-light)',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                background: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.25)',
                padding: '2px 8px',
                borderRadius: 'var(--radius-full)',
              }}
            >
              <span className="pulse-dot" style={{ width: '6px', height: '6px' }} />
              API Online
            </span>
          )}
          <span className="header-badge">AI-Powered</span>
        </div>
      </div>
    </header>
  );
}
