// ============================================================================
// React Router Configuration
// ============================================================================

import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { AppLayout } from '@/components/layout/AppLayout';

// Pages (will be created)
import { LandingPage } from '@/pages/LandingPage';
import { LoginPage } from '@/pages/LoginPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { NewAssessmentPage } from '@/pages/NewAssessmentPage';
import { AssessmentResultsPage } from '@/pages/AssessmentResultsPage';
import { AssessmentHistoryPage } from '@/pages/AssessmentHistoryPage';
import { ProfilePage } from '@/pages/ProfilePage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <LandingPage />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/app',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'assessment/new',
        element: <NewAssessmentPage />,
      },
      {
        path: 'assessment/:id',
        element: <AssessmentResultsPage />,
      },
      {
        path: 'history',
        element: <AssessmentHistoryPage />,
      },
      {
        path: 'profile',
        element: <ProfilePage />,
      },
    ],
  },
]);

export const AppRouter = () => {
  return <RouterProvider router={router} />;
};
