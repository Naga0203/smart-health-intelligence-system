// ============================================================================
// AI Health Intelligence Platform - TypeScript Type Definitions
// ============================================================================

// Authentication Types
export interface User {
  uid: string;
  email: string;
  displayName: string | null;
  photoURL: string | null;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

// User Profile Types
export interface UserProfile {
  uid: string;
  email: string;
  display_name?: string;
  photo_url?: string;
  email_verified: boolean;
  created_at: string;
  updated_at: string;
  last_login: string;
  phone_number?: string;
  date_of_birth?: string;
  gender?: 'male' | 'female' | 'other' | 'prefer_not_to_say';
  address?: Record<string, any>;
  emergency_contact?: Record<string, any>;
  medical_history?: string[];
  allergies?: string[];
  current_medications?: string[];
}

export interface UserStatistics {
  total_assessments: number;
  assessments_by_confidence: {
    LOW: number;
    MEDIUM: number;
    HIGH: number;
  };
  most_common_diseases: Array<{
    disease: string;
    count: number;
  }>;
  last_assessment_date: string | null;
  account_age_days: number;
}

// Assessment Input Types
export interface SymptomInput {
  name: string;
  severity: number; // 1-10
  duration: {
    value: number;
    unit: 'hours' | 'days' | 'weeks' | 'months';
  };
}

export interface DemographicData {
  age: number;
  gender: 'male' | 'female' | 'other';
  medical_history?: string[];
}

export interface VitalsData {
  temperature?: number;
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  heart_rate?: number;
  respiratory_rate?: number;
}

export interface AssessmentRequest {
  symptoms: string[];
  age: number;
  gender: 'male' | 'female' | 'other';
  additional_info?: Record<string, any>;
}

// Assessment Results Types
export interface RiskAssessment {
  status: string;
  confidence: 'LOW' | 'MEDIUM' | 'HIGH';
  message: string;
  user_id?: string;
  assessment_id: string;
  prediction: {
    disease: string;
    probability: number;
    probability_percent: number;
    confidence: 'LOW' | 'MEDIUM' | 'HIGH';
    model_version?: string;
  };
  extraction?: {
    confidence: number;
    method: string;
    extracted_features?: string[];
  };
  explanation?: {
    text: string;
    generated_by: string;
    confidence: 'LOW' | 'MEDIUM' | 'HIGH';
  };
  recommendations?: {
    items: string[];
    urgency: 'low' | 'medium' | 'high';
    confidence: 'LOW' | 'MEDIUM' | 'HIGH';
  };
  treatment_info?: TreatmentInfo;
  risk_factors?: string[];
  disclaimer: string;
  metadata: {
    processing_time_seconds?: number;
    timestamp: string;
    storage_ids?: Record<string, string>;
    pipeline_version?: string;
  };
}

export interface TreatmentInfo {
  allopathy?: TreatmentDetail;
  ayurveda?: TreatmentDetail;
  homeopathy?: TreatmentDetail;
  lifestyle?: TreatmentDetail;
}

export interface TreatmentDetail {
  approach: string;
  focus: string;
  disclaimer: string;
}

// Assessment History Types
export interface AssessmentHistoryItem {
  id: string;
  created_at: string;
  disease: string;
  probability: number;
  confidence: 'LOW' | 'MEDIUM' | 'HIGH';
  symptoms: string[];
  status: string;
}

export interface AssessmentHistory {
  total: number;
  page: number;
  page_size: number;
  assessments: AssessmentHistoryItem[];
}

// System Status Types
export interface SystemStatus {
  status: 'operational' | 'degraded' | 'error';
  version: string;
  components: {
    orchestrator?: { status: string; version?: string };
    predictor?: { status: string; models_loaded?: number };
    database?: { status: string; type?: string };
    gemini_ai?: { status: string };
  };
  timestamp: string;
}

export interface ModelInfo {
  model_loaded: boolean;
  model_type: string;
  num_features: number;
  num_diseases: number;
  device?: string;
}

export interface Disease {
  name: string;
  category?: string;
  symptoms?: string[];
}

export interface DiseasesResponse {
  total: number;
  diseases: string[];
}

// Prediction Types
export interface Prediction {
  disease: string;
  probability: number;
  rank: number;
}

// Notification Types
export interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  dismissible: boolean;
  timestamp: string;
}

// API Error Types
export interface APIError {
  error: string;
  message: string;
  details?: any;
  status_code: number;
  wait_seconds?: number;
}

// Pagination Types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
