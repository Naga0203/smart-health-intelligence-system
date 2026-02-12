import React from 'react';
import {
  Box,
  LinearProgress,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

export interface FileUploadStatus {
  fileName: string;
  progress: number; // 0-100
  status: 'pending' | 'uploading' | 'completed' | 'error';
  error?: string;
}

interface UploadProgressProps {
  files: FileUploadStatus[];
  overallProgress?: number;
}

const getStatusIcon = (status: FileUploadStatus['status']) => {
  switch (status) {
    case 'completed':
      return <CheckCircleIcon color="success" />;
    case 'error':
      return <ErrorIcon color="error" />;
    case 'uploading':
    case 'pending':
      return <CloudUploadIcon color="primary" />;
    default:
      return <CloudUploadIcon />;
  }
};

const getStatusText = (status: FileUploadStatus['status'], progress: number) => {
  switch (status) {
    case 'completed':
      return 'Completed';
    case 'error':
      return 'Failed';
    case 'uploading':
      return `Uploading... ${progress}%`;
    case 'pending':
      return 'Pending';
    default:
      return 'Unknown';
  }
};

export const UploadProgress: React.FC<UploadProgressProps> = ({
  files,
  overallProgress,
}) => {
  if (files.length === 0) {
    return null;
  }

  const hasActiveUploads = files.some(
    (file) => file.status === 'uploading' || file.status === 'pending'
  );

  const completedCount = files.filter((file) => file.status === 'completed').length;
  const errorCount = files.filter((file) => file.status === 'error').length;

  return (
    <Paper elevation={2} sx={{ p: 3, mt: 3 }}>
      <Typography variant="h6" gutterBottom>
        Upload Progress
      </Typography>

      {overallProgress !== undefined && hasActiveUploads && (
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Overall Progress
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {Math.round(overallProgress)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={overallProgress}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>
      )}

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Typography variant="body2" color="text.secondary">
          Total: {files.length}
        </Typography>
        {completedCount > 0 && (
          <Typography variant="body2" color="success.main">
            Completed: {completedCount}
          </Typography>
        )}
        {errorCount > 0 && (
          <Typography variant="body2" color="error.main">
            Failed: {errorCount}
          </Typography>
        )}
      </Box>

      <List disablePadding>
        {files.map((file, index) => (
          <ListItem
            key={`${file.fileName}-${index}`}
            disablePadding
            sx={{
              mb: 2,
              '&:last-child': { mb: 0 },
            }}
          >
            <Box sx={{ width: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {getStatusIcon(file.status)}
                </ListItemIcon>
                <ListItemText
                  primary={file.fileName}
                  secondary={
                    file.error || getStatusText(file.status, file.progress)
                  }
                  primaryTypographyProps={{
                    noWrap: true,
                    title: file.fileName,
                  }}
                  secondaryTypographyProps={{
                    color: file.error ? 'error' : 'text.secondary',
                  }}
                />
              </Box>
              {(file.status === 'uploading' || file.status === 'pending') && (
                <LinearProgress
                  variant={file.status === 'pending' ? 'indeterminate' : 'determinate'}
                  value={file.progress}
                  sx={{ height: 4, borderRadius: 2 }}
                />
              )}
            </Box>
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};
