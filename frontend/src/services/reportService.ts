// ============================================================================
// Report Service - Medical Report Upload and Extraction API
// ============================================================================

import { apiService } from './api';
import { ExtractedMedicalData, UploadError } from '@/types/medicalReport';
import { AxiosError } from 'axios';

// ============================================================================
// Type Definitions
// ============================================================================

export interface UploadResponse {
  success: boolean;
  job_id: string;
  report_id: string;
  file_name: string;
  file_size: number;
  upload_timestamp: string;
  status: string;
  estimated_completion_seconds: number;
}

export interface ExtractionStatus {
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

export interface ReportMetadata {
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

// ============================================================================
// Error Handling Utilities
// ============================================================================

/**
 * Custom error class for report service errors
 */
export class ReportServiceError extends Error {
  constructor(
    message: string,
    public code: string,
    public details?: Record<string, any>,
    public retryAllowed: boolean = false
  ) {
    super(message);
    this.name = 'ReportServiceError';
  }
}

/**
 * Parse error response from API
 */
function parseErrorResponse(error: AxiosError): UploadError {
  if (error.response?.data) {
    const data = error.response.data as any;
    return {
      code: data.error_code || 'unknown_error',
      message: data.message || error.message,
      details: data.details || {},
    };
  }

  // Network or timeout errors
  if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
    return {
      code: 'timeout',
      message: 'Request timed out. Please try again.',
      details: { retry_allowed: true },
    };
  }

  if (!error.response) {
    return {
      code: 'network_error',
      message: 'Network error. Please check your connection.',
      details: { retry_allowed: true },
    };
  }

  return {
    code: 'unknown_error',
    message: error.message || 'An unexpected error occurred',
    details: {},
  };
}

/**
 * Sleep utility for retry delays
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Calculate exponential backoff delay
 */
function getBackoffDelay(attempt: number, baseDelay: number = 1000): number {
  return Math.min(baseDelay * Math.pow(2, attempt), 10000); // Max 10 seconds
}

// ============================================================================
// Report Service Class
// ============================================================================

class ReportService {
  private readonly MAX_RETRIES = 3;
  private readonly BASE_RETRY_DELAY = 1000; // 1 second

  /**
   * Upload a medical report file with retry logic
   * POST /api/reports/upload/
   * 
   * @param file - File to upload
   * @param userId - User ID
   * @param maxRetries - Maximum number of retry attempts (default: 3)
   * @returns Upload response with job and report IDs
   * @throws ReportServiceError on failure after all retries
   */
  async uploadReport(
    file: File,
    userId: string,
    maxRetries: number = this.MAX_RETRIES
  ): Promise<UploadResponse> {
    let lastError: AxiosError | null = null;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_id', userId);

        const response = await apiService.client.post('/api/reports/upload/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 60000, // 60 second timeout for file uploads
        });

        return response.data;
      } catch (error) {
        lastError = error as AxiosError;

        // Don't retry on client errors (4xx except 429)
        if (
          lastError.response?.status &&
          lastError.response.status >= 400 &&
          lastError.response.status < 500 &&
          lastError.response.status !== 429
        ) {
          break;
        }

        // Don't retry if this was the last attempt
        if (attempt === maxRetries) {
          break;
        }

        // Wait before retrying with exponential backoff
        const delay = getBackoffDelay(attempt, this.BASE_RETRY_DELAY);
        await sleep(delay);
      }
    }

    // All retries failed, throw error
    const errorInfo = parseErrorResponse(lastError!);
    throw new ReportServiceError(
      errorInfo.message,
      errorInfo.code,
      errorInfo.details,
      errorInfo.code === 'network_error' || errorInfo.code === 'timeout'
    );
  }

  /**
   * Get extraction status and results with retry logic
   * GET /api/reports/extract/{job_id}/
   * 
   * @param jobId - Extraction job ID
   * @param maxRetries - Maximum number of retry attempts (default: 3)
   * @returns Extraction status and data
   * @throws ReportServiceError on failure after all retries
   */
  async getExtractionStatus(
    jobId: string,
    maxRetries: number = this.MAX_RETRIES
  ): Promise<ExtractionStatus> {
    let lastError: AxiosError | null = null;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const response = await apiService.client.get(`/api/reports/extract/${jobId}/`);
        return response.data;
      } catch (error) {
        lastError = error as AxiosError;

        // Don't retry on client errors (4xx except 429)
        if (
          lastError.response?.status &&
          lastError.response.status >= 400 &&
          lastError.response.status < 500 &&
          lastError.response.status !== 429
        ) {
          break;
        }

        // Don't retry if this was the last attempt
        if (attempt === maxRetries) {
          break;
        }

        // Wait before retrying with exponential backoff
        const delay = getBackoffDelay(attempt, this.BASE_RETRY_DELAY);
        await sleep(delay);
      }
    }

    // All retries failed, throw error
    const errorInfo = parseErrorResponse(lastError!);
    throw new ReportServiceError(
      errorInfo.message,
      errorInfo.code,
      errorInfo.details,
      errorInfo.code === 'network_error' || errorInfo.code === 'timeout'
    );
  }

  /**
   * Get report metadata and download URL with retry logic
   * GET /api/reports/{report_id}/
   * 
   * @param reportId - Report ID
   * @param maxRetries - Maximum number of retry attempts (default: 3)
   * @returns Report metadata including download URL
   * @throws ReportServiceError on failure after all retries
   */
  async getReportMetadata(
    reportId: string,
    maxRetries: number = this.MAX_RETRIES
  ): Promise<ReportMetadata> {
    let lastError: AxiosError | null = null;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const response = await apiService.client.get(`/api/reports/${reportId}/`);
        return response.data;
      } catch (error) {
        lastError = error as AxiosError;

        // Don't retry on client errors (4xx except 429)
        if (
          lastError.response?.status &&
          lastError.response.status >= 400 &&
          lastError.response.status < 500 &&
          lastError.response.status !== 429
        ) {
          break;
        }

        // Don't retry if this was the last attempt
        if (attempt === maxRetries) {
          break;
        }

        // Wait before retrying with exponential backoff
        const delay = getBackoffDelay(attempt, this.BASE_RETRY_DELAY);
        await sleep(delay);
      }
    }

    // All retries failed, throw error
    const errorInfo = parseErrorResponse(lastError!);
    throw new ReportServiceError(
      errorInfo.message,
      errorInfo.code,
      errorInfo.details,
      errorInfo.code === 'network_error' || errorInfo.code === 'timeout'
    );
  }

  /**
   * Poll extraction status until complete or failed
   * 
   * @param jobId - Extraction job ID
   * @param pollInterval - Interval between polls in milliseconds (default: 2000)
   * @param maxPolls - Maximum number of polls (default: 30)
   * @returns Final extraction status
   * @throws ReportServiceError on timeout or failure
   */
  async pollExtractionStatus(
    jobId: string,
    pollInterval: number = 2000,
    maxPolls: number = 30
  ): Promise<ExtractionStatus> {
    for (let poll = 0; poll < maxPolls; poll++) {
      const status = await this.getExtractionStatus(jobId);

      if (status.status === 'complete' || status.status === 'failed') {
        return status;
      }

      // Wait before next poll
      await sleep(pollInterval);
    }

    throw new ReportServiceError(
      'Extraction polling timed out',
      'polling_timeout',
      { max_polls: maxPolls, poll_interval: pollInterval },
      false
    );
  }
}

export const reportService = new ReportService();
