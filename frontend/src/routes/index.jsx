// ============================================================================
// Application Routes
// ============================================================================

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Placeholder components - will be implemented in later tasks
const LandingPage = () => <div>Landing Page</div>;
const LoginPage = () => <div>Login Page</div>;
const DashboardPage = () => <div>Dashboard Page</div>;

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
