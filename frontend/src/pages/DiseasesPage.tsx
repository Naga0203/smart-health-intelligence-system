// ============================================================================
// Diseases Page - Display supported diseases with search and filter
// ============================================================================

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  InputAdornment,
  useTheme,
  alpha,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { useSystemStore } from '@/stores/systemStore';

export default function DiseasesPage() {
  const navigate = useNavigate();
  const theme = useTheme();

  // Define store interface locally to handle types
  interface SystemStore {
    diseases: any[] | null;
    loading: boolean;
    error: string | null;
    fetchDiseases: () => Promise<void>;
  }

  const { diseases, loading, error, fetchDiseases } = useSystemStore() as unknown as SystemStore;

  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');

  // Fetch diseases on mount
  useEffect(() => {
    if (!diseases) {
      fetchDiseases();
    }
  }, [diseases, fetchDiseases]);

  // Extract unique categories from diseases
  const categories = diseases
    ? ['all', ...new Set(diseases.map((d: any) => d.category).filter(Boolean))]
    : ['all'];

  // Filter diseases based on search and category
  const filteredDiseases = diseases
    ? diseases.filter((disease: any) => {
      const matchesSearch = disease.name
        ? disease.name.toLowerCase().includes(searchQuery.toLowerCase())
        : false;
      const matchesCategory =
        categoryFilter === 'all' || disease.category === categoryFilter;
      return matchesSearch && matchesCategory;
    })
    : [];

  // Handle assess risk button click
  const handleAssessRisk = (disease: any) => {
    // Navigate to new assessment page with pre-filled symptoms
    navigate('/app/assessment/new', {
      state: {
        prefilledSymptoms: disease.symptoms || [],
        diseaseContext: disease.name,
      },
    });
  };

  // Handle view treatments button click
  const handleViewTreatments = (disease: any) => {
    navigate(`/app/diseases/${encodeURIComponent(disease.name)}/treatment`);
  };

  if (loading && !diseases) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Box 
      sx={{ 
        minHeight: '100vh', 
        pb: 8,
        background: `linear-gradient(135deg, ${theme.palette.background.default} 0%, ${theme.palette.background.paper} 100%)`, 
      }}
    >
      <Container maxWidth="lg" sx={{ py: 4, position: 'relative', zIndex: 1 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700, color: theme.palette.text.primary }}>
          Supported Diseases
        </Typography>
        <Typography variant="body1" sx={{ color: theme.palette.text.secondary, mb: 4 }}>
          Explore the diseases our system can assess. Click "Assess Risk" to start an
          assessment with pre-filled symptoms.
        </Typography>

        {/* Search and Filter Controls */}
        <Box 
          sx={{ 
            mb: 4, 
            display: 'flex', 
            gap: 2, 
            flexWrap: 'wrap',
            p: 3,
            borderRadius: 4,
            background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.4)} 0%, ${alpha(theme.palette.background.paper, 0.1)} 100%)`,
            backdropFilter: 'blur(10px)',
            border: '1px solid',
            borderColor: alpha(theme.palette.divider, 0.2),
            boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.05)}`,
          }}
        >
          <TextField
            placeholder="Search diseases..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            sx={{ 
              flexGrow: 1, 
              minWidth: '250px',
              '& .MuiOutlinedInput-root': {
                background: alpha(theme.palette.background.paper, 0.5),
                borderRadius: 2,
              }
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
            }}
          />

          <FormControl sx={{ minWidth: '200px' }}>
            <InputLabel>Category</InputLabel>
            <Select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              label="Category"
              sx={{
                background: alpha(theme.palette.background.paper, 0.5),
                borderRadius: 2,
              }}
            >
              {categories.map((category: any) => (
                <MenuItem key={category as string} value={category as string}>
                  {category === 'all' ? 'All Categories' : category}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

      {/* Disease Grid */}
      {filteredDiseases.length === 0 ? (
        <Alert severity="info">
          No diseases found matching your search criteria.
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {filteredDiseases.map((disease: any) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={disease.name}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  borderRadius: 4,
                  background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.4)} 0%, ${alpha(theme.palette.background.paper, 0.1)} 100%)`,
                  backdropFilter: 'blur(10px)',
                  border: '1px solid',
                  borderColor: alpha(theme.palette.divider, 0.2),
                  transition: 'all 0.3s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: `0 12px 40px ${alpha(theme.palette.primary.main, 0.15)}`,
                    borderColor: alpha(theme.palette.primary.main, 0.3),
                  },
                }}
              >
                <CardContent sx={{ flexGrow: 1, p: 3 }}>
                  <Typography variant="h6" component="h2" gutterBottom sx={{ fontWeight: 600 }}>
                    {disease.name}
                  </Typography>

                  {disease.category && (
                    <Chip
                      label={disease.category}
                      size="small"
                      sx={{ 
                        mb: 2,
                        background: alpha(theme.palette.primary.main, 0.1),
                        color: theme.palette.primary.main,
                        fontWeight: 600,
                        border: 'none',
                      }}
                    />
                  )}

                  {disease.symptoms && disease.symptoms.length > 0 && (
                    <>
                      <Typography variant="subtitle2" sx={{ color: theme.palette.text.secondary, mb: 1.5, fontWeight: 600 }}>
                        Common Symptoms:
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {disease.symptoms.slice(0, 5).map((symptom: any, index: number) => (
                          <Chip
                            key={index}
                            label={symptom}
                            size="small"
                            variant="outlined"
                            sx={{
                              borderColor: alpha(theme.palette.text.primary, 0.1),
                              background: 'transparent',
                            }}
                          />
                        ))}
                        {disease.symptoms.length > 5 && (
                          <Chip
                            label={`+${disease.symptoms.length - 5} more`}
                            size="small"
                            variant="outlined"
                            sx={{
                              borderColor: alpha(theme.palette.text.primary, 0.1),
                              background: 'transparent',
                            }}
                          />
                        )}
                      </Box>
                    </>
                  )}
                </CardContent>

                <CardActions sx={{ p: 3, pt: 0, gap: 1 }}>
                  <Button
                    size="small"
                    variant="contained"
                    onClick={() => handleAssessRisk(disease)}
                    fullWidth
                    sx={{
                      borderRadius: 2,
                      textTransform: 'none',
                      fontWeight: 600,
                      boxShadow: `0 4px 14px ${alpha(theme.palette.primary.main, 0.4)}`,
                    }}
                  >
                    Assess Risk
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => handleViewTreatments(disease)}
                    fullWidth
                    sx={{
                      borderRadius: 2,
                      textTransform: 'none',
                      fontWeight: 600,
                      borderColor: alpha(theme.palette.primary.main, 0.5),
                    }}
                  >
                    Treatments
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
      </Container>
    </Box>
  );
}
