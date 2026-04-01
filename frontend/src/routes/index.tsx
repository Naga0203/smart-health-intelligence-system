// ============================================================================
// Application Routes
// ============================================================================

import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { AppLayout } from '@/components/layout/AppLayout';
import { GlobalLayout } from '@/components/layout/GlobalLayout';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';

// Eagerly load critical routes
import { LandingPage } from '@/pages/LandingPage';
import { LoginPage } from '@/pages/LoginPage';
import { RegisterPage } from '@/pages/RegisterPage';

// Lazy load pages
const AnalyzePage = lazy(() => import('@/pages/AnalyzePage'));
const AboutPage = lazy(() => import('@/pages/AboutPage'));
const DashboardPage = lazy(() => import('@/pages/DashboardPage'));
const ProfilePage = lazy(() => import('@/pages/ProfilePage').then(module => ({ default: module.ProfilePage })));
const UploadReportPage = lazy(() => import('@/pages/UploadReportPage'));
const AssessmentResultsPage = lazy(() => import('@/pages/AssessmentResultsPage'));
const DiseasesPage = lazy(() => import('@/pages/DiseasesPage'));
const NewAssessmentPage = lazy(() => import('@/pages/NewAssessmentPage'));
const AssessmentHistoryPage = lazy(() => import('@/pages/AssessmentHistoryPage').then(module => ({ default: module.AssessmentHistoryPage })));
const TreatmentExplorationPage = lazy(() => import('@/pages/TreatmentExplorationPage'));

export function AppRouter() {
  return (
    <BrowserRouter>
      <GlobalLayout>
        <Suspense fallback={<LoadingSkeleton />}>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/analyze" element={<AnalyzePage />} />
            <Route path="/about" element={<AboutPage />} />

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
              <Route path="diseases/:diseaseId/treatment" element={<TreatmentExplorationPage />} />
            </Route>

            {/* Catch-all redirect */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </GlobalLayout>
    </BrowserRouter>
  );
}
