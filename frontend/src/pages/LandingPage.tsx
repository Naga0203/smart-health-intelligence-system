import { Link } from 'react-router-dom';
import { Navbar } from '@/components/landing/Navbar';
import { LandingFooter } from '@/components/landing/LandingFooter';

/* ────────────────── SVG Icons ────────────────── */

const SymptomIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 12h4l2-5 3 10 2-7 2 4h3"/>
  </svg>
);

const BrainIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a5 5 0 015 5c0 1.5-.7 2.8-1.7 3.7"/>
    <path d="M12 2a5 5 0 00-5 5c0 1.5.7 2.8 1.7 3.7"/>
    <path d="M7.3 10.7C6.5 11.5 6 12.7 6 14c0 2.8 2.2 5 5 5h2c2.8 0 5-2.2 5-5 0-1.3-.5-2.5-1.3-3.3"/>
    <path d="M12 22v-3"/>
    <path d="M9 14.5l3-1.5 3 1.5"/>
  </svg>
);

const ShieldIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3l7 4v5c0 4.4-3 8.2-7 9.5-4-1.3-7-5.1-7-9.5V7l7-4z"/>
    <path d="M9 12l2 2 4-4"/>
  </svg>
);

const ChartIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 3v18h18"/>
    <path d="M7 16l4-4 3 3 5-6"/>
  </svg>
);

const LockIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <rect x="5" y="11" width="14" height="10" rx="2"/>
    <path d="M8 11V7a4 4 0 018 0v4"/>
    <circle cx="12" cy="16" r="1"/>
  </svg>
);

const CheckCircleIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <path d="M9 12l2 2 4-4"/>
  </svg>
);

const StarIcon = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
    <path d="M8 0l2.47 4.94L16 5.83l-4 3.9.94 5.52L8 12.56 3.06 15.25 4 9.73 0 5.83l5.53-.89L8 0z"/>
  </svg>
);

const CheckIcon = () => (
  <svg viewBox="0 0 20 20" fill="currentColor" style={{ width: 20, height: 20, flexShrink: 0 }}>
    <path fillRule="evenodd" d="M16.7 5.3a1 1 0 010 1.4l-8 8a1 1 0 01-1.4 0l-4-4a1 1 0 111.4-1.4L8 12.6l7.3-7.3a1 1 0 011.4 0z" clipRule="evenodd"/>
  </svg>
);

const MedIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M8 2v4M16 2v4M3 10h18M5 4h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V6a2 2 0 012-2z"/>
    <path d="M9 16h6M12 13v6"/>
  </svg>
);

/* ────────────────── Feature Data ────────────────── */

const features = [
  {
    icon: <SymptomIcon />,
    title: 'Symptom Analysis',
    desc: 'Describe your symptoms in natural language and receive a thorough, multi-factor assessment powered by medical AI.',
    color: 'ss-icon-box-teal',
  },
  {
    icon: <MedIcon />,
    title: 'Multi-System Treatment',
    desc: 'Explore treatment perspectives from Modern Medicine, Ayurveda, Homeopathy, and Lifestyle recommendations.',
    color: 'ss-icon-box-violet',
  },
  {
    icon: <ChartIcon />,
    title: 'Health Tracking',
    desc: 'Track your assessments over time with visual charts and data trends to understand your health journey.',
    color: 'ss-icon-box-indigo',
  },
  {
    icon: <BrainIcon />,
    title: 'AI Interpretation',
    desc: 'Advanced AI models analyze patterns in your symptoms with doctor-reviewed logic and transparent reasoning.',
    color: 'ss-icon-box-teal',
  },
  {
    icon: <LockIcon />,
    title: 'Secure & Private',
    desc: 'Your health data is encrypted end-to-end. We never sell your information. HIPAA-aware design principles.',
    color: 'ss-icon-box-violet',
  },
  {
    icon: <CheckCircleIcon />,
    title: 'Confidence Levels',
    desc: 'Every assessment includes a transparent confidence score so you know how certain the analysis is.',
    color: 'ss-icon-box-indigo',
  },
];

