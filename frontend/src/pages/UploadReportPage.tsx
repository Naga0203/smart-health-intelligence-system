import React, { useState, useCallback } from 'react';
import { Container, Box, Typography, Paper, Button, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { FileDropzone } from '@/components/upload/FileDropzone';
import { FilePreview } from '@/components/upload/FilePreview';
import { UploadProgress, FileUploadStatus } from '@/components/upload/UploadProgress';
import { ExtractionPreview, ExtractedData } from '@/components/upload/ExtractionPreview';
import { useAssessmentStore } from '@/stores/assessmentStore';
import { useSystemStore } from '@/stores/systemStore';
import { useNotificationStore } from '@/stores/notificationStore';

export const UploadReportPage: React.FC = () => {
  const navigate = useNavigate();
  const submitAssessment = useAssessmentStore((state: any) => state.submitAssessment);
  const systemStatus = useSystemStore((state: any) => state.status);
  const addNotification = useNotificationStore((state: any) => state.addNotification);

  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadStatuses, setUploadStatuses] = useState<FileUploadStatus[]>([]);
  const [extractedData, setExtractedData] = useState<ExtractedData[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFilesSelected = useCallback((files: File[]) => {
    setSelectedFiles((prev) => [...prev, ...files]);
    setUploadError(null);
  }, []);

  const handleRemoveFile = useCallback((index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
    // Also remove from upload statuses and extracted data if present
    setUploadStatuses((prev) => prev.filter((_, i) => i !== index));
    setExtractedData((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const simulateFileUpload = useCallback(
    async (file: File, index: number): Promise<ExtractedData> => {
      // Update status to uploading
      setUploadStatuses((prev) => {
        const newStatuses = [...prev];
        newStatuses[index] = {
          fileName: file.name,
          progress: 0,
          status: 'uploading',
        };
        return newStatuses;
      });

      // Simulate upload progress
      for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise((resolve) => setTimeout(resolve, 100));
        setUploadStatuses((prev) => {
          const newStatuses = [...prev];
          if (newStatuses[index]) {
            newStatuses[index].progress = progress;
          }
          return newStatuses;
        });
      }

      // Simulate extraction (in real implementation, this would call the backend)
      // For now, return mock extracted data
      const mockExtractedData: ExtractedData = {
        fileName: file.name,
        confidence: Math.floor(Math.random() * 40) + 60, // 60-100
        method: 'OCR + NLP',
        extractedFeatures: ['text_extraction', 'entity_recognition', 'medical_terminology'],
        symptoms: ['fever', 'cough', 'fatigue'],
        vitals: {
          temperature: 99.5,
          heartRate: 85,
          bloodPressureSystolic: 120,
          bloodPressureDiastolic: 80,
        },
        demographics: {
          age: 35,
          gender: 'male',
        },
        notes: 'Extracted from medical report dated ' + new Date().toLocaleDateString(),
      };

      // Update status to completed
      setUploadStatuses((prev) => {
        const newStatuses = [...prev];
        newStatuses[index] = {
          fileName: file.name,
          progress: 100,
          status: 'completed',
        };
        return newStatuses;
      });

      return mockExtractedData;
    },
    []
  );

  const handleUpload = useCallback(async () => {
    if (selectedFiles.length === 0) {
      addNotification({
        type: 'warning',
        message: 'Please select at least one file to upload',
        dismissible: true,
      });
      return;
    }

    // Check system status
    if (systemStatus?.status !== 'operational') {
      addNotification({
        type: 'error',
        message: 'System is currently unavailable. Please try again later.',
        dismissible: true,
      });
      return;
    }

    setIsUploading(true);
    setUploadError(null);

    try {
      // Initialize upload statuses
      const initialStatuses: FileUploadStatus[] = selectedFiles.map((file) => ({
        fileName: file.name,
        progress: 0,
        status: 'pending',
      }));
      setUploadStatuses(initialStatuses);

      // Upload files and extract data
      const extractedResults: ExtractedData[] = [];
      for (let i = 0; i < selectedFiles.length; i++) {
        try {
          const result = await simulateFileUpload(selectedFiles[i], i);
          extractedResults.push(result);
        } catch (error) {
          setUploadStatuses((prev) => {
            const newStatuses = [...prev];
            newStatuses[i] = {
              fileName: selectedFiles[i].name,
              progress: 0,
              status: 'error',
              error: 'Upload failed',
            };
            return newStatuses;
          });
        }
      }

      setExtractedData(extractedResults);

      if (extractedResults.length === 0) {
        setUploadError('All file uploads failed. Please try again.');
      } else if (extractedResults.length < selectedFiles.length) {
        addNotification({
          type: 'warning',
          message: 'Some files failed to upload. Please review the results.',
          dismissible: true,
        });
      } else {
        addNotification({
          type: 'success',
          message: 'All files uploaded successfully',
          dismissible: true,
        });
      }
    } catch (error) {
      setUploadError('An error occurred during upload. Please try again.');
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  }, [selectedFiles, systemStatus, addNotification, simulateFileUpload]);

  const handleConfirmSubmit = useCallback(async () => {
    if (extractedData.length === 0) {
      return;
    }

    setIsSubmitting(true);

    try {
      // Combine all extracted data into a single assessment request
      const allSymptoms = new Set<string>();
      let demographics = null;
      let vitals = null;

      extractedData.forEach((data) => {
        if (data.symptoms) {
          data.symptoms.forEach((symptom) => allSymptoms.add(symptom));
        }
        if (data.demographics && !demographics) {
          demographics = data.demographics;
        }
        if (data.vitals && !vitals) {
          vitals = data.vitals;
        }
      });

      // Create assessment request
      const assessmentData = {
        symptoms: Array.from(allSymptoms),
        age: demographics?.age || 30,
        gender: demographics?.gender || 'other',
        additional_info: {
          vitals,
          source: 'medical_report_upload',
          files: extractedData.map((d) => d.fileName),
        },
      };

      // Submit assessment
      await submitAssessment(assessmentData);

      addNotification({
        type: 'success',
        message: 'Assessment submitted successfully',
        dismissible: true,
      });

      // Navigate to results or dashboard
      // In a real implementation, we would navigate to the specific assessment result
      navigate('/app/dashboard');
    } catch (error) {
      addNotification({
        type: 'error',
        message: 'Failed to submit assessment. Please try again.',
        dismissible: true,
      });
      console.error('Submit error:', error);
    } finally {
      setIsSubmitting(false);
    }
  }, [extractedData, submitAssessment, addNotification, navigate]);

  const handleCancel = useCallback(() => {
    setExtractedData([]);
    setUploadStatuses([]);
    setSelectedFiles([]);
  }, []);

  const handleBack = useCallback(() => {
    navigate('/app/dashboard');
  }, [navigate]);

  const overallProgress = uploadStatuses.length > 0
    ? uploadStatuses.reduce((sum, status) => sum + status.progress, 0) / uploadStatuses.length
    : 0;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={handleBack}
        sx={{ mb: 3 }}
      >
        Back to Dashboard
      </Button>

      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          Upload Medical Reports
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Upload your medical reports (PDF, JPG, PNG, DICOM) for automated data extraction and
          health risk assessment.
        </Typography>

        {systemStatus?.status !== 'operational' && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            System is currently {systemStatus?.status || 'unavailable'}. Please try again later.
          </Alert>
        )}

        <Box sx={{ mt: 3 }}>
          <FileDropzone onFilesSelected={handleFilesSelected} />
        </Box>

        {selectedFiles.length > 0 && (
          <>
            <FilePreview files={selectedFiles} onRemove={handleRemoveFile} />

            {extractedData.length === 0 && (
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
                <Button
                  variant="contained"
                  onClick={handleUpload}
                  disabled={isUploading || systemStatus?.status !== 'operational'}
                >
                  {isUploading ? 'Uploading...' : 'Upload and Extract Data'}
                </Button>
              </Box>
            )}
          </>
        )}

        {uploadStatuses.length > 0 && (
          <UploadProgress files={uploadStatuses} overallProgress={overallProgress} />
        )}

        {uploadError && (
          <Alert severity="error" sx={{ mt: 3 }}>
            {uploadError}
          </Alert>
        )}

        {extractedData.length > 0 && (
          <ExtractionPreview
            extractedData={extractedData}
            onConfirm={handleConfirmSubmit}
            onCancel={handleCancel}
            loading={isSubmitting}
          />
        )}
      </Paper>
    </Container>
  );
};

export default UploadReportPage;
