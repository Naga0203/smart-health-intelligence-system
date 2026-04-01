import { useState } from 'react';
import { Navbar } from '@/components/landing/Navbar';
import { LandingFooter } from '@/components/landing/LandingFooter';

/* ────── SVG Icons ────── */
const CheckSvg = () => (
  <svg viewBox="0 0 20 20" fill="currentColor" style={{ width: 16, height: 16 }}>
    <path fillRule="evenodd" d="M16.7 5.3a1 1 0 010 1.4l-8 8a1 1 0 01-1.4 0l-4-4a1 1 0 111.4-1.4L8 12.6l7.3-7.3a1 1 0 011.4 0z" clipRule="evenodd"/>
  </svg>
);

/* ────── Data ────── */
const durations = ['Less than a day', '1–3 days', '4–7 days', '1–2 weeks', '2–4 weeks', 'More than a month'];
const conditions = ['Diabetes', 'Hypertension', 'Asthma', 'Heart Disease', 'Thyroid Issues', 'None'];

const treatmentData: Record<string, { title: string; items: string[] }> = {
  modern: {
    title: 'Modern Medicine',
    items: [
      'Schedule an appointment with a general practitioner for clinical evaluation.',
      'Consider diagnostic blood work including CBC and metabolic panel.',
      'Over-the-counter antipyretics (e.g., acetaminophen) for symptom management.',
      'Monitor for any progression of symptoms over the next 48 hours.',
    ],
  },
  ayurveda: {
    title: 'Ayurveda',
    items: [
      'Warm water infused with ginger, tulsi, and honey for respiratory comfort.',
      'Gentle Nasya therapy (nasal oil application) for sinus-related symptoms.',
      'Light, warm meals emphasizing Kapha-balancing spices like turmeric and black pepper.',
      'Adequate rest and avoidance of cold, heavy, or fried foods.',
    ],
  },
  homeopathy: {
    title: 'Homeopathy',
    items: [
      'Aconitum napellus 30C — early onset with sudden symptoms and restlessness.',
      'Bryonia alba 30C — for symptoms that worsen with movement, with dryness.',
      'Consult a qualified homeopathic practitioner for constitutional assessment.',
      'Maintain a symptom journal to track changes in response to remedies.',
    ],
  },
  lifestyle: {
    title: 'Lifestyle',
    items: [
      'Prioritize 8–9 hours of quality sleep to support immune function.',
      'Stay hydrated — aim for at least 2.5 liters of water daily.',
      'Incorporate gentle movement like walking or yoga when energy permits.',
      'Practice stress-reduction techniques such as deep breathing or meditation.',
    ],
  },
};

/* ────── Confidence Ring Component ────── */
const ConfidenceRing = ({ score }: { score: number }) => {
  const radius = 58;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 80 ? 'var(--success)' : score >= 50 ? 'var(--warning)' : 'var(--danger)';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={radius} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8"/>
        <circle
          cx="70" cy="70" r={radius} fill="none"
          stroke={color} strokeWidth="8" strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={offset}
          transform="rotate(-90 70 70)"
          style={{ transition: 'stroke-dashoffset 1s ease-out' }}
        />
        <text x="70" y="66" textAnchor="middle" fill="var(--text-primary)" fontFamily="var(--font-heading)" fontWeight="800" fontSize="28">
          {score}%
        </text>
        <text x="70" y="86" textAnchor="middle" fill="var(--text-muted)" fontFamily="var(--font-body)" fontSize="11">
          Confidence
        </text>
      </svg>
    </div>
  );
};