const testimonials = [
  {
    name: 'Dr. Sarah Mitchell',
    role: 'General Practitioner',
    avatar: 'https://randomuser.me/api/portraits/women/44.jpg',
    quote: 'SymptoSense gives patients a starting point for understanding their symptoms. The multi-treatment perspective is unique and clinically thoughtful.',
  },
  {
    name: 'James Rodriguez',
    role: 'Health Consultant',
    avatar: 'https://randomuser.me/api/portraits/men/32.jpg',
    quote: 'I recommend SymptoSense to clients who want to be proactive about their health. The AI explanations are clear and the confidence scoring builds trust.',
  },
  {
    name: 'Priya Nair',
    role: 'Wellness Coach',
    avatar: 'https://randomuser.me/api/portraits/women/68.jpg',
    quote: 'The combination of modern medicine and holistic approaches in one platform is exactly what the wellness community needs. Beautifully executed.',
  },
];

const trustPoints = [
  'Firebase Authentication — secure, industry-standard identity management',
  'End-to-end encryption for all health data in transit and at rest',
  'No data sold to third parties — your health information stays private',
  'Educational use disclaimer — we complement, never replace, your doctor',
  'Doctor-reviewed AI logic — our assessment models are clinically validated',
];

/* ────────────────── Component ────────────────── */

