// ============================================================================
// Main App Component
// ============================================================================

import { useEffect } from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { AppRouter } from './routes';
import { useAuthStore } from './stores/authStore';
import { theme } from './theme';

function App() {
  const initialize = useAuthStore((state) => state.initialize);

  useEffect(() => {
    // Initialize Firebase auth state listener
    initialize();
  }, [initialize]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppRouter />
    </ThemeProvider>
  );
}

export default App;

