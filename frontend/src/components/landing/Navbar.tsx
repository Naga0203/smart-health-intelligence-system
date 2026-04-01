import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const HeartbeatIcon = () => (
  <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="28" height="28" rx="8" fill="url(#hb_grad)" fillOpacity="0.15"/>
    <path d="M5 14h4l2-5 3 10 2-7 2 4h5" stroke="url(#hb_grad)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
    <defs>
      <linearGradient id="hb_grad" x1="0" y1="0" x2="28" y2="28">
        <stop stopColor="#0ea5e9"/>
        <stop offset="1" stopColor="#7c3aed"/>
      </linearGradient>
    </defs>
  </svg>
);

export const Navbar = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();

  const handleNav = (hash: string) => {
    setMobileOpen(false);
    const el = document.getElementById(hash);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <>
      <nav className="ss-navbar" role="navigation" aria-label="Main navigation">
        <div className="ss-navbar-inner">
          <Link to="/" className="ss-navbar-logo" aria-label="SymptoSense home">
            <HeartbeatIcon />
            <span>SymptoSense</span>
          </Link>

          <div className="ss-navbar-links">
            <a href="#features" onClick={(e) => { e.preventDefault(); handleNav('features'); }}>Features</a>
            <a href="#how-it-works" onClick={(e) => { e.preventDefault(); handleNav('how-it-works'); }}>How It Works</a>
            <Link to="/about">About</Link>
            <a href="#pricing" onClick={(e) => { e.preventDefault(); handleNav('pricing'); }}>Pricing</a>
          </div>

          <div className="ss-navbar-actions">
            <Link to="/login" className="ss-btn-outline ss-btn-sm">Sign In</Link>
            <Link to="/register" className="ss-btn-primary ss-btn-sm">Get Started</Link>
          </div>

          <button
            className="ss-hamburger"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
            aria-expanded={mobileOpen}
          >
            <span></span>
            <span></span>
            <span></span>
          </button>
        </div>
      </nav>

      <div className={`ss-mobile-nav ${mobileOpen ? 'ss-mobile-nav-open' : ''}`}>
        <a href="#features" onClick={(e) => { e.preventDefault(); handleNav('features'); }}>Features</a>
        <a href="#how-it-works" onClick={(e) => { e.preventDefault(); handleNav('how-it-works'); }}>How It Works</a>
        <Link to="/about" onClick={() => setMobileOpen(false)}>About</Link>
        <a href="#pricing" onClick={(e) => { e.preventDefault(); handleNav('pricing'); }}>Pricing</a>
        <div className="ss-mobile-nav-actions">
          <Link to="/login" className="ss-btn-outline" onClick={() => setMobileOpen(false)}>Sign In</Link>
          <Link to="/register" className="ss-btn-primary" onClick={() => setMobileOpen(false)}>Get Started</Link>
        </div>
      </div>
    </>
  );
};
