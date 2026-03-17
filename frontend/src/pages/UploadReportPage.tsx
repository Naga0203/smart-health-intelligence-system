// ============================================================================
// Upload Medical Records Page - Responsive Design
// Clean, modern interface for uploading medical documents
// Matches HealthIntel AI design mockup
// ============================================================================

import React, { useState, useCallback, useRef } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  LinearProgress,
  Breadcrumbs,
  Link,
  Fade,
  useTheme,
  alpha,
} from '@mui/material';
import {
  CloudUpload,
  Description,
  Delete,
  CheckCircle,
  Error as ErrorIcon,
  NavigateNext,
  Lock,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface UploadedFile {
  id: string;
  file: File;
  status: 'pending' | 'uploading' | 'validated' | 'error';
  progress: number;
  errorMessage?: string;
}

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
const ALLOWED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.dcm'];

export const UploadReportPage: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();

  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Validate file
  const validateFile = (file: File): { valid: boolean; error?: string } => {
    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return { valid: false, error: 'File exceeds 50MB limit' };
    }

    // Check file type
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    const isValidType = ALLOWED_TYPES.includes(file.type) ||
      ALLOWED_EXTENSIONS.includes(extension);

    if (!isValidType) {
      return { valid: false, error: 'File format not supported' };
    }

    return { valid: true };
  };

  // Handle file selection
  const handleFiles = useCallback((files: FileList | null) => {
    if (!files) return;

    const newFiles: UploadedFile[] = [];

    Array.from(files).forEach((file) => {
      const validation = validateFile(file);

      const uploadedFile: UploadedFile = {
        id: `${file.name}-${Date.now()}-${Math.random()}`,
        file,
        status: validation.valid ? 'pending' : 'error',
        progress: 0,
        errorMessage: validation.error,
      };

      newFiles.push(uploadedFile);

      // Simulate upload for valid files
      if (validation.valid) {
        simulateUpload(uploadedFile.id);
      }
    });

    setUploadedFiles(prev => [...prev, ...newFiles]);
  }, []);

  // Simulate file upload
  const simulateUpload = (fileId: string) => {
    // Start uploading
    setUploadedFiles(prev =>
      prev.map(f => f.id === fileId ? { ...f, status: 'uploading' as const, progress: 0 } : f)
    );

    // Simulate progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += 15;

      if (progress >= 100) {
        clearInterval(interval);
        setUploadedFiles(prev =>
          prev.map(f => f.id === fileId ? { ...f, status: 'validated' as const, progress: 100 } : f)
        );
      } else {
        setUploadedFiles(prev =>
          prev.map(f => f.id === fileId ? { ...f, progress } : f)
        );
      }
    }, 200);
  };

  // Handle drag events
  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    handleFiles(e.dataTransfer.files);
  };

  // Handle browse button click
  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  // Handle file input change
  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  };

  // Remove file
  const handleRemoveFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  // Get file icon
  const getFileIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'validated':
        return <CheckCircle sx={{ color: 'success.main' }} />;
      case 'error':
        return <ErrorIcon sx={{ color: 'error.main' }} />;
      case 'uploading':
        return <Description sx={{ color: 'primary.main' }} />;
      default:
        return <Description />;
    }
  };

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  // Handle process reports
  const handleProcessReports = () => {
    // Navigate to results or trigger processing
    navigate('/app/dashboard');
  };

  // Handle cancel
  const handleCancel = () => {
    setUploadedFiles([]);
  };

  const hasValidFiles = uploadedFiles.some(f => f.status === 'validated');

  return (
    <Fade in={true} timeout={500}>
      <Box
        sx={{
          minHeight: '100vh',
          pb: 8,
          background: `linear-gradient(135deg, ${theme.palette.background.default} 0%, ${theme.palette.background.paper} 100%)`,
        }}
      >
        <Container
          maxWidth="lg"
          sx={{
            py: { xs: 2, sm: 3, md: 4 },
            px: { xs: 2, sm: 3 },
            position: 'relative',
            zIndex: 1,
          }}
        >
          {/* Breadcrumbs */}
          <Breadcrumbs
            separator={<NavigateNext fontSize="small" />}
            sx={{ mb: { xs: 2, sm: 3 } }}
          >
            <Link
              color="inherit"
              href="/app/dashboard"
              underline="hover"
              sx={{ cursor: 'pointer' }}
            >
              Home
            </Link>
            <Link
              color="inherit"
              href="/app/assessment/new"
              underline="hover"
              sx={{ cursor: 'pointer' }}
            >
              New Case
            </Link>
            <Typography color="text.primary">Upload Reports</Typography>
          </Breadcrumbs>

          {/* Page Title */}
          <Box sx={{ mb: { xs: 3, sm: 4 } }}>
            <Typography
              variant="h3"
              gutterBottom
              sx={{
                fontSize: { xs: '1.75rem', sm: '2.5rem', md: '3rem' },
                fontWeight: 700,
              }}
            >
              Upload Medical Records
            </Typography>
            <Typography
              variant="body1"
              color="text.secondary"
              sx={{
                fontSize: { xs: '0.875rem', sm: '1rem' },
              }}
            >
              Securely upload patient history, lab results, or imaging for AI analysis.
            </Typography>
          </Box>

          {/* Drag & Drop Zone */}
          <Paper
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            sx={{
              background: isDragging 
                ? `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)} 0%, ${alpha(theme.palette.primary.light, 0.05)} 100%)`
                : `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.4)} 0%, ${alpha(theme.palette.background.paper, 0.1)} 100%)`,
              backdropFilter: 'blur(10px)',
              border: '2px dashed',
              borderColor: isDragging ? theme.palette.primary.main : alpha(theme.palette.divider, 0.2),
              borderRadius: 4,
              p: { xs: 4, sm: 6, md: 8 },
              textAlign: 'center',
              transition: 'all 0.3s ease-in-out',
              cursor: 'pointer',
              mb: { xs: 3, sm: 4 },
              boxShadow: isDragging ? `0 8px 24px ${alpha(theme.palette.primary.main, 0.15)}` : 'none',
              '&:hover': {
                borderColor: theme.palette.primary.main,
                background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(theme.palette.primary.light, 0.02)} 100%)`,
                transform: 'translateY(-2px)',
                boxShadow: `0 8px 24px ${alpha(theme.palette.primary.main, 0.1)}`,
              },
            }}
          >
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 2,
              }}
            >
              <Box
                sx={{
                  width: { xs: 60, sm: 80 },
                  height: { xs: 60, sm: 80 },
                  borderRadius: '50%',
                  bgcolor: 'primary.light',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <CloudUpload
                  sx={{
                    fontSize: { xs: 32, sm: 40 },
                    color: 'primary.main',
                  }}
                />
              </Box>

              <Typography
                variant="h6"
                sx={{
                  fontSize: { xs: '1rem', sm: '1.25rem' },
                  fontWeight: 600,
                }}
              >
                Drag & drop files here
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
              >
                Supports PDF, JPG, PNG, and DICOM (Max 50MB per file).
              </Typography>

              <Button
                variant="outlined"
                onClick={handleBrowseClick}
                sx={{
                  mt: 1,
                  minHeight: { xs: 44, sm: 48 },
                  px: 4,
                  borderRadius: 3,
                  textTransform: 'none',
                  fontWeight: 600,
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                  borderColor: alpha(theme.palette.primary.main, 0.5),
                  color: 'primary.main',
                  backdropFilter: 'blur(10px)',
                  background: alpha(theme.palette.primary.main, 0.05),
                  '&:hover': {
                    borderColor: 'primary.main',
                    background: alpha(theme.palette.primary.main, 0.1),
                    transform: 'translateY(-2px)',
                  },
                  transition: 'all 0.2s ease-in-out',
                }}
              >
                Browse Files
              </Button>

              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.jpg,.jpeg,.png,.dcm"
                onChange={handleFileInputChange}
                style={{ display: 'none' }}
              />
            </Box>
          </Paper>

          {/* Uploaded Files List */}
          {uploadedFiles.length > 0 && (
            <Box sx={{ mb: { xs: 3, sm: 4 } }}>
              <Typography
                variant="h6"
                gutterBottom
                sx={{
                  fontSize: { xs: '1.125rem', sm: '1.25rem' },
                  fontWeight: 600,
                  mb: 2,
                }}
              >
                Uploaded Files
              </Typography>

              <List sx={{ bgcolor: 'background.paper', borderRadius: 1 }}>
                {uploadedFiles.map((uploadedFile) => (
                  <ListItem
                    key={uploadedFile.id}
                    sx={{
                      background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.4)} 0%, ${alpha(theme.palette.background.paper, 0.1)} 100%)`,
                      backdropFilter: 'blur(10px)',
                      border: '1px solid',
                      borderColor: alpha(theme.palette.divider, 0.2),
                      borderRadius: 3,
                      mb: 2,
                      transition: 'all 0.3s ease-in-out',
                      '&:hover': {
                        background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(theme.palette.primary.light, 0.02)} 100%)`,
                        borderColor: alpha(theme.palette.primary.main, 0.3),
                        transform: 'translateY(-2px)',
                        boxShadow: `0 4px 12px ${alpha(theme.palette.primary.main, 0.08)}`,
                      },
                    }}
                  >
                    <ListItemIcon>
                      {getFileIcon(uploadedFile.status)}
                    </ListItemIcon>

                    <ListItemText
                      primary={
                        <Typography
                          variant="body1"
                          sx={{
                            fontSize: { xs: '0.875rem', sm: '1rem' },
                            fontWeight: 500,
                          }}
                        >
                          {uploadedFile.file.name}
                        </Typography>
                      }
                      secondary={
                        <Box>
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ fontSize: { xs: '0.75rem', sm: '0.75rem' } }}
                          >
                            {formatFileSize(uploadedFile.file.size) + ' • '}
                            {uploadedFile.status === 'validated' && 'Complete'}
                            {uploadedFile.status === 'uploading' && `Uploading... ${uploadedFile.progress}%`}
                            {uploadedFile.status === 'error' && uploadedFile.errorMessage}
                          </Typography>

                          {uploadedFile.status === 'uploading' && (
                            <LinearProgress
                              variant="determinate"
                              value={uploadedFile.progress}
                              sx={{ mt: 1, height: 6, borderRadius: 1 }}
                            />
                          )}
                        </Box>
                      }
                    />

                    <ListItemSecondaryAction>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        {uploadedFile.status === 'validated' && (
                          <Typography
                            variant="caption"
                            sx={{
                              color: 'success.main',
                              fontWeight: 600,
                              display: { xs: 'none', sm: 'block' },
                            }}
                          >
                            Validated
                          </Typography>
                        )}

                        <IconButton
                          edge="end"
                          onClick={() => handleRemoveFile(uploadedFile.id)}
                          sx={{
                            minWidth: { xs: 44, sm: 40 },
                            minHeight: { xs: 44, sm: 40 },
                          }}
                        >
                          <Delete />
                        </IconButton>
                      </Box>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {/* Security Notice & Actions */}
          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', sm: 'row' },
              justifyContent: 'space-between',
              alignItems: { xs: 'stretch', sm: 'center' },
              gap: 2,
              mt: 4,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Lock sx={{ color: 'text.secondary', fontSize: 18 }} />
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ fontSize: { xs: '0.75rem', sm: '0.75rem' } }}
              >
                Your data is encrypted end-to-end. We adhere to strict HIPAA privacy standards to ensure patient confidentiality.
              </Typography>
            </Box>

            <Box
              sx={{
                display: 'flex',
                gap: 2,
                flexDirection: { xs: 'column', sm: 'row' },
              }}
            >
              <Button
                variant="outlined"
                onClick={handleCancel}
                disabled={uploadedFiles.length === 0}
                sx={{
                  minHeight: { xs: 44, sm: 48 },
                  minWidth: { sm: 120 },
                  borderRadius: 3,
                  textTransform: 'none',
                  fontWeight: 600,
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                  borderColor: alpha(theme.palette.text.primary, 0.5),
                  color: 'text.primary',
                  backdropFilter: 'blur(10px)',
                  background: alpha(theme.palette.background.paper, 0.1),
                  '&:hover': {
                    borderColor: 'text.primary',
                    background: alpha(theme.palette.background.paper, 0.2),
                    transform: 'translateY(-2px)',
                  },
                  transition: 'all 0.2s ease-in-out',
                }}
              >
                Cancel
              </Button>

              <Button
                variant="contained"
                onClick={handleProcessReports}
                disabled={!hasValidFiles}
                sx={{
                  minHeight: { xs: 44, sm: 48 },
                  minWidth: { sm: 160 },
                  bgcolor: 'primary.main',
                  color: 'white',
                  borderRadius: 3,
                  textTransform: 'none',
                  fontWeight: 600,
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                  boxShadow: `0 8px 24px ${alpha(theme.palette.primary.main, 0.4)}`,
                  '&:hover': {
                    bgcolor: 'primary.dark',
                    transform: 'translateY(-2px)',
                    boxShadow: `0 12px 28px ${alpha(theme.palette.primary.main, 0.6)}`,
                  },
                  transition: 'all 0.2s ease-in-out',
                  '&.Mui-disabled': {
                    background: alpha(theme.palette.action.disabledBackground, 0.1),
                    color: alpha(theme.palette.text.primary, 0.3),
                  }
                }}
              >
                Process Reports
              </Button>
            </Box>
          </Box>
        </Container>
      </Box>
    </Fade>
  );
};

export default UploadReportPage;
