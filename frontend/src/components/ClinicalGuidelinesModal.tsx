/**
 * Clinical Guidelines Modal Component
 * 
 * Displays comprehensive clinical guidelines for treatment-disease combinations.
 * Fetches data from the backend AI agent and presents it in an organized format.
 * 
 * Implements Task 8: Responsive design and accessibility
 * - Responsive styling for mobile, tablet, and desktop viewports (8.1)
 * - ARIA labels and keyboard navigation support (8.2)
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  CircularProgress,
  Box,
  Typography,
  IconButton,
  Alert,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { apiService } from '@/services/api';

/**
 * Props for the ClinicalGuidelinesModal component
 */
export interface ClinicalGuidelinesModalProps {
  /** Controls modal visibility */
  open: boolean;
  /** Callback function to close the modal */
  onClose: () => void;
  /** Name of the treatment to fetch guidelines for */
  treatmentName: string;
  /** Name of the disease to fetch guidelines for */
  diseaseName: string;
}

/**
 * Clinical guidelines data structure returned from the backend
 */
export interface ClinicalGuidelinesData {
  /** Treatment mechanisms and overview */
  treatment_details: string;
  /** Disease-specific protocols and guidelines */
  disease_protocols: string;
  /** Research studies and evidence summary */
  research_evidence: string;
  /** Clinical recommendations for practitioners */
  clinical_recommendations: string;
  /** Optional dosage information and administration guidelines */
  dosage_guidelines?: string;
  /** Contraindications, warnings, and precautions */
  contraindications: string;
  /** Source citations */
  sources: string[];
  /** Medical disclaimer text */
  disclaimer: string;
}

/**
 * Internal state management for the modal
 */
export interface ModalState {
  /** True while API request is in progress */
  loading: boolean;
  /** Error message if request fails, null otherwise */
  error: string | null;
  /** Clinical guidelines data, null until loaded */
  data: ClinicalGuidelinesData | null;
}

/**
 * ClinicalGuidelinesModal Component
 * 
 * Implements subtasks 2.1, 2.3, and 2.5:
 * - Modal component with Material-UI Dialog (2.1)
 * - Loading state UI (2.3)
 * - Error state UI with retry functionality (2.5)
 */