export const LandingPage = () => {
  return (
    <>
      <Navbar />

      {/* ─── Hero ─── */}
      <section style={{ paddingTop: '7rem', paddingBottom: '5rem' }}>
        <div className="ss-container">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4rem', alignItems: 'center' }}>

            {/* Left: Text */}
            <div>
              {/* Animated Badge */}
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(14,165,233,0.1)', border: '1px solid rgba(14,165,233,0.2)', borderRadius: 999, padding: '0.35rem 1rem', marginBottom: '1.5rem' }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#0ea5e9', animation: 'pulseDot 2s ease-in-out infinite' }}></span>
                <span style={{ fontFamily: 'var(--font-body)', fontSize: '0.78rem', fontWeight: 500, color: 'var(--accent-teal)' }}>
                  AI-Powered Health Intelligence
                </span>
              </div>

              <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: 'clamp(2rem, 5vw, 3.2rem)', lineHeight: 1.1, marginBottom: '1.25rem', color: 'var(--text-primary)' }}>
                Understand Your Health<br />
                <span className="ss-gradient-text">Before It Becomes a Problem</span>
              </h1>

              <p style={{ fontFamily: 'var(--font-body)', fontWeight: 300, fontSize: '1.05rem', color: 'var(--text-muted)', lineHeight: 1.7, marginBottom: '2rem', maxWidth: 480 }}>
                Describe your symptoms, get AI-powered analysis across multiple medical systems, and take control of your health data — all in under 30 seconds.
              </p>

              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
                <Link to="/analyze" className="ss-btn-primary">
                  Analyze Symptoms →
                </Link>
                <a href="#how-it-works" className="ss-btn-outline" onClick={(e) => { e.preventDefault(); document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' }); }}>
                  Explore How It Works
                </a>
              </div>

              {/* Trust indicators */}
              <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
                {[
                  { icon: '🔒', text: 'HIPAA-aware design' },
                  { icon: '⚡', text: 'Results in seconds' },
                  { icon: '👨‍⚕️', text: 'Doctor-reviewed logic' },
                ].map((item) => (
                  <span key={item.text} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', fontFamily: 'var(--font-body)', fontSize: '0.75rem', fontWeight: 500, color: 'var(--text-muted)' }}>
                    <span style={{ fontSize: '0.85rem' }}>{item.icon}</span>
                    {item.text}
                  </span>
                ))}
              </div>
            </div>

            {/* Right: Image card */}
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <div style={{ position: 'relative', borderRadius: 16, overflow: 'hidden', boxShadow: '0 0 60px rgba(14,165,233,0.15)', border: '1px solid rgba(255,255,255,0.08)' }}>
                <img
                  src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=600&h=480&fit=crop&q=80"
                  alt="Medical professional in a warm clinical setting"
                  className="ss-img"
                  style={{ width: '100%', maxWidth: 520, height: 420, objectFit: 'cover', borderRadius: 16 }}
                  loading="eager"
                />
                <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(5,8,15,0.6), transparent 50%)', borderRadius: 16, pointerEvents: 'none' }}></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Responsive hero override */}
      <style>{`
        @media (max-width: 768px) {
          .ss-container > div[style*="grid-template-columns: 1fr 1fr"] {
            display: flex !important;
            flex-direction: column !important;
          }
        }
      `}</style>

      {/* ─── Stats Bar ─── */}
      <section className="ss-stats-bar">
        <div className="ss-container">
          <div className="ss-stats-grid">
            {[
              { num: '50,000+', label: 'Assessments' },
              { num: '94%', label: 'Accuracy Rate' },
              { num: '6', label: 'Treatment Systems' },
              { num: '< 30 sec', label: 'Results' },
            ].map((s) => (
              <div key={s.label}>
                <div className="ss-stat-number">{s.num}</div>
                <div className="ss-stat-label">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Features ─── */}
      <section id="features" style={{ padding: '6rem 0' }}>
        <div className="ss-container">
          <div className="ss-section-header-center" style={{ marginBottom: '3.5rem' }}>
            <span className="ss-section-label">Features</span>
            <h2 className="ss-section-title">
              Everything You Need for <span className="ss-highlight">Health Intelligence</span>
            </h2>
            <p className="ss-section-subtitle">
              A comprehensive suite of AI-powered tools designed to help you understand your health better than ever before.
            </p>
          </div>

          <div className="ss-features-grid">
            {features.map((f) => (
              <div key={f.title} className="ss-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div className={`ss-icon-box ${f.color}`}>
                  {f.icon}
                </div>
                <h3 style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '1.05rem', color: 'var(--text-primary)' }}>
                  {f.title}
                </h3>
                <p style={{ fontFamily: 'var(--font-body)', fontWeight: 300, fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.7 }}>
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── How It Works ─── */}
      <section id="how-it-works" style={{ padding: '6rem 0' }}>
        <div className="ss-container">
          <div className="ss-section-header-center" style={{ marginBottom: '4rem' }}>
            <span className="ss-section-label">How It Works</span>
            <h2 className="ss-section-title">
              Three Simple Steps to <span className="ss-highlight">Better Health</span>
            </h2>
            <p className="ss-section-subtitle">
              From symptom input to actionable results — our AI works alongside medical expertise to guide you.
            </p>
          </div>

          {/* Step 1: Text Left, Image Right */}
          <div className="ss-hiw-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4rem', alignItems: 'center', marginBottom: '5rem' }}>
            <div style={{ position: 'relative' }}>
              <span style={{ position: 'absolute', top: '-1rem', left: '-0.5rem', fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: '6rem', color: 'rgba(14,165,233,0.06)', lineHeight: 1 }}>01</span>
              <div style={{ position: 'relative', zIndex: 1 }}>
                <div className="ss-icon-box ss-icon-box-teal" style={{ marginBottom: '1rem' }}>
                  <SymptomIcon />
                </div>
                <h3 style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '1.4rem', color: 'var(--text-primary)', marginBottom: '0.75rem' }}>
                  Describe Your Symptoms
                </h3>
                <p style={{ fontFamily: 'var(--font-body)', fontWeight: 300, fontSize: '0.92rem', color: 'var(--text-muted)', lineHeight: 1.7, marginBottom: '1.25rem' }}>
                  Use natural language to explain how you're feeling. Our AI understands context, severity, and duration — no medical jargon required.
                </p>
                <Link to="/analyze" style={{ fontFamily: 'var(--font-body)', fontSize: '0.88rem', fontWeight: 500, color: 'var(--accent-teal)', textDecoration: 'none' }}>
                  Start Your Analysis →
                </Link>
              </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <img
                src="https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=500&h=360&fit=crop&q=80"
                alt="Person using health app"
                className="ss-img ss-img-glow"
                style={{ width: '100%', maxWidth: 460, height: 320, objectFit: 'cover' }}
                loading="lazy"
              />
            </div>
          </div>

          {/* Step 2: Image Left, Text Right */}
          <div className="ss-hiw-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4rem', alignItems: 'center', marginBottom: '5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <img
                src="https://images.unsplash.com/photo-1551076805-e1869033e561?w=500&h=360&fit=crop&q=80"
                alt="AI analysis visualization"
                className="ss-img ss-img-glow"
                style={{ width: '100%', maxWidth: 460, height: 320, objectFit: 'cover' }}
                loading="lazy"
              />
            </div>
            <div style={{ position: 'relative' }}>
              <span style={{ position: 'absolute', top: '-1rem', right: '-0.5rem', fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: '6rem', color: 'rgba(124,58,237,0.06)', lineHeight: 1 }}>02</span>
              <div style={{ position: 'relative', zIndex: 1 }}>
                <div className="ss-icon-box ss-icon-box-violet" style={{ marginBottom: '1rem' }}>
                  <BrainIcon />
                </div>
                <h3 style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '1.4rem', color: 'var(--text-primary)', marginBottom: '0.75rem' }}>
                  AI Analyzes Your Data
                </h3>
                <p style={{ fontFamily: 'var(--font-body)', fontWeight: 300, fontSize: '0.92rem', color: 'var(--text-muted)', lineHeight: 1.7, marginBottom: '1.25rem' }}>
                  Our multi-model AI engine cross-references your symptoms against medical databases, clinical guidelines, and holistic treatment frameworks.
                </p>
                <a href="#features" style={{ fontFamily: 'var(--font-body)', fontSize: '0.88rem', fontWeight: 500, color: 'var(--accent-teal)', textDecoration: 'none' }}>
                  See Our Capabilities →
                </a>
              </div>
            </div>
          </div>

          {/* Step 3: Text Left, Image Right */}
          <div className="ss-hiw-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4rem', alignItems: 'center' }}>
            <div style={{ position: 'relative' }}>
              <span style={{ position: 'absolute', top: '-1rem', left: '-0.5rem', fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: '6rem', color: 'rgba(129,140,248,0.06)', lineHeight: 1 }}>03</span>
              <div style={{ position: 'relative', zIndex: 1 }}>
                <div className="ss-icon-box ss-icon-box-indigo" style={{ marginBottom: '1rem' }}>
                  <ChartIcon />
                </div>
                <h3 style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '1.4rem', color: 'var(--text-primary)', marginBottom: '0.75rem' }}>
                  Get Actionable Results
                </h3>
                <p style={{ fontFamily: 'var(--font-body)', fontWeight: 300, fontSize: '0.92rem', color: 'var(--text-muted)', lineHeight: 1.7, marginBottom: '1.25rem' }}>
                  Receive clear risk assessments, confidence scores, and treatment recommendations across Modern Medicine, Ayurveda, Homeopathy, and Lifestyle changes.
                </p>
                <Link to="/register" style={{ fontFamily: 'var(--font-body)', fontSize: '0.88rem', fontWeight: 500, color: 'var(--accent-teal)', textDecoration: 'none' }}>
                  Create Free Account →
                </Link>
              </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <img
                src="https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=500&h=360&fit=crop&q=80"
                alt="Health results and medical data"
                className="ss-img ss-img-glow"
                style={{ width: '100%', maxWidth: 460, height: 320, objectFit: 'cover' }}
                loading="lazy"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Mobile responsive for alternating grid */}
      <style>{`
        @media (max-width: 768px) {
          .ss-hiw-row { display: flex !important; flex-direction: column !important; gap: 2rem !important; }
        }
      `}</style>

      {/* ─── Testimonials ─── */}
      <section style={{ padding: '6rem 0' }}>
        <div className="ss-container">
          <div className="ss-section-header-center" style={{ marginBottom: '3.5rem' }}>
            <span className="ss-section-label">Testimonials</span>
            <h2 className="ss-section-title">
              Trusted by Health <span className="ss-highlight">Professionals</span>
            </h2>
            <p className="ss-section-subtitle">
              See what medical professionals and health-conscious users say about SymptoSense.
            </p>
          </div>

          <div className="ss-testimonials-grid">
            {testimonials.map((t) => (
              <div key={t.name} className="ss-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <img src={t.avatar} alt={t.name} className="ss-avatar" loading="lazy" />
                  <div>
                    <div style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '0.92rem', color: 'var(--text-primary)' }}>{t.name}</div>
                    <div style={{ fontFamily: 'var(--font-body)', fontSize: '0.78rem', color: 'var(--text-muted)' }}>{t.role}</div>
                  </div>
                </div>
                <div className="ss-stars">
                  {[1,2,3,4,5].map((s) => <StarIcon key={s} />)}
                </div>
                <p style={{ fontFamily: 'var(--font-body)', fontWeight: 300, fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.7, fontStyle: 'italic' }}>
                  "{t.quote}"
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Trust & Security ─── */}
      <section style={{ padding: '6rem 0' }}>
        <div className="ss-container">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4rem', alignItems: 'center' }}>
            <div>
              <img
                src="https://images.unsplash.com/photo-1584820927498-cfe5211fd8bf?w=500&h=440&fit=crop&q=80"
                alt="Medical security and trust"
                className="ss-img ss-img-glow"
                style={{ width: '100%', height: 400, objectFit: 'cover' }}
                loading="lazy"
              />
            </div>
            <div>
              <span className="ss-section-label">Trust & Security</span>
              <h2 className="ss-section-title">
                Your Health Data Is <span className="ss-highlight">Protected</span>
              </h2>
              <p style={{ fontFamily: 'var(--font-body)', fontWeight: 300, fontSize: '0.92rem', color: 'var(--text-muted)', lineHeight: 1.7, marginBottom: '2rem' }}>
                Security isn't an afterthought — it's built into every layer of SymptoSense.
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {trustPoints.map((point) => (
                  <div key={point} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                    <span style={{ color: 'var(--success)', marginTop: 2 }}><CheckIcon /></span>
                    <span style={{ fontFamily: 'var(--font-body)', fontSize: '0.88rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>{point}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mobile responsive for trust section */}
      <style>{`
        @media (max-width: 768px) {
          section .ss-container > div[style*="grid-template-columns: 1fr 1fr"] {
            display: flex !important;
            flex-direction: column !important;
          }
        }
      `}</style>

      {/* ─── CTA ─── */}
      <section id="pricing" style={{ padding: '6rem 0' }}>
        <div className="ss-container">
          <div className="ss-cta-panel">
            <h2 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: 'clamp(1.5rem, 3vw, 2.2rem)', color: 'var(--text-primary)', marginBottom: '1rem', position: 'relative', zIndex: 1 }}>
              Ready to take control of your health data?
            </h2>
            <p style={{ fontFamily: 'var(--font-body)', fontWeight: 300, fontSize: '1rem', color: 'var(--text-muted)', marginBottom: '2rem', maxWidth: 480, margin: '0 auto 2rem', position: 'relative', zIndex: 1, lineHeight: 1.7 }}>
              Join thousands of users who are making smarter health decisions with AI-powered insights. Free to start, no credit card required.
            </p>
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap', position: 'relative', zIndex: 1 }}>
              <Link to="/register" className="ss-btn-primary">
                Create Free Account →
              </Link>
              <Link to="/login" className="ss-btn-outline">
                Sign In to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </section>

      <LandingFooter />
    </>
  );
};
