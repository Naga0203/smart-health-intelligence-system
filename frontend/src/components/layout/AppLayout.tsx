// ============================================================================
// App Layout Component - Responsive Design with Keyboard Navigation
// ============================================================================

import { Outlet } from 'react-router-dom';
import { Box, Container, useMediaQuery, useTheme } from '@mui/material';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { useState, useEffect } from 'react';
import { useKeyboardShortcuts } from '@/hooks';

export const AppLayout = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md')); // <768px
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg')); // 768-1024px
  
  // Enable global keyboard shortcuts
  useKeyboardShortcuts();
  
  // Sidebar should be closed by default on mobile, open on desktop
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);

  // Update sidebar state when screen size changes
  useEffect(() => {
    setSidebarOpen(!isMobile);
  }, [isMobile]);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', flexDirection: 'column' }}>
      <Header onMenuClick={toggleSidebar} />
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <Box
        component="main"
        role="main"
        aria-label="Main content"
        id="main-content"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          // Responsive padding
          p: { xs: 2, sm: 2, md: 3 },
          // Responsive top margin for fixed header
          mt: { xs: 7, sm: 8 },
          // Responsive left margin for sidebar
          ml: {
            xs: 0, // No margin on mobile (sidebar is overlay)
            md: sidebarOpen ? '240px' : 0, // Margin on desktop when sidebar is open
          },
          transition: theme.transitions.create(['margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          // Ensure content doesn't get too wide on large screens
          maxWidth: '100%',
        }}
      >
        <Container 
          maxWidth="xl" 
          sx={{ 
            flexGrow: 1,
            px: { xs: 0, sm: 2, md: 3 },
          }}
        >
          <Outlet />
        </Container>
      </Box>
    </Box>
  );
};

