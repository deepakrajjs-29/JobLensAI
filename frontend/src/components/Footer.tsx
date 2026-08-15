export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <p className="footer-privacy">
          🔒 Your documents are processed for analysis purposes only and are not
          stored permanently. JobLens AI does not retain your resume or job
          descriptions beyond the current session.
        </p>
        <p className="footer-credit">
          Built with ❤️ for the{' '}
          <span className="highlight">AWS Weekend Creative Challenge</span> ·
          Powered by Amazon Bedrock
        </p>
      </div>
    </footer>
  );
}
