<<<<<<< HEAD
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
=======
import { useEffect, useState } from 'react';
import { Container, Grid, Typography, Box, useTheme } from '@mui/material';
import { useAssessmentStore } from '@/stores/assessmentStore';
>>>>>>> d205e2c3b4d37e237e6680a1b659b923cf7962e9

/* ────── SVG Icons ────── */
const DashIcon = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="6" height="6" rx="1"/><rect x="11" y="3" width="6" height="6" rx="1"/><rect x="3" y="11" width="6" height="6" rx="1"/><rect x="11" y="11" width="6" height="6" rx="1"/></svg>
);
const AnalyzeIcon = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M3 10h3l2-5 3 10 2-5 2 2h2"/></svg>
);
const HistoryIcon = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="10" cy="10" r="7"/><path d="M10 6v4l3 2"/></svg>
);
const SettingsIcon = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="10" cy="10" r="3"/><path d="M10 1v3m0 12v3m-7-9H0m20 0h-3m-1.3-5.7l2.1-2.1M2.2 17.8l2.1-2.1m0-11.4L2.2 2.2m15.6 15.6l-2.1-2.1"/></svg>
);
const LogoutIcon = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M7 17H4a1 1 0 01-1-1V4a1 1 0 011-1h3M14 14l3-3-3-3M8 10h9"/></svg>
);
const HeartbeatLogo = () => (
  <svg width="24" height="24" viewBox="0 0 28 28" fill="none"><path d="M5 14h4l2-5 3 10 2-7 2 4h5" stroke="url(#db_hb)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" fill="none"/><defs><linearGradient id="db_hb" x1="0" y1="0" x2="28" y2="28"><stop stopColor="#0ea5e9"/><stop offset="1" stopColor="#7c3aed"/></linearGradient></defs></svg>
);

/* ────── Mock Data ────── */
const mockAssessments = [
  { id: 1, date: '2026-03-28', symptoms: 'Persistent headache, mild fatigue', risk: 'Moderate', system: 'Modern Medicine' },
  { id: 2, date: '2026-03-25', symptoms: 'Stomach discomfort, nausea', risk: 'Low', system: 'Ayurveda' },
  { id: 3, date: '2026-03-22', symptoms: 'Joint pain in knees, stiffness', risk: 'Moderate', system: 'Homeopathy' },
  { id: 4, date: '2026-03-18', symptoms: 'Seasonal allergies, sneezing', risk: 'Low', system: 'Lifestyle' },
  { id: 5, date: '2026-03-14', symptoms: 'Chest tightness, shortness of breath', risk: 'High', system: 'Modern Medicine' },
];

<<<<<<< HEAD
const chartData = [
  { date: 'Mar 10', score: 35 },
  { date: 'Mar 14', score: 72 },
  { date: 'Mar 18', score: 25 },
  { date: 'Mar 22', score: 48 },
  { date: 'Mar 25', score: 30 },
  { date: 'Mar 28', score: 45 },
];
=======
/**
 * Dashboard overview page
 * Displays recent assessments, system status, user statistics, and quick actions
 */
export default function DashboardPage() {
  const { fetchAssessmentHistory, assessmentHistory, loading: assessmentsLoading } = useAssessmentStore();
  const theme = useTheme();
>>>>>>> d205e2c3b4d37e237e6680a1b659b923cf7962e9

const DashboardPage = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
<<<<<<< HEAD
      await logout();
      navigate('/');
    } catch (e) { /* handled in store */ }
=======
      // Try to get data from the most recent assessment
      const recentAssessment = assessmentHistory?.assessments?.[0];

      if (!recentAssessment || !recentAssessment.symptoms || recentAssessment.symptoms.length === 0) {
        setPredictionsError('No recent assessment data available. Complete an assessment first.');
        setPredictions(null);
        return;
      }

      // Use data from recent assessment
      const result = await apiService.getTopPredictions(
        recentAssessment.symptoms,
        30, // Default age if not available
        'other', // Default gender if not available
        n
      );

      setPredictions(result.predictions || []);
    } catch (error: any) {
      console.error('Error fetching top predictions:', error);
      setPredictionsError(error.response?.data?.message || 'Failed to fetch predictions');
      setPredictions(null);
    } finally {
      setPredictionsLoading(false);
    }