const ClinicalGuidelinesModal: React.FC<ClinicalGuidelinesModalProps> = ({
  open,
  onClose,
  treatmentName,
  diseaseName,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));
  
  const [state, setState] = useState<ModalState>({
    loading: false,
    error: null,
    data: null,
  });

  /**
   * Fetch clinical guidelines from the backend API
   */
  const fetchGuidelines = async () => {
    setState({ loading: true, error: null, data: null });

    try {
      const response = await apiService.fetchClinicalGuidelines(treatmentName, diseaseName);

      if (response.data.success && response.data.data) {
        setState({
          loading: false,
          error: null,
          data: response.data.data,
        });
      } else {
        setState({
          loading: false,
          error: response.data.message || 'Failed to retrieve clinical guidelines',
          data: null,
        });
      }
    } catch (error: any) {
      let errorMessage = 'Unable to retrieve clinical guidelines. Please try again.';

      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        errorMessage = 'Request is taking longer than expected. Please try again.';
      } else if (error.response?.status === 504) {
        errorMessage = 'Request timeout: Clinical guidelines generation exceeded 30 seconds. Please try again.';
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (!error.response) {
        errorMessage = 'Unable to connect to server. Please check your connection and try again.';
      }

      setState({
        loading: false,
        error: errorMessage,
        data: null,
      });
    }
  };

  /**
   * Fetch guidelines when modal opens
   */
  useEffect(() => {
    if (open && treatmentName && diseaseName) {
      fetchGuidelines();
    }
  }, [open, treatmentName, diseaseName]);

  /**
   * Handle retry button click
   */
  const handleRetry = () => {
    fetchGuidelines();
  };

  /**
   * Render loading state (Subtask 2.3)
   */
  const renderLoadingState = () => (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="300px"
      gap={2}
      role="status"
      aria-live="polite"
      aria-label="Loading clinical guidelines"
    >
      <CircularProgress size={48} aria-hidden="true" />
      <Typography variant="body1" color="text.secondary">
        Loading clinical guidelines...
      </Typography>
    </Box>
  );

  /**
   * Render error state with retry functionality (Subtask 2.5)
   */
  const renderErrorState = () => (
    <Box 
      minHeight="300px" 
      display="flex" 
      flexDirection="column" 
      gap={2}
    >
      <Alert severity="error" sx={{ mb: 2 }}>
        {state.error}
      </Alert>
      <Button
        variant="contained"
        color="primary"
        onClick={handleRetry}
        sx={{ alignSelf: 'center' }}
        aria-label="Retry loading clinical guidelines"
      >
        Retry
      </Button>
    </Box>
  );

  /**
   * Render clinical guidelines content
   * Implements subtasks 3.1, 3.2, 3.4, and 3.5
   * Task 8.1: Responsive styling for different screen sizes
   */
  const renderContent = () => {
    if (!state.data) return null;

    const { data } = state;

    return (
      <Box 
        sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: { xs: 2, sm: 2.5, md: 3 },
          px: { xs: 0, sm: 0 },
        }}
      >
        {/* Treatment Details Section - Subtask 3.1 */}
        <Box>
          <Typography 
            variant="h6" 
            gutterBottom 
            sx={{ 
              fontWeight: 600, 
              color: 'primary.main',
              fontSize: { xs: '1rem', sm: '1.1rem', md: '1.25rem' },
            }}
            id="treatment-details-heading"
          >
            Treatment Details
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              whiteSpace: 'pre-line',
              fontSize: { xs: '0.875rem', sm: '0.9rem', md: '1rem' },
              lineHeight: { xs: 1.5, md: 1.6 },
            }}
            aria-labelledby="treatment-details-heading"
          >
            {data.treatment_details}
          </Typography>
        </Box>

        {/* Disease Protocols Section - Subtask 3.1 */}
        <Box>
          <Typography 
            variant="h6" 
            gutterBottom 
            sx={{ 
              fontWeight: 600, 
              color: 'primary.main',
              fontSize: { xs: '1rem', sm: '1.1rem', md: '1.25rem' },
            }}
            id="disease-protocols-heading"
          >
            Disease-Specific Protocols
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              whiteSpace: 'pre-line',
              fontSize: { xs: '0.875rem', sm: '0.9rem', md: '1rem' },
              lineHeight: { xs: 1.5, md: 1.6 },
            }}
            aria-labelledby="disease-protocols-heading"
          >
            {data.disease_protocols}
          </Typography>
        </Box>

        {/* Research Evidence Section - Subtask 3.1 */}
        <Box>
          <Typography 
            variant="h6" 
            gutterBottom 
            sx={{ 
              fontWeight: 600, 
              color: 'primary.main',
              fontSize: { xs: '1rem', sm: '1.1rem', md: '1.25rem' },
            }}
            id="research-evidence-heading"
          >
            Research Evidence
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              whiteSpace: 'pre-line',
              fontSize: { xs: '0.875rem', sm: '0.9rem', md: '1rem' },
              lineHeight: { xs: 1.5, md: 1.6 },
            }}
            aria-labelledby="research-evidence-heading"
          >
            {data.research_evidence}
          </Typography>
        </Box>

        {/* Clinical Recommendations Section - Subtask 3.1 */}
        <Box>
          <Typography 
            variant="h6" 
            gutterBottom 
            sx={{ 
              fontWeight: 600, 
              color: 'primary.main',
              fontSize: { xs: '1rem', sm: '1.1rem', md: '1.25rem' },
            }}
            id="clinical-recommendations-heading"
          >
            Clinical Recommendations
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              whiteSpace: 'pre-line',
              fontSize: { xs: '0.875rem', sm: '0.9rem', md: '1rem' },
              lineHeight: { xs: 1.5, md: 1.6 },
            }}
            aria-labelledby="clinical-recommendations-heading"
          >
            {data.clinical_recommendations}
          </Typography>
        </Box>

        {/* Dosage Guidelines Section - Subtask 3.2: Optional field rendering */}
        {data.dosage_guidelines && data.dosage_guidelines.trim() !== '' && (
          <Box>
            <Typography 
              variant="h6" 
              gutterBottom 
              sx={{ 
                fontWeight: 600, 
                color: 'primary.main',
                fontSize: { xs: '1rem', sm: '1.1rem', md: '1.25rem' },
              }}
              id="dosage-guidelines-heading"
            >
              Dosage Guidelines
            </Typography>
            <Typography 
              variant="body2" 
              sx={{ 
                whiteSpace: 'pre-line',
                fontSize: { xs: '0.875rem', sm: '0.9rem', md: '1rem' },
                lineHeight: { xs: 1.5, md: 1.6 },
              }}
              aria-labelledby="dosage-guidelines-heading"
            >
              {data.dosage_guidelines}
            </Typography>
          </Box>
        )}

        {/* Contraindications Section - Subtask 3.1 */}
        <Box>
          <Typography 
            variant="h6" 
            gutterBottom 
            sx={{ 
              fontWeight: 600, 
              color: 'warning.main',
              fontSize: { xs: '1rem', sm: '1.1rem', md: '1.25rem' },
            }}
            id="contraindications-heading"
          >
            Contraindications and Warnings
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              whiteSpace: 'pre-line',
              fontSize: { xs: '0.875rem', sm: '0.9rem', md: '1rem' },
              lineHeight: { xs: 1.5, md: 1.6 },
            }}
            aria-labelledby="contraindications-heading"
          >
            {data.contraindications}
          </Typography>
        </Box>

        {/* Sources Section - Subtask 3.4 */}
        {data.sources && data.sources.length > 0 && (
          <Box>
            <Typography 
              variant="h6" 
              gutterBottom 
              sx={{ 
                fontWeight: 600, 
                color: 'primary.main',
                fontSize: { xs: '1rem', sm: '1.1rem', md: '1.25rem' },
              }}
              id="sources-heading"
            >
              Sources
            </Typography>
            <Box 
              component="ul" 
              sx={{ 
                mt: 1, 
                pl: { xs: 1.5, sm: 2 },
                fontSize: { xs: '0.875rem', sm: '0.9rem', md: '1rem' },
              }}
              aria-labelledby="sources-heading"
            >
              {data.sources.map((source, index) => (
                <Typography 
                  component="li" 
                  variant="body2" 
                  key={index} 
                  sx={{ 
                    mb: 0.5,
                    fontSize: { xs: '0.875rem', sm: '0.9rem', md: '1rem' },
                  }}
                >
                  {source}
                </Typography>
              ))}
            </Box>
          </Box>
        )}

        {/* Medical Disclaimer Section - Subtask 3.4 */}
        <Box 
          sx={{ 
            mt: 2, 
            p: { xs: 1.5, sm: 2 }, 
            bgcolor: 'grey.100', 
            borderRadius: 1,
            border: '1px solid',
            borderColor: 'grey.300',
          }}
          role="note"
          aria-label="Medical disclaimer"
        >
          <Typography 
            variant="subtitle2" 
            gutterBottom 
            sx={{ 
              fontWeight: 600,
              fontSize: { xs: '0.875rem', sm: '0.9rem', md: '1rem' },
            }}
          >
            Medical Disclaimer
          </Typography>
          <Typography 
            variant="caption" 
            color="text.secondary" 
            sx={{ 
              whiteSpace: 'pre-line',
              fontSize: { xs: '0.75rem', sm: '0.8rem', md: '0.875rem' },
              lineHeight: { xs: 1.4, md: 1.5 },
            }}
          >
            {data.disclaimer}
          </Typography>
        </Box>
      </Box>
    );
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth={isMobile ? 'sm' : isTablet ? 'md' : 'md'}
      fullWidth
      aria-labelledby="clinical-guidelines-dialog-title"
      aria-describedby="clinical-guidelines-dialog-description"
      slotProps={{
        backdrop: {
          onClick: onClose,
        },
        paper: {
          sx: {
            maxHeight: { xs: '90vh', sm: '85vh', md: '90vh' },
            margin: { xs: 1, sm: 2 },
          },
        },
      }}
    >
      <DialogTitle 
        id="clinical-guidelines-dialog-title"
        sx={{
          fontSize: { xs: '1.1rem', sm: '1.25rem', md: '1.5rem' },
          pb: { xs: 1, sm: 1.5 },
        }}
      >
        <Box 
          display="flex" 
          alignItems="center" 
          justifyContent="space-between"
          gap={1}
        >
          <Typography 
            variant="h6" 
            component="div"
            sx={{
              fontSize: { xs: '1rem', sm: '1.1rem', md: '1.25rem' },
              fontWeight: 600,
              flex: 1,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            Clinical Guidelines: {treatmentName} for {diseaseName}
          </Typography>
          <IconButton
            aria-label="close clinical guidelines modal"
            onClick={onClose}
            sx={{
              color: (theme) => theme.palette.grey[500],
              flexShrink: 0,
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent 
        dividers
        id="clinical-guidelines-dialog-description"
        sx={{
          overflowY: 'auto',
          px: { xs: 1.5, sm: 2, md: 3 },
          py: { xs: 1.5, sm: 2 },
        }}
      >
        {state.loading && renderLoadingState()}
        {state.error && renderErrorState()}
        {!state.loading && !state.error && state.data && renderContent()}
      </DialogContent>

      <DialogActions
        sx={{
          px: { xs: 1.5, sm: 2, md: 3 },
          py: { xs: 1, sm: 1.5 },
          gap: 1,
        }}
      >
        <Button 
          onClick={onClose} 
          color="primary"
          aria-label="close modal"
          sx={{
            fontSize: { xs: '0.875rem', sm: '1rem' },
          }}
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ClinicalGuidelinesModal;