/* ────── Main Component ────── */
const AnalyzePage = () => {
  const [step, setStep] = useState(1);
  const [symptoms, setSymptoms] = useState('');
  const [severity, setSeverity] = useState(5);
  const [duration, setDuration] = useState('');
  const [age, setAge] = useState('');
  const [sex, setSex] = useState('');
  const [selectedConditions, setSelectedConditions] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState('modern');

  const toggleCondition = (c: string) => {
    if (c === 'None') { setSelectedConditions(['None']); return; }
    setSelectedConditions(prev =>
      prev.includes(c) ? prev.filter(x => x !== c) : [...prev.filter(x => x !== 'None'), c]
    );
  };

  const riskLevel = severity >= 7 ? 'High' : severity >= 4 ? 'Moderate' : 'Low';
  const riskClass = severity >= 7 ? 'ss-badge-high' : severity >= 4 ? 'ss-badge-moderate' : 'ss-badge-low';
  const confidence = Math.min(95, 60 + symptoms.length / 5 + (age ? 5 : 0) + (sex ? 5 : 0));

  const steps = [
    { num: 1, label: 'Symptoms' },
    { num: 2, label: 'Demographics' },
    { num: 3, label: 'Results' },
  ];

  return (
    <>
      <Navbar />

      <section style={{ paddingTop: '7rem', paddingBottom: '5rem', minHeight: '100vh' }}>
        <div className="ss-container" style={{ maxWidth: 680, margin: '0 auto', padding: '0 2rem' }}>
          {/* Section Header */}
          <div className="ss-section-header-center" style={{ marginBottom: '2.5rem' }}>
            <span className="ss-section-label">Symptom Analyzer</span>
            <h2 className="ss-section-title">
              AI-Powered <span className="ss-highlight">Health Assessment</span>
            </h2>
          </div>

          {/* Step Indicator */}
          <div className="ss-step-indicator">
            {steps.map((s, i) => (
              <div key={s.num} style={{ display: 'flex', alignItems: 'center' }}>
                <div className="ss-step">
                  <div className={`ss-step-circle ${step === s.num ? 'ss-step-active' : step > s.num ? 'ss-step-done' : ''}`}>
                    {step > s.num ? <CheckSvg /> : s.num}
                  </div>
                  <span className="ss-step-text">{s.label}</span>
                </div>
                {i < steps.length - 1 && (
                  <div className={`ss-step-line ${step > s.num ? 'ss-step-line-active' : ''}`}></div>
                )}
              </div>
            ))}
          </div>

          {/* Form Card */}
          <div className="ss-card" style={{ padding: '2.5rem' }}>
            {/* ── Step 1: Symptoms ── */}
            {step === 1 && (
              <div>
                <div style={{ marginBottom: '1.5rem' }}>
                  <label className="ss-label">Describe your symptoms</label>
                  <textarea
                    className="ss-textarea"
                    placeholder="Describe what you're feeling in detail — e.g., persistent headache on the right side for 3 days, mild nausea in the morning..."
                    value={symptoms}
                    onChange={(e) => setSymptoms(e.target.value)}
                    rows={5}
                  />
                </div>

                <div style={{ marginBottom: '1.5rem' }}>
                  <label className="ss-label">Severity Level: {severity}/10</label>
                  <input
                    type="range"
                    className="ss-slider"
                    min="1" max="10"
                    value={severity}
                    onChange={(e) => setSeverity(Number(e.target.value))}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--font-body)', fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                    <span>Mild</span><span>Moderate</span><span>Severe</span>
                  </div>
                </div>

                <div style={{ marginBottom: '2rem' }}>
                  <label className="ss-label">Duration</label>
                  <select
                    className="ss-select"
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                  >
                    <option value="">Select duration...</option>
                    {durations.map(d => <option key={d} value={d}>{d}</option>)}
                  </select>
                </div>

                <button
                  className="ss-btn-primary"
                  style={{ width: '100%' }}
                  onClick={() => setStep(2)}
                  disabled={!symptoms.trim()}
                >
                  Continue →
                </button>
              </div>
            )}

            {/* ── Step 2: Demographics ── */}
            {step === 2 && (
              <div>
                <div style={{ marginBottom: '1.5rem' }}>
                  <label className="ss-label">Age</label>
                  <input
                    className="ss-input"
                    type="number"
                    placeholder="Enter your age"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    min="1" max="120"
                  />
                </div>

                <div style={{ marginBottom: '1.5rem' }}>
                  <label className="ss-label">Biological Sex</label>
                  <div className="ss-toggle-group">
                    {['Male', 'Female', 'Other'].map(opt => (
                      <button
                        key={opt}
                        className={`ss-toggle-option ${sex === opt ? 'ss-toggle-active' : ''}`}
                        onClick={() => setSex(opt)}
                        type="button"
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                </div>

                <div style={{ marginBottom: '2rem' }}>
                  <label className="ss-label">Pre-existing Conditions</label>
                  <div className="ss-checkbox-group">
                    {conditions.map(c => (
                      <label key={c} className="ss-checkbox-label">
                        <input
                          type="checkbox"
                          checked={selectedConditions.includes(c)}
                          onChange={() => toggleCondition(c)}
                        />
                        {c}
                      </label>
                    ))}
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '0.75rem' }}>
                  <button className="ss-btn-outline" style={{ flex: 1 }} onClick={() => setStep(1)} type="button">
                    ← Back
                  </button>
                  <button className="ss-btn-primary" style={{ flex: 2 }} onClick={() => setStep(3)} type="button">
                    Analyze Now →
                  </button>
                </div>
              </div>
            )}

            {/* ── Step 3: Results ── */}
            {step === 3 && (
              <div>
                {/* Score + Risk */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '2.5rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
                  <ConfidenceRing score={Math.round(confidence)} />
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontFamily: 'var(--font-body)', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Risk Level</div>
                    <span className={`ss-badge ${riskClass}`} style={{ fontSize: '0.88rem', padding: '0.4rem 1.2rem' }}>
                      {riskLevel}
                    </span>
                  </div>
                </div>

                {/* Summary */}
                <div className="ss-card" style={{ marginBottom: '1.5rem', background: 'rgba(14,165,233,0.05)', borderColor: 'rgba(14,165,233,0.15)' }}>
                  <p style={{ fontFamily: 'var(--font-body)', fontSize: '0.88rem', color: 'var(--text-primary)', lineHeight: 1.7 }}>
                    <strong>Assessment Summary:</strong> Based on your reported symptoms ({symptoms.substring(0, 80)}{symptoms.length > 80 ? '...' : ''}), severity level {severity}/10, the AI analysis suggests a {riskLevel.toLowerCase()} risk assessment. Below are treatment perspectives from multiple medical systems.
                  </p>
                </div>

                {/* Treatment Tabs */}
                <div className="ss-tabs">
                  {Object.entries(treatmentData).map(([key, val]) => (
                    <button
                      key={key}
                      className={`ss-tab ${activeTab === key ? 'ss-tab-active' : ''}`}
                      onClick={() => setActiveTab(key)}
                      type="button"
                    >
                      {val.title}
                    </button>
                  ))}
                </div>

                {/* Treatment Content */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '2rem' }}>
                  {treatmentData[activeTab].items.map((item, i) => (
                    <div key={i} className="ss-card" style={{ padding: '1rem 1.25rem', display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                      <span style={{ color: 'var(--accent-teal)', marginTop: 2, flexShrink: 0 }}>
                        <svg viewBox="0 0 20 20" fill="currentColor" style={{ width: 16, height: 16 }}>
                          <circle cx="10" cy="10" r="3"/>
                        </svg>
                      </span>
                      <span style={{ fontFamily: 'var(--font-body)', fontSize: '0.88rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>
                        {item}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', gap: '0.75rem' }}>
                  <button className="ss-btn-primary" style={{ flex: 1 }} type="button">
                    Save Assessment
                  </button>
                  <button className="ss-btn-outline" style={{ flex: 1 }} onClick={() => { setStep(1); setSymptoms(''); setSeverity(5); setDuration(''); setAge(''); setSex(''); setSelectedConditions([]); }} type="button">
                    Start Over
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      <LandingFooter />
    </>
  );
};

export default AnalyzePage;
