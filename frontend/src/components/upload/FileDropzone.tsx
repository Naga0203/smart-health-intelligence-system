import React, { useCallback, useState } from 'react';
import { Box, Typography, Paper, Alert } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

interface FileDropzoneProps {
  onFilesSelected: (files: File[]) => void;
  maxFileSize?: number; // in bytes
  acceptedFormats?: string[];
}

const DEFAULT_MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const DEFAULT_ACCEPTED_FORMATS = ['.pdf', '.jpg', '.jpeg', '.png', '.dcm', '.dicom'];

export const FileDropzone: React.FC<FileDropzoneProps> = ({
  onFilesSelected,
  maxFileSize = DEFAULT_MAX_FILE_SIZE,
  acceptedFormats = DEFAULT_ACCEPTED_FORMATS,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const validateFile = (file: File): string | null => {
    // Check file size
    if (file.size > maxFileSize) {
      return `File "${file.name}" exceeds maximum size of ${maxFileSize / (1024 * 1024)}MB`;
    }

    // Check file format
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    const isValidFormat = acceptedFormats.some(format => 
      fileExtension === format.toLowerCase()
    );

    if (!isValidFormat) {
      return `File "${file.name}" has an invalid format. Accepted formats: ${acceptedFormats.join(', ')}`;
    }

    return null;
  };

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files || files.length === 0) return;

    const fileArray = Array.from(files);
    const validFiles: File[] = [];
    let errorMessage: string | null = null;

    for (const file of fileArray) {
      const error = validateFile(file);
      if (error) {
        errorMessage = error;
        break;
      }
      validFiles.push(file);
    }

    if (errorMessage) {
      setValidationError(errorMessage);
      return;
    }

    setValidationError(null);
    onFilesSelected(validFiles);
  }, [onFilesSelected, maxFileSize, acceptedFormats]);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    handleFiles(files);
  }, [handleFiles]);

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    handleFiles(files);
    // Reset input value to allow selecting the same file again
    e.target.value = '';
  }, [handleFiles]);

  const handleClick = useCallback(() => {
    const input = document.getElementById('file-input') as HTMLInputElement;
    input?.click();
  }, []);

  return (
    <Box>
      <Paper
        elevation={isDragging ? 8 : 2}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={handleClick}
        sx={{
          p: 4,
          textAlign: 'center',
          cursor: 'pointer',
          borderRadius: 3,
          border: '2px dashed',
          borderColor: isDragging ? '#0ea5e9' : 'rgba(255, 255, 255, 0.2)',
          backgroundColor: isDragging ? 'rgba(14, 165, 233, 0.1)' : 'rgba(255, 255, 255, 0.02)',
          backdropFilter: 'blur(10px)',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: '#0ea5e9',
            backgroundColor: 'rgba(14, 165, 233, 0.05)',
            boxShadow: '0 4px 20px rgba(14, 165, 233, 0.15)',
          },
        }}
      >
        <CloudUploadIcon
          sx={{
            fontSize: 64,
            color: isDragging ? '#38bdf8' : 'rgba(255, 255, 255, 0.5)',
            mb: 2,
          }}
        />
        <Typography variant="h6" gutterBottom>
          {isDragging ? 'Drop files here' : 'Drag and drop files here'}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          or click to select files
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 2 }}>
          Accepted formats: PDF, JPG, PNG, DICOM
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block">
          Maximum file size: {maxFileSize / (1024 * 1024)}MB
        </Typography>
      </Paper>

      <input
        id="file-input"
        type="file"
        multiple
        accept={acceptedFormats.join(',')}
        onChange={handleFileInputChange}
        style={{ display: 'none' }}
      />

      {validationError && (
        <Alert severity="error" sx={{ mt: 2 }} onClose={() => setValidationError(null)}>
          {validationError}
        </Alert>
      )}
    </Box>
  );
};