>>>>>>> d205e2c3b4d37e237e6680a1b659b923cf7962e9
  };

  const greeting = (() => {
    const h = new Date().getHours();
    if (h < 12) return 'Good morning';
    if (h < 18) return 'Good afternoon';
    return 'Good evening';
  })();

  const riskBadge = (risk: string) => {
    const cls = risk === 'High' ? 'ss-badge-high' : risk === 'Moderate' ? 'ss-badge-moderate' : 'ss-badge-low';
    return <span className={`ss-badge ${cls}`}>{risk}</span>;
  };

  return (
<<<<<<< HEAD
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* ── Sidebar ── */}
      <aside className="ss-sidebar">
        <Link to="/" className="ss-sidebar-logo">
          <HeartbeatLogo />
          <span>SymptoSense</span>
        </Link>

        <nav className="ss-sidebar-nav">
          <Link to="/app/dashboard" className="ss-sidebar-link ss-sidebar-active">
            <DashIcon /> Dashboard
          </Link>
          <Link to="/analyze" className="ss-sidebar-link">
            <AnalyzeIcon /> Analyze
          </Link>
          <Link to="/app/history" className="ss-sidebar-link">
            <HistoryIcon /> History
          </Link>
          <Link to="/app/profile" className="ss-sidebar-link">
            <SettingsIcon /> Settings
          </Link>

          <div className="ss-sidebar-bottom">
            <button onClick={handleLogout} className="ss-sidebar-link" style={{ width: '100%', textAlign: 'left', background: 'none', border: 'none', cursor: 'pointer' }}>
              <LogoutIcon /> Sign Out
            </button>
          </div>
        </nav>
      </aside>

      {/* ── Main Content ── */}
      <main className="ss-dash-main">
        <div style={{ maxWidth: 1000, margin: '0 auto' }}>
          {/* Header */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: '1.6rem', color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
                {greeting}, {user?.displayName || 'there'}
              </h1>
              <p style={{ fontFamily: 'var(--font-body)', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
              </p>
            </div>
            <Link to="/analyze" className="ss-btn-primary">
              New Analysis
            </Link>
          </div>

          {/* Stats Row */}
          <div className="ss-metric-grid" style={{ marginBottom: '2rem' }}>
            {[
              { label: 'Total Assessments', value: '12', sub: '+2 this week' },
              { label: 'Last Risk Level', value: 'Moderate', sub: 'March 28' },
              { label: 'Streak Days', value: '7', sub: 'Consecutive usage' },
              { label: 'Reports Saved', value: '9', sub: '75% save rate' },
            ].map((m) => (
              <div key={m.label} className="ss-card" style={{ padding: '1.25rem' }}>
                <div style={{ fontFamily: 'var(--font-body)', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>{m.label}</div>
                <div style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: '1.5rem', color: 'var(--text-primary)', marginBottom: '0.25rem' }}>{m.value}</div>
                <div style={{ fontFamily: 'var(--font-body)', fontSize: '0.72rem', color: 'var(--text-muted)' }}>{m.sub}</div>
              </div>
            ))}
          </div>

          {/* Recent Assessments */}
          <div className="ss-card" style={{ marginBottom: '2rem', padding: '0', overflow: 'hidden' }}>
            <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <h2 style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '1.05rem', color: 'var(--text-primary)' }}>Recent Assessments</h2>
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table className="ss-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Symptoms</th>
                    <th>Risk Level</th>
                    <th>Treatment</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {mockAssessments.map(a => (
                    <tr key={a.id}>
                      <td style={{ whiteSpace: 'nowrap' }}>{a.date}</td>
                      <td style={{ maxWidth: 260, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{a.symptoms}</td>
                      <td>{riskBadge(a.risk)}</td>
                      <td>{a.system}</td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <button className="ss-btn-outline ss-btn-sm" type="button">View</button>
                          <button className="ss-btn-outline ss-btn-sm" type="button" style={{ borderColor: 'rgba(239,68,68,0.3)', color: 'var(--danger)' }}>Delete</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Health Trend Chart */}
          <div className="ss-card" style={{ padding: '1.5rem' }}>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '1.05rem', color: 'var(--text-primary)', marginBottom: '1.5rem' }}>Health Trend</h2>
            <div style={{ width: '100%', height: 260 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis dataKey="date" stroke="rgba(200,210,240,0.4)" tick={{ fontFamily: 'DM Sans', fontSize: 12 }} />
                  <YAxis stroke="rgba(200,210,240,0.4)" tick={{ fontFamily: 'DM Sans', fontSize: 12 }} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{
                      background: 'rgba(5,8,15,0.95)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: 10,
                      fontFamily: 'DM Sans',
                      fontSize: 13,
                      color: '#f0f4ff',
                    }}
                    labelStyle={{ color: 'rgba(200,210,240,0.6)' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="score"
                    name="Risk Score"
                    stroke="#0ea5e9"
                    strokeWidth={2.5}
                    dot={{ fill: '#0ea5e9', r: 4, strokeWidth: 0 }}
                    activeDot={{ r: 6, fill: '#0ea5e9', stroke: 'rgba(14,165,233,0.3)', strokeWidth: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </main>
    </div>
=======
    <Box
      sx={{
        minHeight: '100vh',
        background: `linear-gradient(135deg, ${theme.palette.background.default} 0%, ${theme.palette.background.paper} 100%)`,
        py: 4,
      }}
    >
      <Container maxWidth="lg">
        <Typography variant="h4" component="h1" gutterBottom fontWeight="700">
          Dashboard
        </Typography>

        <Grid container spacing={4}>
          {/* Quick Actions */}
          <Grid size={{ xs: 12 }}>
            <QuickActions />
          </Grid>

          {/* User Statistics */}
          <Grid size={{ xs: 12, md: 6 }}>
            <UserStatistics statistics={statistics} loading={statsLoading} />
          </Grid>

          {/* Top Predictions */}
          <Grid size={{ xs: 12, md: 6 }}>
            <TopPredictions
              predictions={predictions}
              loading={predictionsLoading}
              error={predictionsError}
              onFetchPredictions={handleFetchPredictions}
              defaultN={5}
            />
          </Grid>

          {/* Recent Assessments */}
          <Grid size={{ xs: 12, md: 6 }}>
            <RecentAssessments
              assessments={assessmentHistory?.assessments || []}
              loading={assessmentsLoading}
            />
          </Grid>

        </Grid>
      </Container>
    </Box>
>>>>>>> d205e2c3b4d37e237e6680a1b659b923cf7962e9
  );
};

export default DashboardPage;
