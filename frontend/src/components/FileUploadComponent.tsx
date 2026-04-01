// ============================================================================
// FileUploadComponent - Medical Report Upload with Extraction
// ============================================================================

import React, { useState, useCallback, useEffect } from 'react';
import { Box, Button, Alert, Typography } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { FileDropzone, FilePreview, UploadProgress, FileUploadStatus } from './upload';
import { ExtractedMedicalData, UploadError } from '@/types/medicalReport';
import { geminiAI } from '@/services/geminiService';
import { firebaseService } from '@/services/firebase.ts';

interface FileUploadComponentProps {
  onUploadComplete: (extractedData: ExtractedMedicalData, jobId: string, reportMetadata: {
    reportId: string;
    fileName: string;
    fileSize: number;
    uploadTimestamp: string;
  }) => void;
  onUploadError: (error: UploadError) => void;
  maxFileSizeMB?: number;
  acceptedFormats?: string[];
  userId: string;
}

const DEFAULT_MAX_FILE_SIZE_MB = 10;
const DEFAULT_ACCEPTED_FORMATS = ['.pdf', '.jpg', '.jpeg', '.png'];

export const FileUploadComponent: React.FC<FileUploadComponentProps> = ({
  onUploadComplete,
  onUploadError,
  maxFileSizeMB = DEFAULT_MAX_FILE_SIZE_MB,
  acceptedFormats = DEFAULT_ACCEPTED_FORMATS,
  userId,
}) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadStatus, setUploadStatus] = useState<FileUploadStatus[]>([]);
  const [extractionError, setExtractionError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  /**
   * Handle file selection from dropzone
   */
  const handleFilesSelected = useCallback((files: File[]) => {
    // For medical reports, we only support single file upload
    const file = files[0];
    if (!file) return;

    setSelectedFiles([file]);
    setExtractionError(null);
    setRetryCount(0);

    // Initialize upload status
    setUploadStatus([{
      fileName: file.name,
      progress: 0,
      status: 'pending',
    }]);
  }, []);

  /**
   * Remove selected file
   */
  const handleRemoveFile = useCallback(() => {
    setSelectedFiles([]);
    setUploadStatus([]);
    setExtractionError(null);
    setRetryCount(0);
  }, []);

  /**
   * Convert file to Base64 string
   */
  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const base64String = reader.result as string;
        const base64Data = base64String.split(',')[1];
        resolve(base64Data);
      };
      reader.onerror = error => reject(error);
    });
  };

  /**
   * Process file with Gemini OCR
   */
  const processFile = useCallback(async () => {
    if (selectedFiles.length === 0) return;

    const file = selectedFiles[0];
    setExtractionError(null);

    try {
      setUploadStatus([{
        fileName: file.name,
        progress: 10,
        status: 'uploading',
      }]);

      const base64Data = await fileToBase64(file);
      
      setUploadStatus([{
        fileName: file.name,
        progress: 40,
        status: 'uploading',
      }]);

      const extractionResult = await geminiAI.extractFromReport(base64Data, file.type);
      
      setUploadStatus([{
        fileName: file.name,
        progress: 80,
        status: 'uploading',
      }]);

      const jobId = `job_${Date.now()}`;
      const reportMetadata = {
        reportId: `report_${Date.now()}`,
        fileName: file.name,
        fileSize: file.size,
        uploadTimestamp: new Date().toISOString(),
      };

      await firebaseService.saveToCollection('analyses', {
        jobId,
        userId,
        status: 'complete',
        extractionData: extractionResult,
        reportMetadata,
        method: 'frontend_gemini_ocr'
      }, jobId);

      setUploadStatus([{
        fileName: file.name,
        progress: 100,
        status: 'completed',
      }]);

      onUploadComplete(extractionResult as any, jobId, reportMetadata);

    } catch (error: any) {
      console.error('OCR error:', error);
      const errorMessage = error.message || 'Failed to process report';
      setExtractionError(errorMessage);
      setUploadStatus([{
        fileName: file.name,
        progress: 0,
        status: 'error',
        error: errorMessage,
      }]);

      firebaseService.logError(error, 'FileUploadComponent.processFile');
      onUploadError({ code: 'ocr_failed', message: errorMessage });
    }
  }, [selectedFiles, userId, onUploadComplete, onUploadError]);

  /**
   * Retry processing
   */
  const handleRetry = useCallback(() => {
    setRetryCount(prev => prev + 1);
    setExtractionError(null);
    processFile();
  }, [processFile]);

  /**
   * Cancel and reset
   */
  const handleCancel = useCallback(() => {
    setSelectedFiles([]);
    setUploadStatus([]);
    setExtractionError(null);
    setRetryCount(0);
  }, []);

  useEffect(() => {
    if (selectedFiles.length > 0 && uploadStatus.length > 0 && uploadStatus[0].status === 'pending') {
      processFile();
    }
  }, [selectedFiles, uploadStatus, processFile]);

  const hasError = uploadStatus.some(file => file.status === 'error');
  const isUploading = uploadStatus.some(file => file.status === 'uploading');
  const isComplete = uploadStatus.some(file => file.status === 'completed');

  return (
    <Box>
      {selectedFiles.length === 0 && (
        <FileDropzone
          onFilesSelected={handleFilesSelected}
          maxFileSize={maxFileSizeMB * 1024 * 1024}
          acceptedFormats={acceptedFormats}
        />
      )}

      {selectedFiles.length > 0 && !isUploading && !isComplete && (
        <FilePreview
          files={selectedFiles}
          onRemove={handleRemoveFile}
        />
      )}

      {uploadStatus.length > 0 && (
        <UploadProgress files={uploadStatus} />
      )}

      {hasError && extractionError && (
        <Alert
          severity="error"
          sx={{ mt: 2 }}
          action={
            <Button
              color="inherit"
              size="small"
              startIcon={<RefreshIcon />}
              onClick={handleRetry}
              disabled={retryCount >= 3}
            >
              Retry
            </Button>
          }
        >
          <Typography variant="body2" fontWeight="medium">
            {extractionError}
          </Typography>
          {retryCount > 0 && (
            <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
              Retry attempt {retryCount} of 3
            </Typography>
          )}
        </Alert>
      )}

      {isComplete && (
        <Alert severity="success" sx={{ mt: 2 }}>
          <Typography variant="body2" fontWeight="medium">
            Report processed successfully!
          </Typography>
        </Alert>
      )}

      {(hasError || isComplete) && (
        <Box sx={{ mt: 2 }}>
          <Button variant="outlined" onClick={handleCancel}>
            Upload Another Report
          </Button>
        </Box>
      )}
    </Box>
  );
};

