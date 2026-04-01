import { Link } from 'react-router-dom';

const HeartbeatIcon = () => (
  <svg width="24" height="24" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M5 14h4l2-5 3 10 2-7 2 4h5" stroke="url(#ft_hb)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
    <defs>
      <linearGradient id="ft_hb" x1="0" y1="0" x2="28" y2="28">
        <stop stopColor="#0ea5e9"/>
        <stop offset="1" stopColor="#7c3aed"/>
      </linearGradient>
    </defs>
  </svg>
);

export const LandingFooter = () => {
  return (
    <footer className="ss-footer">
      <div className="ss-container">
        <div className="ss-footer-grid">
          {/* Brand Column */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
              <HeartbeatIcon />
              <span style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>
                SymptoSense
              </span>
            </div>
            <p style={{ fontFamily: 'var(--font-body)', fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.7 }}>
              AI-powered health intelligence that helps you understand your symptoms, assess risks, and explore treatment options — transparently and securely.
            </p>
          </div>

          {/* Platform */}
          <div>
            <h4 className="ss-footer-heading">Platform</h4>
            <div className="ss-footer-links">
              <Link to="/analyze">Symptom Analyzer</Link>
              <Link to="/app/dashboard">Dashboard</Link>
              <Link to="/app/history">Assessment History</Link>
              <Link to="/register">Create Account</Link>
            </div>
          </div>

          {/* Company */}
          <div>
            <h4 className="ss-footer-heading">Company</h4>
            <div className="ss-footer-links">
              <Link to="/about">About Us</Link>
              <a href="#how-it-works">How It Works</a>
              <a href="#">Privacy Policy</a>
              <a href="#">Terms of Service</a>
            </div>
          </div>

          {/* Important Notice */}
          <div>
            <h4 className="ss-footer-heading">Important Notice</h4>
            <p style={{ fontFamily: 'var(--font-body)', fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.7 }}>
              SymptoSense is designed for educational and informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider.
            </p>
          </div>
        </div>

        <div className="ss-footer-bar">
          <span>© {new Date().getFullYear()} SymptoSense. All rights reserved.</span>
          <div className="ss-footer-legal">
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
            <a href="#">Cookies</a>
          </div>
        </div>
      </div>
    </footer>
  );
};
