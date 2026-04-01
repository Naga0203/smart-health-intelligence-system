// ============================================================================
// Sidebar Component - Responsive Design
// ============================================================================

import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Box,
  useMediaQuery,
  useTheme,
  alpha
} from '@mui/material';
import {
  Dashboard,
  Assessment,
  History,
  Person,
  LocalHospital,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const menuItems = [
  { text: 'Dashboard', icon: <Dashboard />, path: '/app/dashboard' },
  { text: 'New Assessment', icon: <Assessment />, path: '/app/assessment/new' },
  { text: 'History', icon: <History />, path: '/app/history' },
  { text: 'Diseases', icon: <LocalHospital />, path: '/app/diseases' },
  { text: 'Profile', icon: <Person />, path: '/app/profile' },
];

export const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md')); // <768px

  const handleNavigation = (path: string) => {
    navigate(path);
    // Close sidebar on mobile after navigation
    if (isMobile) {
      onClose();
    }
  };

  const drawerContent = (
    <Box role="navigation" aria-label="Main navigation">
      <Toolbar sx={{ minHeight: { xs: 56, sm: 64 } }} />
      <List sx={{ pt: { xs: 1, md: 2 }, px: 2 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleNavigation(item.path)}
              sx={{
                // Responsive padding
                py: { xs: 1.5, md: 1.25 },
                px: { xs: 2, md: 2 },
                borderRadius: 3,
                transition: 'all 0.2s',
                // Ensure proper touch target size on mobile
                minHeight: 44,
                '&:hover': {
                  backgroundColor: alpha(theme.palette.primary.main, 0.1),
                },
                '&.Mui-selected': {
                  backgroundColor: alpha(theme.palette.primary.main, 0.15),
                  color: theme.palette.primary.main,
                  fontWeight: 600,
                  boxShadow: `inset 4px 0 0 0 ${theme.palette.primary.main}`,
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.primary.main, 0.25),
                  },
                  '& .MuiListItemIcon-root': {
                    color: theme.palette.primary.main,
                  },
                },
              }}
            >
              <ListItemIcon 
                sx={{ 
                  minWidth: { xs: 40, md: 48 },
                  color: location.pathname === item.path 
                    ? theme.palette.primary.main 
                    : alpha(theme.palette.text.primary, 0.7),
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.text}
                primaryTypographyProps={{
                  fontSize: { xs: '0.875rem', md: '1rem' },
                  fontWeight: location.pathname === item.path ? 600 : 500,
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  const drawerWidth = 260; // Slightly wider for premium feel

  const glassDrawerSx = {
    background: alpha(theme.palette.background.paper, 0.5),
    backdropFilter: 'blur(24px)',
    borderRight: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    boxShadow: `4px 0 24px ${alpha(theme.palette.common.black, 0.05)}`
  };

  return (
    <>
      {/* Mobile drawer - temporary overlay */}
      <Drawer
        variant="temporary"
        open={open}
        onClose={onClose}
        ModalProps={{ 
          keepMounted: true, // Better mobile performance
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { 
            width: drawerWidth,
            boxSizing: 'border-box',
            ...glassDrawerSx
          },
        }}
      >
        {drawerContent}
      </Drawer>

      {/* Desktop drawer - persistent */}
      <Drawer
        variant="persistent"
        open={open}
        sx={{
          display: { xs: 'none', md: 'block' },
          '& .MuiDrawer-paper': { 
            width: drawerWidth,
            boxSizing: 'border-box',
            ...glassDrawerSx
          },
        }}
      >
        {drawerContent}
      </Drawer>
    </>
  );
};

