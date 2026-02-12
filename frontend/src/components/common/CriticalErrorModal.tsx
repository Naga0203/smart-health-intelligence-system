// ============================================================================
// Critical Error Modal Component
// ============================================================================
// Requirements: 11.7
// - Display modal dialog for critical errors
// - Require user acknowledgment before dismissing

import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  Alert,
  Box,
} from '@mui/material';
import { Error as ErrorIcon } from '@mui/icons-material';

interface CriticalErrorModalProps {
  open: boolean;
  title: string;
  message: string;
  details?: string;
  onAcknowledge: () => void;
}

export const CriticalErrorModal: React.FC<CriticalErrorModalProps> = ({
  open,
  title,
  message,
  details,
  onAcknowledge,
}) => {
  return (
    <Dialog
      open={open}
      onClose={undefined} // Prevent closing by clicking outside or pressing ESC
      aria-labelledby="critical-error-dialog-title"
      aria-describedby="critical-error-dialog-description"
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle id="critical-error-dialog-title">
        <Box display="flex" alignItems="center" gap={1}>
          <ErrorIcon color="error" />
          {title}
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Alert severity="error" sx={{ mb: 2 }}>
          {message}
        </Alert>
        
        {details && (
          <DialogContentText id="critical-error-dialog-description">
            {details}
          </DialogContentText>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button 
          onClick={onAcknowledge} 
          color="error" 
          variant="contained" 
          autoFocus
        >
          I Understand
        </Button>
      </DialogActions>
    </Dialog>
  );
};
