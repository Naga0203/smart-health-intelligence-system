// ============================================================================
// Report Service - Medical Report Upload and Extraction API
// ============================================================================

import { apiService } from './api';
import { ExtractedMedicalData } from '@/types/medicalReport';

interface UploadResponse {
  success: boolean;
  job_id: string;
  report_id: string;
  file_name: string;
  file_size: number;
  upload_timestamp: string;
  status: string;
  estimated_completion_seconds: number;
}

interface ExtractionStatusResponse {
  job_id: string;
  status: 'processing' | 'complete' | 'failed';
  progress_percent?: number;
  message?: string;
  extracted_data?: ExtractedMedicalData;
  extraction_metadata?: {
    extraction_time_seconds: number;
    ocr_used: boolean;
    pages_processed: number;
    gemini_model: string;
  };
  error_code?: string;
  partial_data?: any;
}

interface ReportMetadataResponse {
  report_id: string;
  user_id: string;
  file_name: string;
  file_size: number;
  file_type: string;
  upload_timestamp: string;
  download_url: string;
  extraction_job_id: string;
  associated_assessment_id?: string;
}

class ReportService {
  /**
   * Upload a medical report file
   * POST /api/reports/upload/
   */
  async uploadReport(file: File, userId: string): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);

    const response = await apiService.client.post('/api/reports/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  /**
   * Get extraction status and results
   * GET /api/reports/extract/{job_id}/
   */
  async getExtractionStatus(jobId: string): Promise<ExtractionStatusResponse> {
    const response = await apiService.client.get(`/api/reports/extract/${jobId}/`);
    return response.data;
  }

  /**
   * Get report metadata and download URL
   * GET /api/reports/{report_id}/
   */
  async getReportMetadata(reportId: string): Promise<ReportMetadataResponse> {
    const response = await apiService.client.get(`/api/reports/${reportId}/`);
    return response.data;
  }
}

export const reportService = new ReportService();
