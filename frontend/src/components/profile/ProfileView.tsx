// ============================================================================
// ProfileView Component - Display user profile information
// ============================================================================

import { Box, Card, CardContent, Typography, Grid, Chip, Button, Avatar, Divider, Tabs, Tab, Paper, useTheme, alpha } from '@mui/material';
import { Edit as EditIcon, Person as PersonIcon, LocalHospital as HospitalIcon, CheckCircle as CheckCircleIcon, CalendarToday as CalendarIcon, Phone as PhoneIcon, MedicalInformation as MedicalIcon } from '@mui/icons-material';
import { useState } from 'react';

interface ProfileViewProps {
  profile: any;
  onEdit: () => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function CustomTabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`profile-tabpanel-${index}`}
      aria-labelledby={`profile-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export function ProfileView({ profile, onEdit }: ProfileViewProps) {
  const theme = useTheme();
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (!profile) {
    return null;
  }

  const glassCardSx = {
    background: alpha(theme.palette.background.paper, 0.7),
    backdropFilter: 'blur(16px)',
    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    boxShadow: `0 8px 32px 0 ${alpha(theme.palette.common.black, 0.05)}`,
    borderRadius: 4,
    overflow: 'hidden',
  };

  const gradientHeaderSx = {
    background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)} 0%, ${alpha(theme.palette.secondary.main, 0.05)} 100%)`,
    p: { xs: 3, sm: 5 },
    display: 'flex',
    flexDirection: { xs: 'column', sm: 'row' },
    alignItems: 'center',
    gap: 4,
    position: 'relative' as const,
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      {/* Header Card */}
      <Card sx={glassCardSx} elevation={0}>
        <Box sx={gradientHeaderSx}>
          <Box sx={{ position: 'absolute', top: 16, right: 16 }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<EditIcon />}
              onClick={onEdit}
              sx={{ borderRadius: 2, textTransform: 'none', boxShadow: 2, display: { xs: 'none', sm: 'flex' } }}
            >
              Edit Profile
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={onEdit}
              sx={{ borderRadius: 2, minWidth: 0, p: 1, display: { xs: 'flex', sm: 'none' } }}
            >
              <EditIcon />
            </Button>
          </Box>
          
          <Avatar 
            sx={{ 
              width: { xs: 100, sm: 130 }, 
              height: { xs: 100, sm: 130 }, 
              bgcolor: theme.palette.primary.main,
              fontSize: '3rem',
              boxShadow: `0 8px 24px 0 ${alpha(theme.palette.primary.main, 0.3)}`,
              border: `4px solid ${theme.palette.background.paper}`
            }}
          >
            {profile.display_name ? profile.display_name.charAt(0).toUpperCase() : <PersonIcon fontSize="large" />}
          </Avatar>
          
          <Box sx={{ textAlign: { xs: 'center', sm: 'left' } }}>
            <Typography variant="h3" fontWeight="bold" gutterBottom sx={{ fontSize: { xs: '2rem', sm: '2.5rem' } }}>
              {profile.display_name || 'Anonymous User'}
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', justifyContent: { xs: 'center', sm: 'flex-start' }, gap: 1, mb: 2 }}>
               {profile.email} 
               {profile.email_verified && <CheckCircleIcon color="success" fontSize="small" titleAccess="Verified" />}
            </Typography>
            
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5, justifyContent: { xs: 'center', sm: 'flex-start' } }}>
              {profile.gender && (
                <Chip size="medium" label={profile.gender.charAt(0).toUpperCase() + profile.gender.slice(1)} variant="outlined" sx={{ borderRadius: 1.5 }} />
              )}
              {profile.date_of_birth && (
                <Chip size="medium" icon={<CalendarIcon fontSize="small"/>} label={profile.date_of_birth} variant="outlined" sx={{ borderRadius: 1.5 }} />
              )}
              <Chip size="medium" label="Member" color="primary" variant="filled" sx={{ borderRadius: 1.5, fontWeight: 'bold' }} />
            </Box>
          </Box>
        </Box>
      </Card>

      {/* Main Content Area with Tabs */}
      <Card sx={glassCardSx} elevation={0}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', px: { xs: 1, sm: 3 }, pt: 2, bgcolor: alpha(theme.palette.background.paper, 0.4) }}>
          <Tabs 
             value={tabValue} 
             onChange={handleTabChange} 
             aria-label="profile tabs"
             variant="scrollable"
             scrollButtons="auto"
             sx={{ 
               '& .MuiTab-root': { py: 2, minHeight: 64 } 
             }}
          >
             <Tab icon={<PersonIcon />} iconPosition="start" label="Personal Info" sx={{ textTransform: 'none', fontWeight: 'bold', fontSize: '1rem', letterSpacing: '0.01em' }} />
             <Tab icon={<MedicalIcon />} iconPosition="start" label="Medical History" sx={{ textTransform: 'none', fontWeight: 'bold', fontSize: '1rem', letterSpacing: '0.01em' }} />
          </Tabs>
        </Box>
        
        <CardContent sx={{ p: { xs: 2, sm: 4 } }}>
           <CustomTabPanel value={tabValue} index={0}>
              <Grid container spacing={4}>
                 <Grid size={{ xs: 12, md: 6 }}>
                    <Box sx={{ mb: 4 }}>
                       <Typography variant="overline" color="text.secondary" fontWeight="bold" letterSpacing="0.1em">Contact Details</Typography>
                       
                       <Box sx={{ display: 'flex', alignItems: 'center', mt: 3, gap: 2.5 }}>
                          <Avatar sx={{ bgcolor: alpha(theme.palette.primary.main, 0.1), color: 'primary.main', width: 50, height: 50, borderRadius: 3 }}>
                             <PhoneIcon />
                          </Avatar>
                          <Box>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>Phone Number</Typography>
                            <Typography variant="body1" fontWeight="medium" fontSize="1.1rem">{profile.phone_number || 'Not provided'}</Typography>
                          </Box>
                       </Box>
                    </Box>
                    <Divider sx={{ my: 3, opacity: 0.6 }} />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                       <Box>
                         <Typography variant="caption" color="text.secondary" fontWeight="bold">Account Created</Typography>
                         <Typography variant="body2" mt={0.5}>{new Date(profile.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}</Typography>
                       </Box>
                       <Box>
                         <Typography variant="caption" color="text.secondary" fontWeight="bold">Last Updated</Typography>
                         <Typography variant="body2" mt={0.5}>{new Date(profile.updated_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}</Typography>
                       </Box>
                    </Box>
                 </Grid>
              </Grid>
           </CustomTabPanel>
           
           <CustomTabPanel value={tabValue} index={1}>
              <Grid container spacing={3}>
                <Grid size={{ xs: 12 }}>
                  <Paper elevation={0} sx={{ p: 4, bgcolor: alpha(theme.palette.background.default, 0.4), borderRadius: 3, border: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
                    <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1.5, color: 'primary.main' }}>
                       <HospitalIcon /> Pre-existing Conditions
                    </Typography>
                    {profile.medical_history && profile.medical_history.length > 0 ? (
                      <Box display="flex" flexWrap="wrap" gap={1.5} mt={3}>
                        {profile.medical_history.map((condition: string, index: number) => (
                          <Chip key={index} label={condition} color="primary" variant="outlined" sx={{ borderRadius: 1.5, px: 1, py: 2.5, fontWeight: 'medium' }} />
                        ))}
                      </Box>
                    ) : (
                       <Typography variant="body1" color="text.secondary" mt={2} fontStyle="italic">No medical history recorded.</Typography>
                    )}
                  </Paper>
                </Grid>
                
                <Grid size={{ xs: 12, md: 6 }}>
                  <Paper elevation={0} sx={{ p: 4, bgcolor: alpha(theme.palette.background.default, 0.4), borderRadius: 3, border: `1px solid ${alpha(theme.palette.divider, 0.1)}`, height: '100%' }}>
                    <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ color: 'warning.main' }}>Allergies</Typography>
                    {profile.allergies && profile.allergies.length > 0 ? (
                      <Box display="flex" flexWrap="wrap" gap={1.5} mt={3}>
                        {profile.allergies.map((allergy: string, index: number) => (
                          <Chip key={index} label={allergy} color="warning" sx={{ borderRadius: 1.5, px: 1, py: 2.5, fontWeight: 'medium' }} />
                        ))}
                      </Box>
                    ) : (
                       <Typography variant="body1" color="text.secondary" mt={2} fontStyle="italic">No allergies recorded.</Typography>
                    )}
                  </Paper>
                </Grid>
                
                <Grid size={{ xs: 12, md: 6 }}>
                  <Paper elevation={0} sx={{ p: 4, bgcolor: alpha(theme.palette.background.default, 0.4), borderRadius: 3, border: `1px solid ${alpha(theme.palette.divider, 0.1)}`, height: '100%' }}>
                    <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ color: 'info.main' }}>Current Medications</Typography>
                    {profile.current_medications && profile.current_medications.length > 0 ? (
                      <Box display="flex" flexWrap="wrap" gap={1.5} mt={3}>
                        {profile.current_medications.map((medication: string, index: number) => (
                          <Chip key={index} label={medication} color="info" sx={{ borderRadius: 1.5, px: 1, py: 2.5, fontWeight: 'medium' }} />
                        ))}
                      </Box>
                    ) : (
                       <Typography variant="body1" color="text.secondary" mt={2} fontStyle="italic">No current medications.</Typography>
                    )}
                  </Paper>
                </Grid>
              </Grid>
           </CustomTabPanel>
        </CardContent>
      </Card>
    </Box>
  );
}
