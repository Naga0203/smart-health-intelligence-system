// ============================================================================
// FileUploadComponent - Medical Report Upload with Extraction
// ============================================================================

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Box, Button, Alert, Typography } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { FileDropzone, FilePreview, UploadProgress, FileUploadStatus } from './upload';
import { ExtractedMedicalData, UploadError } from '@/types/medicalReport';
import { reportService } from '@/services/reportService';

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
const POLL_INTERVAL_MS = 2000; // Poll every 2 seconds
const MAX_POLL_ATTEMPTS = 60; // 2 minutes max (60 * 2 seconds)

export const FileUploadComponent: React.FC<FileUploadComponentProps> = ({
  onUploadComplete,
  onUploadError,
  maxFileSizeMB = DEFAULT_MAX_FILE_SIZE_MB,
  acceptedFormats = DEFAULT_ACCEPTED_FORMATS,
  userId,
}) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadStatus, setUploadStatus] = useState<FileUploadStatus[]>([]);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [currentReportMetadata, setCurrentReportMetadata] = useState<{
    reportId: string;
    fileName: string;
    fileSize: number;
    uploadTimestamp: string;
  } | null>(null);
  const [extractionError, setExtractionError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const pollAttemptsRef = useRef<number>(0);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

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
    setCurrentJobId(null);
  }, []);

  /**
   * Poll extraction status
   */
  const pollExtractionStatus = useCallback(async (jobId: string) => {
    try {
      pollAttemptsRef.current += 1;

      const statusResponse = await reportService.getExtractionStatus(jobId);

      if (statusResponse.status === 'complete') {
        // Extraction complete
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        setIsPolling(false);

        setUploadStatus(prev => prev.map(file => ({
          ...file,
          progress: 100,
          status: 'completed',
        })));

        // Call success callback with extracted data and report metadata
        if (currentReportMetadata && statusResponse.extracted_data) {
          onUploadComplete(statusResponse.extracted_data, jobId, currentReportMetadata);
        }

      } else if (statusResponse.status === 'failed') {
        // Extraction failed
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        setIsPolling(false);

        const errorMessage = statusResponse.message || 'Extraction failed';
        setExtractionError(errorMessage);

        setUploadStatus(prev => prev.map(file => ({
          ...file,
          status: 'error',
          error: errorMessage,
        })));

        onUploadError({
          code: statusResponse.error_code || 'extraction_failed',
          message: errorMessage,
          details: statusResponse.partial_data,
        });

      } else if (statusResponse.status === 'processing') {
        // Still processing - update progress
        const progress = statusResponse.progress_percent || 50;
        setUploadStatus(prev => prev.map(file => ({
          ...file,
          progress,
          status: 'uploading',
        })));
      }

      // Check if we've exceeded max poll attempts
      if (pollAttemptsRef.current >= MAX_POLL_ATTEMPTS) {
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        setIsPolling(false);

        const timeoutError = 'Extraction timeout - processing is taking longer than expected';
        setExtractionError(timeoutError);

        setUploadStatus(prev => prev.map(file => ({
          ...file,
          status: 'error',
          error: timeoutError,
        })));

        onUploadError({
          code: 'extraction_timeout',
          message: timeoutError,
        });
      }

    } catch (error: any) {
      console.error('Error polling extraction status:', error);

      // Don't stop polling on network errors - just log and continue
      if (pollAttemptsRef.current >= MAX_POLL_ATTEMPTS) {
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        setIsPolling(false);

        const errorMessage = error.response?.data?.message || 'Failed to check extraction status';
        setExtractionError(errorMessage);

        setUploadStatus(prev => prev.map(file => ({
          ...file,
          status: 'error',
          error: errorMessage,
        })));

        onUploadError({
          code: 'status_check_failed',
          message: errorMessage,
        });
      }
    }
  }, [onUploadComplete, onUploadError]);

  /**
   * Start polling for extraction status
   */
  const startPolling = useCallback((jobId: string) => {
    setIsPolling(true);
    pollAttemptsRef.current = 0;

    // Clear any existing interval
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }

    // Start polling
    pollIntervalRef.current = setInterval(() => {
      pollExtractionStatus(jobId);
    }, POLL_INTERVAL_MS);

    // Also poll immediately
    pollExtractionStatus(jobId);
  }, [pollExtractionStatus]);

  /**
   * Upload file to backend
   */
  const uploadFile = useCallback(async () => {
    if (selectedFiles.length === 0) return;

    const file = selectedFiles[0];
    setExtractionError(null);

    try {
      // Update status to uploading
      setUploadStatus([{
        fileName: file.name,
        progress: 0,
        status: 'uploading',
      }]);

      // Upload file
      const uploadResponse = await reportService.uploadReport(file, userId);

      // Store report metadata
      setCurrentReportMetadata({
        reportId: uploadResponse.report_id,
        fileName: uploadResponse.file_name,
        fileSize: uploadResponse.file_size,
        uploadTimestamp: uploadResponse.upload_timestamp,
      });

      // Update progress to show upload complete
      setUploadStatus([{
        fileName: file.name,
        progress: 30,
        status: 'uploading',
      }]);

      // Store job ID and start polling
      setCurrentJobId(uploadResponse.job_id);
      startPolling(uploadResponse.job_id);

    } catch (error: any) {
      console.error('Upload error:', error);

      const errorMessage = error.response?.data?.message || 'Upload failed';
      const errorCode = error.response?.data?.error_code || 'upload_failed';

      setExtractionError(errorMessage);

      setUploadStatus([{
        fileName: file.name,
        progress: 0,
        status: 'error',
        error: errorMessage,
      }]);

      onUploadError({
        code: errorCode,
        message: errorMessage,
        details: error.response?.data?.details,
      });
    }
  }, [selectedFiles, userId, startPolling, onUploadError]);

  /**
   * Retry upload after failure
   */
  const handleRetry = useCallback(() => {
    setRetryCount(prev => prev + 1);
    setExtractionError(null);
    uploadFile();
  }, [uploadFile]);

  /**
   * Cancel upload and reset
   */
  const handleCancel = useCallback(() => {
    // Stop polling
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
    setIsPolling(false);

    // Reset state
    setSelectedFiles([]);
    setUploadStatus([]);
    setExtractionError(null);
    setCurrentJobId(null);
    setCurrentReportMetadata(null);
    setRetryCount(0);
    pollAttemptsRef.current = 0;
  }, []);

  // Auto-upload when file is selected
  useEffect(() => {
    if (selectedFiles.length > 0 && uploadStatus.length > 0 && uploadStatus[0].status === 'pending') {
      uploadFile();
    }
  }, [selectedFiles, uploadStatus, uploadFile]);

  const hasError = uploadStatus.some(file => file.status === 'error');
  const isUploading = uploadStatus.some(file => file.status === 'uploading') || isPolling;
  const isComplete = uploadStatus.some(file => file.status === 'completed');

  return (
    <Box>
      {/* File Selection */}
      {selectedFiles.length === 0 && (
        <FileDropzone
          onFilesSelected={handleFilesSelected}
          maxFileSize={maxFileSizeMB * 1024 * 1024}
          acceptedFormats={acceptedFormats}
        />
      )}

      {/* File Preview */}
      {selectedFiles.length > 0 && !isUploading && !isComplete && (
        <FilePreview
          files={selectedFiles}
          onRemove={handleRemoveFile}
        />
      )}

      {/* Upload Progress */}
      {uploadStatus.length > 0 && (
        <UploadProgress files={uploadStatus} />
      )}

      {/* Error Display with Retry */}
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

      {/* Success Message */}
      {isComplete && (
        <Alert severity="success" sx={{ mt: 2 }}>
          <Typography variant="body2" fontWeight="medium">
            Report uploaded and processed successfully!
          </Typography>
          <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
            Your assessment form has been populated with the extracted data.
          </Typography>
        </Alert>
      )}

      {/* Action Buttons */}
      {(hasError || isComplete) && (
        <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            onClick={handleCancel}
          >
            Upload Another Report
          </Button>
        </Box>
      )}
    </Box>
  );
};
