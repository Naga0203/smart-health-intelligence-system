import { Navbar } from '@/components/landing/Navbar';
import { LandingFooter } from '@/components/landing/LandingFooter';

/* ────── SVG Icons ────── */
const TransparencyIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <path d="M12 6v12M6 12h12"/>
  </svg>
);

const AccessibilityIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="4" r="2"/>
    <path d="M12 6v8M8 10h8M9 22l3-8 3 8"/>
  </svg>
);

const PrivacyIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3l7 4v5c0 4.4-3 8.2-7 9.5-4-1.3-7-5.1-7-9.5V7l7-4z"/>
  </svg>
);

const IntegrityIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
  </svg>
);

const values = [
  {
    icon: <TransparencyIcon />,
    title: 'Transparency',
    desc: 'Every assessment comes with confidence scores and clear explanations. We show our reasoning, not just our conclusions.',
    color: 'ss-icon-box-teal',
  },
  {
    icon: <AccessibilityIcon />,
    title: 'Accessibility',
    desc: 'Health intelligence should be available to everyone. Our platform is free to start and built for all devices and abilities.',
    color: 'ss-icon-box-violet',
  },
  {
    icon: <PrivacyIcon />,
    title: 'Privacy',
    desc: 'Your health data is encrypted, never sold, and always under your control. We follow HIPAA-aware design principles throughout.',
    color: 'ss-icon-box-indigo',
  },
  {
    icon: <IntegrityIcon />,
    title: 'Medical Integrity',
    desc: 'Our AI models are reviewed by healthcare professionals. We complement medical advice — we never try to replace it.',
    color: 'ss-icon-box-teal',
  },
];

const AboutPage = () => {
  return (
    <>
      <Navbar />

      {/* ─── Mission Section ─── */}
      <section style={{ paddingTop: '7rem', paddingBottom: '5rem' }}>
        <div className="ss-container">
          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '4rem', alignItems: 'center' }}>
            <div>
              <span className="ss-section-label">Our Mission</span>
              <h2 className="ss-section-title" style={{ marginBottom: '1.5rem' }}>
                Making Health Intelligence <span className="ss-highlight">Accessible to Everyone</span>
              </h2>
              <p style={{ fontFamily: 'var(--font-body)', fontWeight: 300, fontSize: '1rem', color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1.25rem' }}>
                SymptoSense was born from a simple observation: people deserve to understand their health before it becomes a crisis. Too often, symptoms go unaddressed because accessing medical guidance feels overwhelming, expensive, or inaccessible.
              </p>
              <p style={{ fontFamily: 'var(--font-body)', fontWeight: 300, fontSize: '1rem', color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1.25rem' }}>
                We're building an AI-powered platform that bridges the gap between how you feel and what you should do about it — drawing from modern medicine, traditional systems like Ayurveda and Homeopathy, and evidence-based lifestyle interventions.
              </p>
              <p style={{ fontFamily: 'var(--font-body)', fontWeight: 300, fontSize: '1rem', color: 'var(--text-muted)', lineHeight: 1.8 }}>
                Our goal is not to replace your doctor. It's to help you walk into that appointment better informed, with clearer questions, and a deeper understanding of your own body.
              </p>
            </div>
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <img
                src="https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=500&h=500&fit=crop&q=80"
                alt="Medical team collaborating in a modern clinical environment"
                className="ss-img ss-img-glow"
                style={{ width: '100%', maxWidth: 440, height: 440, objectFit: 'cover' }}
                loading="lazy"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Responsive */}
      <style>{`
        @media (max-width: 768px) {
          .ss-container > div[style*="grid-template-columns: 1.2fr 1fr"] {
            display: flex !important;
            flex-direction: column !important;
          }
        }
      `}</style>

      {/* ─── Values Grid ─── */}
      <section style={{ padding: '5rem 0' }}>
        <div className="ss-container">
          <div className="ss-section-header-center" style={{ marginBottom: '3.5rem' }}>
            <span className="ss-section-label">Our Values</span>
            <h2 className="ss-section-title">
              Built on <span className="ss-highlight">Principles That Matter</span>
            </h2>
            <p className="ss-section-subtitle">
              Every decision we make is guided by four non-negotiable values that define who we are.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
            {values.map((v) => (
              <div key={v.title} className="ss-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div className={`ss-icon-box ${v.color}`}>
                  {v.icon}
                </div>
                <h3 style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '1.1rem', color: 'var(--text-primary)' }}>
                  {v.title}
                </h3>
                <p style={{ fontFamily: 'var(--font-body)', fontWeight: 300, fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.7 }}>
                  {v.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Responsive values grid */}
      <style>{`
        @media (max-width: 640px) {
          .ss-container > div[style*="grid-template-columns: repeat(2, 1fr)"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>

      {/* ─── Disclaimer ─── */}
      <section style={{ padding: '3rem 0 5rem' }}>
        <div className="ss-container">
          <div className="ss-disclaimer">
            <h3 style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '1.1rem', color: 'var(--warning)', marginBottom: '0.75rem' }}>
              ⚠️ Important Medical Disclaimer
            </h3>
            <p style={{ fontFamily: 'var(--font-body)', fontWeight: 400, fontSize: '0.92rem', color: 'var(--text-primary)', lineHeight: 1.8, marginBottom: '0.75rem' }}>
              SymptoSense is designed for <strong>educational and informational purposes only</strong>. It does not provide medical diagnoses, treatment plans, or prescriptions.
            </p>
            <p style={{ fontFamily: 'var(--font-body)', fontWeight: 400, fontSize: '0.92rem', color: 'var(--text-primary)', lineHeight: 1.8, marginBottom: '0.75rem' }}>
              The AI-generated assessments are based on statistical models and publicly available medical information. They should <strong>never be used as a substitute</strong> for professional medical advice, diagnosis, or treatment.
            </p>
            <p style={{ fontFamily: 'var(--font-body)', fontWeight: 400, fontSize: '0.92rem', color: 'var(--text-muted)', lineHeight: 1.8 }}>
              Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. If you think you may have a medical emergency, call your doctor, go to the emergency department, or call emergency services immediately.
            </p>
          </div>
        </div>
      </section>

      <LandingFooter />
    </>
  );
};

export default AboutPage;
