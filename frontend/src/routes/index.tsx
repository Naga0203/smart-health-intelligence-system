// ============================================================================
// Application Routes
// ============================================================================

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { AppLayout } from '@/components/layout/AppLayout';

// Import actual pages
import { LoginPage } from '@/pages/LoginPage';
import { RegisterPage } from '@/pages/RegisterPage';
import DashboardPage from '@/pages/DashboardPage';
import { ProfilePage } from '@/pages/ProfilePage';

// Placeholder components - will be implemented in later tasks
const LandingPage = () => (
  <div style={{ 
    display: 'flex', 
    flexDirection: 'column', 
    alignItems: 'center', 
    justifyContent: 'center', 
    minHeight: '100vh',
    gap: '20px',
    padding: '20px'
  }}>
    <h1>AI Health Intelligence Platform</h1>
    <p>Your personal health assessment companion</p>
    <div style={{ display: 'flex', gap: '10px' }}>
      <a href="/login" style={{ 
        padding: '10px 20px', 
        backgroundColor: '#667eea', 
        color: 'white', 
        textDecoration: 'none',
        borderRadius: '5px'
      }}>
        Sign In
      </a>
      <a href="/register" style={{ 
        padding: '10px 20px', 
        backgroundColor: '#764ba2', 
        color: 'white', 
        textDecoration: 'none',
        borderRadius: '5px'
      }}>
        Create Account
      </a>
    </div>
  </div>
);
const NewAssessmentPage = () => <div>New Assessment Page</div>;
const AssessmentResultsPage = () => <div>Assessment Results Page</div>;
const AssessmentHistoryPage = () => <div>Assessment History Page</div>;
const UploadReportPage = () => <div>Upload Report Page</div>;
const DiseasesPage = () => <div>Diseases Page</div>;

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* Protected routes with AppLayout */}
        <Route
          path="/app"
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/app/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="assessment/new" element={<NewAssessmentPage />} />
          <Route path="assessment/:id" element={<AssessmentResultsPage />} />
          <Route path="history" element={<AssessmentHistoryPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="upload" element={<UploadReportPage />} />
          <Route path="diseases" element={<DiseasesPage />} />
        </Route>
        
        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
