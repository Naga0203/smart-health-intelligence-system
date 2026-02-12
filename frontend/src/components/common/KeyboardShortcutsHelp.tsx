// ============================================================================
// Keyboard Shortcuts Help Component
// ============================================================================

import {
  Dialog,
  DialogTitle,
  DialogContent,
  List,
  ListItem,
  ListItemText,
  Typography,
  Box,
  IconButton,
} from '@mui/material';
import { Close } from '@mui/icons-material';
import { KEYBOARD_SHORTCUTS, formatShortcut } from '@/utils/keyboardNavigation';

interface KeyboardShortcutsHelpProps {
  open: boolean;
  onClose: () => void;
}

export const KeyboardShortcutsHelp: React.FC<KeyboardShortcutsHelpProps> = ({
  open,
  onClose,
}) => {
  const shortcuts = [
    { ...KEYBOARD_SHORTCUTS.DASHBOARD, description: 'Go to Dashboard' },
    { ...KEYBOARD_SHORTCUTS.NEW_ASSESSMENT, description: 'New Assessment' },
    { ...KEYBOARD_SHORTCUTS.HISTORY, description: 'View History' },
    { ...KEYBOARD_SHORTCUTS.PROFILE, description: 'View Profile' },
    { ...KEYBOARD_SHORTCUTS.SUBMIT, description: 'Submit Form' },
    { ...KEYBOARD_SHORTCUTS.CANCEL, description: 'Cancel/Close' },
  ];

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      aria-labelledby="keyboard-shortcuts-title"
    >
      <DialogTitle id="keyboard-shortcuts-title">
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Keyboard Shortcuts</Typography>
          <IconButton
            aria-label="close"
            onClick={onClose}
            size="small"
          >
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <List>
          {shortcuts.map((shortcut, index) => (
            <ListItem key={index} sx={{ py: 1 }}>
              <ListItemText
                primary={shortcut.description}
                secondary={
                  <Box
                    component="kbd"
                    sx={{
                      display: 'inline-block',
                      px: 1,
                      py: 0.5,
                      backgroundColor: 'grey.200',
                      borderRadius: 1,
                      fontSize: '0.875rem',
                      fontFamily: 'monospace',
                      border: '1px solid',
                      borderColor: 'grey.400',
                    }}
                  >
                    {formatShortcut(shortcut)}
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Note: Shortcuts work when not typing in input fields.
        </Typography>
      </DialogContent>
    </Dialog>
  );
};
