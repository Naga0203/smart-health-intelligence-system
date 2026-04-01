// ============================================================================
// Header Component - Responsive Design
// ============================================================================

import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Box,
  useMediaQuery,
  useTheme,
  alpha
} from '@mui/material';
import {
  AccountCircle,
  Logout,
} from '@mui/icons-material';
import { BurgerMenu } from '../ui/BurgerMenu';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { LogoutModal } from '../common';

interface HeaderProps {
  onMenuClick: () => void;
  sidebarOpen?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onMenuClick, sidebarOpen = false }) => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm')); // <600px
  const { user, logout } = useAuthStore();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [isLogoutModalOpen, setIsLogoutModalOpen] = useState(false);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleProfile = () => {
    handleMenuClose();
    navigate('/app/profile');
  };

  const handleLogoutClick = () => {
    handleMenuClose();
    setIsLogoutModalOpen(true);
  };

  const handleConfirmLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setIsLogoutModalOpen(false);
    }
  };

  return (
    <>
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          height: { xs: 56, sm: 64 },
          background: alpha(theme.palette.background.paper, 0.4),
          backdropFilter: 'blur(24px)',
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
          color: theme.palette.text.primary,
        }}
      >
        <Toolbar
          sx={{
            minHeight: { xs: 56, sm: 64 },
            px: { xs: 1, sm: 2, md: 3 },
          }}
        >
<<<<<<< HEAD
          <Box sx={{ mr: { xs: 1, sm: 2 } }}>
            <BurgerMenu
              open={sidebarOpen}
              onClick={onMenuClick}
              aria-label="toggle menu"
            />
          </Box>
=======
          {/* Menu button uses primary color for pop */}
          <IconButton
            color="primary"
            aria-label="toggle menu"
            edge="start"
            onClick={onMenuClick}
            sx={{
              mr: { xs: 1, sm: 2 },
              minWidth: 44,
              minHeight: 44,
              backgroundColor: alpha(theme.palette.primary.main, 0.1),
              borderRadius: 2,
              '&:hover': {
                backgroundColor: alpha(theme.palette.primary.main, 0.2),
              }
            }}
          >
            <MenuIcon />
          </IconButton>
>>>>>>> d205e2c3b4d37e237e6680a1b659b923cf7962e9

          <Typography
            variant="h6"
            component="div"
            fontWeight="bold"
            sx={{
              flexGrow: 1,
              fontSize: { xs: '1rem', sm: '1.25rem' },
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              display: 'flex',
              alignItems: 'center',
              background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            {isMobile ? 'Health AI' : 'AI Health Intelligence'}
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 0.5, sm: 1 } }}>
            {!isMobile && (
              <Typography
                variant="body2"
                fontWeight="500"
                sx={{
                  maxWidth: { sm: 150, md: 200 },
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {user?.displayName || user?.email}
              </Typography>
            )}

            <IconButton
              onClick={handleMenuOpen}
              aria-label="user menu"
              color="inherit"
              sx={{
                minWidth: 44,
                minHeight: 44,
                ml: 1,
              }}
            >
              {user?.photoURL ? (
                <Avatar
                  src={user.photoURL}
                  sx={{ 
                    width: { xs: 32, sm: 36 }, 
                    height: { xs: 32, sm: 36 },
                    border: `2px solid ${theme.palette.primary.main}`
                  }}
                  alt={user?.displayName || 'User avatar'}
                />
              ) : (
                <Avatar 
                  sx={{ 
                    width: { xs: 32, sm: 36 }, 
                    height: { xs: 32, sm: 36 },
                    bgcolor: alpha(theme.palette.primary.main, 0.2),
                    color: theme.palette.primary.main,
                    border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`
                  }}
                >
                  <AccountCircle />
                </Avatar>
              )}
            </IconButton>
          </Box>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            PaperProps={{
              sx: {
                mt: 1.5,
                background: alpha(theme.palette.background.paper, 0.8),
                backdropFilter: 'blur(20px)',
                borderRadius: 2,
                border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                boxShadow: `0 8px 32px 0 ${alpha(theme.palette.common.black, 0.1)}`,
              }
            }}
          >
            <MenuItem onClick={handleProfile} sx={{ py: 1.5, px: 2, borderRadius: 1, mx: 1 }}>
              <AccountCircle sx={{ mr: 1.5, color: 'text.secondary' }} />
              <Typography fontWeight="500">Profile</Typography>
            </MenuItem>
            <MenuItem onClick={handleLogoutClick} sx={{ py: 1.5, px: 2, borderRadius: 1, mx: 1, color: 'error.main' }}>
              <Logout sx={{ mr: 1.5 }} />
              <Typography fontWeight="500">Logout</Typography>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <LogoutModal
        isOpen={isLogoutModalOpen}
        onClose={() => setIsLogoutModalOpen(false)}
        onConfirm={handleConfirmLogout}
      />
    </>
  );
};

