// ============================================================================
// Medical Report Upload and Extraction - Type Definitions
// ============================================================================

/**
 * Vitals data extracted from medical reports
 */
export interface Vitals {
  bloodPressure?: string;
  heartRate?: number;
  temperature?: number;
  weight?: number;
  height?: number;
}

/**
 * Lab result from medical report
 */
export interface LabResult {
  testName: string;
  value: number;
  unit: string;
  referenceRange: string;
  date: string;
}

/**
 * Medication information from medical report
 */
export interface Medication {
  name: string;
  dosage: string;
  frequency: string;
  startDate: string;
}

/**
 * Diagnosis information from medical report
 */
export interface Diagnosis {
  condition: string;
  icdCode?: string;
  date: string;
  status: 'active' | 'resolved' | 'chronic';
}

/**
 * Confidence scores for extracted data categories
 */
export interface ConfidenceScores {
  overall: number;
  symptoms: number;
  vitals: number;
  labResults: number;
  medications: number;
  diagnoses: number;
}

/**
 * Complete extracted medical data structure
 */
export interface ExtractedMedicalData {
  symptoms: string[];
  vitals: Vitals;
  labResults: LabResult[];
  medications: Medication[];
  diagnoses: Diagnosis[];
  confidenceScores: ConfidenceScores;
}

/**
 * Metadata for uploaded medical report
 */
export interface ReportMetadata {
  reportId: string;
  fileName: string;
  fileSize: number;
  uploadTimestamp: string;
  extractionJobId: string;
}

/**
 * Upload error information
 */
export interface UploadError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

/**
 * Validation result for file or data validation
 */
export interface ValidationResult {
  valid: boolean;
  errors?: string[];
}
