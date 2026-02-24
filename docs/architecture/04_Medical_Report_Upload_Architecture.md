# Medical Report Upload & Extraction Architecture

## Overview

The Medical Report Upload and Extraction feature enables users to upload medical reports (PDF, JPG, PNG) and automatically extract structured medical data using Google Gemini AI. This feature integrates seamlessly with the existing multi-agent assessment system.

## Feature Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              MEDICAL REPORT UPLOAD SYSTEM                    │
└─────────────────────────────────────────────────────────────┘

User Uploads Report (PDF/Image)
    │
    ▼
┌─────────────────────┐
│  Frontend           │
│  FileUploadComponent│
│  • File validation  │
│  • Progress tracking│
└──────┬──────────────┘
       │
       │ HTTP POST (multipart/form-data)
       │
       ▼
┌─────────────────────┐
│  Upload API         │
│  /api/reports/upload│
│  • Auth check       │
│  • File validation  │
└──────┬──────────────┘
       │
       ├─────────────────────────┐
       │                         │
       ▼                         ▼
┌─────────────────┐      ┌─────────────────┐
│ Firebase Storage│      │ Firestore DB    │
│ • Store file    │      │ • Job metadata  │
│ • Generate URL  │      │ • Report info   │
└─────────────────┘      └──────┬──────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │ Extraction Agent│
                        │ • PDF parsing   │
                        │ • OCR (images)  │
                        │ • AI extraction │
                        └──────┬──────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │ Gemini AI       │
                        │ • Text analysis │
                        │ • Data structure│
                        └──────┬──────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │ Extracted Data  │
                        │ • Symptoms      │
                        │ • Vitals        │
                        │ • Lab results   │
                        │ • Medications   │
                        │ • Diagnoses     │
                        └──────┬──────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │ Frontend Form   │
                        │ Auto-population │
                        └─────────────────┘
```

## Component Architecture

### 1. Frontend Components

#### FileUploadComponent

**Purpose**: Handle file selection, upload, and extraction status polling

**State Management**:
```typescript
interface FileUploadState {
  selectedFiles: File[];
  uploadStatus: FileUploadStatus[];
  currentJobId: string | null;
  currentReportMetadata: ReportMetadata | null;
  extractionError: string | null;
  isPolling: boolean;
  retryCount: number;
}
```

**Workflow**:
```
User Selects File
    │
    ▼
File Validation
    │
    ├─ Valid → Continue
    └─ Invalid → Show Error
    │
    ▼
Upload to Backend
    │
    ▼
Receive Job ID
    │
    ▼
Start Status Polling (every 2 seconds)
    │
    ├─ Processing → Update Progress
    ├─ Complete → Trigger onUploadComplete
    └─ Failed → Show Error + Retry Option
```

#### AssessmentForm Enhancement

**Data Source Tracking**:
```typescript
interface FormState {
  // Field values
  symptomDescription: string;
  temperature: string;
  // ... other fields
  
  // Data source tracking
  dataSources: Map<string, 'manual' | 'extracted'>;
  
  // Extracted data
  extractedData: ExtractedMedicalData | null;
  reportMetadata: ReportMetadata | null;
}
```

**Visual Indicators**:
- Green badge for auto-filled fields
- Icon showing data source
- Editable fields with user override

### 2. Backend Services

#### FileStorageService

**Purpose**: Manage file upload and storage in Firebase Storage

**Algorithm**:
```
FUNCTION upload_file(file, user_id):
    // Step 1: Validation
    IF file.size > 10MB:
        RETURN error("File too large")
    
    IF file.type NOT IN ["application/pdf", "image/jpeg", "image/png"]:
        RETURN error("Invalid file type")
    
    // Step 2: Generate Unique ID
    report_id = generate_uuid()
    
    // Step 3: Storage Path
    storage_path = f"medical_reports/{user_id}/{report_id}.{file.extension}"
    
    // Step 4: Upload to Firebase Storage
    blob = storage_bucket.blob(storage_path)
    blob.upload_from_file(file)
    
    // Step 5: Generate Signed URL
    download_url = blob.generate_signed_url(expiration=3600)
    
    // Step 6: Store Metadata in Firestore
    metadata = {
        "report_id": report_id,
        "user_id": user_id,
        "file_name": file.name,
        "file_size": file.size,
        "file_type": file.type,
        "storage_path": storage_path,
        "upload_timestamp": current_timestamp(),
        "download_url": download_url
    }
    
    firestore.collection("medical_reports").document(report_id).set(metadata)
    
    RETURN {
        "report_id": report_id,
        "storage_path": storage_path,
        "download_url": download_url
    }
END FUNCTION
```

#### ExtractionJobManager

**Purpose**: Manage asynchronous extraction jobs

**Job Lifecycle**:
```
┌─────────────────────────────────────────────────────────────┐
│                    JOB LIFECYCLE                             │
└─────────────────────────────────────────────────────────────┘

PENDING
    │
    │ Start extraction
    ▼
PROCESSING
    │
    ├─ Success → COMPLETE
    └─ Failure → FAILED
    
Job States:
• PENDING: Job created, waiting to start
• PROCESSING: Extraction in progress
• COMPLETE: Extraction successful
• FAILED: Extraction failed
```

**Algorithm**:
```
FUNCTION create_job(report_id, user_id):
    job_id = generate_uuid()
    
    job_data = {
        "job_id": job_id,
        "report_id": report_id,
        "user_id": user_id,
        "status": "pending",
        "progress_percent": 0,
        "created_at": current_timestamp(),
        "updated_at": current_timestamp()
    }
    
    firestore.collection("extraction_jobs").document(job_id).set(job_data)
    
    // Trigger async extraction
    trigger_extraction_task(job_id, report_id)
    
    RETURN job_id
END FUNCTION

FUNCTION update_job_status(job_id, status, data=None):
    update_data = {
        "status": status,
        "updated_at": current_timestamp()
    }
    
    IF status == "complete":
        update_data["completed_at"] = current_timestamp()
        update_data["extracted_data"] = data
        update_data["progress_percent"] = 100
    
    IF status == "failed":
        update_data["error_info"] = data
    
    firestore.collection("extraction_jobs").document(job_id).update(update_data)
END FUNCTION
```

#### EnhancedExtractionAgent

**Purpose**: Extract structured medical data from reports using AI

**Extraction Pipeline**:
```
Report File
    │
    ▼
┌─────────────────────┐
│  File Type Detection│
│  • PDF              │
│  • Image (JPG/PNG)  │
└──────┬──────────────┘
       │
       ├─────────────────────┐
       │                     │
       ▼                     ▼
┌─────────────┐      ┌─────────────┐
│ PDF Parser  │      │ OCR Engine  │
│ (PyPDF2)    │      │ (Gemini)    │
└──────┬──────┘      └──────┬──────┘
       │                     │
       └──────────┬──────────┘
                  │
                  ▼
          ┌─────────────────┐
          │  Raw Text       │
          └──────┬──────────┘
                 │
                 ▼
          ┌─────────────────┐
          │  Gemini AI      │
          │  Extraction     │
          └──────┬──────────┘
                 │
                 ▼
          ┌─────────────────┐
          │  Structured Data│
          │  • Symptoms     │
          │  • Vitals       │
          │  • Lab results  │
          │  • Medications  │
          │  • Diagnoses    │
          └──────┬──────────┘
                 │
                 ▼
          ┌─────────────────┐
          │  Validation     │
          │  • Type check   │
          │  • Range check  │
          │  • Completeness │
          └──────┬──────────┘
                 │
                 ▼
          ┌─────────────────┐
          │  Confidence     │
          │  Scoring        │
          └─────────────────┘
```

**Extraction Algorithm**:
```
FUNCTION extract_from_report(file_stream, file_type):
    // Step 1: Text Extraction
    IF file_type == "PDF":
        raw_text = extract_pdf_text(file_stream)
    ELSE IF file_type IN ["JPG", "PNG"]:
        raw_text = perform_ocr(file_stream)
    ELSE:
        RETURN error("Unsupported file type")
    
    // Step 2: AI-Powered Extraction
    extraction_prompt = """
    You are a medical data extraction specialist. 
    Extract structured medical information from the following report:
    
    {raw_text}
    
    Extract and return as JSON:
    1. Symptoms: List of symptoms mentioned
    2. Vitals: 
       - blood_pressure (e.g., "120/80")
       - heart_rate (bpm)
       - temperature (°C)
       - weight (kg)
       - height (cm)
    3. Lab Results: Array of:
       - test_name
       - value
       - unit
       - reference_range
       - date (YYYY-MM-DD)
    4. Medications: Array of:
       - name
       - dosage
       - frequency
       - start_date (YYYY-MM-DD)
    5. Diagnoses: Array of:
       - condition
       - icd_code (if present)
       - date (YYYY-MM-DD)
       - status (active/resolved/chronic)
    
    Rules:
    - Only extract explicitly stated information
    - Use null for missing data
    - Standardize units (kg, cm, °C)
    - Include confidence level (0.0-1.0) for each field
    """
    
    ai_response = gemini_client.generate(extraction_prompt)
    extracted_data = parse_json(ai_response)
    
    // Step 3: Validation
    validation_result = validate_extracted_data(extracted_data)
    IF NOT validation_result.is_valid:
        RETURN error(validation_result.errors)
    
    // Step 4: Confidence Scoring
    confidence_scores = calculate_confidence_scores(
        extracted_data, 
        raw_text
    )
    
    // Step 5: Return Structured Data
    RETURN {
        "success": True,
        "extracted_data": {
            "symptoms": extracted_data.symptoms,
            "vitals": extracted_data.vitals,
            "lab_results": extracted_data.lab_results,
            "medications": extracted_data.medications,
            "diagnoses": extracted_data.diagnoses,
            "confidence_scores": confidence_scores
        },
        "extraction_metadata": {
            "extraction_time_seconds": elapsed_time,
            "ocr_used": file_type != "PDF",
            "pages_processed": count_pages(file_stream),
            "gemini_model": "gemini-pro"
        }
    }
END FUNCTION
```

### 3. Data Models

#### ExtractedMedicalData

```typescript
interface ExtractedMedicalData {
  symptoms: string[];
  
  vitals: {
    bloodPressure?: string;      // "120/80"
    heartRate?: number;           // bpm
    temperature?: number;         // °C
    weight?: number;              // kg
    height?: number;              // cm
  };
  
  labResults: Array<{
    testName: string;
    value: number;
    unit: string;
    referenceRange: string;
    date: string;                 // YYYY-MM-DD
  }>;
  
  medications: Array<{
    name: string;
    dosage: string;
    frequency: string;
    startDate: string;            // YYYY-MM-DD
  }>;
  
  diagnoses: Array<{
    condition: string;
    icdCode?: string;
    date: string;                 // YYYY-MM-DD
    status: 'active' | 'resolved' | 'chronic';
  }>;
  
  confidenceScores: {
    overall: number;              // 0.0-1.0
    symptoms: number;
    vitals: number;
    labResults: number;
    medications: number;
    diagnoses: number;
  };
}
```

#### ReportMetadata

```typescript
interface ReportMetadata {
  reportId: string;
  userId: string;
  fileName: string;
  fileSize: number;
  fileType: string;
  uploadTimestamp: string;
  downloadUrl: string;
  extractionJobId: string;
  associatedAssessmentId?: string;
}
```

## API Endpoints

### POST /api/reports/upload/

**Purpose**: Upload medical report file

**Request**:
```http
POST /api/reports/upload/
Content-Type: multipart/form-data
Authorization: Bearer <jwt_token>

file: <binary>
user_id: string
```

**Response** (201 Created):
```json
{
  "success": true,
  "job_id": "uuid",
  "report_id": "uuid",
  "file_name": "report.pdf",
  "file_size": 1024000,
  "upload_timestamp": "2024-01-15T10:30:00Z",
  "status": "processing",
  "estimated_completion_seconds": 10
}
```

### GET /api/reports/extract/{job_id}/

**Purpose**: Check extraction status and retrieve results

**Request**:
```http
GET /api/reports/extract/{job_id}/
Authorization: Bearer <jwt_token>
```

**Response - Processing** (200 OK):
```json
{
  "job_id": "uuid",
  "status": "processing",
  "progress_percent": 50,
  "message": "Extracting medical data..."
}
```

**Response - Complete** (200 OK):
```json
{
  "job_id": "uuid",
  "status": "complete",
  "extracted_data": {
    "symptoms": ["headache", "fever"],
    "vitals": {
      "temperature": 38.5,
      "heart_rate": 85
    },
    "lab_results": [],
    "medications": [],
    "diagnoses": [],
    "confidence_scores": {
      "overall": 0.9,
      "symptoms": 0.95,
      "vitals": 0.92,
      "lab_results": 0.0,
      "medications": 0.0,
      "diagnoses": 0.0
    }
  },
  "extraction_metadata": {
    "extraction_time_seconds": 8.5,
    "ocr_used": false,
    "pages_processed": 2,
    "gemini_model": "gemini-pro"
  }
}
```

**Response - Failed** (200 OK):
```json
{
  "job_id": "uuid",
  "status": "failed",
  "error_code": "unreadable",
  "message": "Unable to extract text from report",
  "partial_data": null
}
```

### GET /api/reports/{report_id}/

**Purpose**: Retrieve report metadata and download URL

**Request**:
```http
GET /api/reports/{report_id}/
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "report_id": "uuid",
  "user_id": "user123",
  "file_name": "lab_report.pdf",
  "file_size": 1024000,
  "file_type": "application/pdf",
  "upload_timestamp": "2024-01-15T10:30:00Z",
  "download_url": "https://storage.googleapis.com/...",
  "extraction_job_id": "uuid",
  "associated_assessment_id": "uuid"
}
```

## Integration with Assessment Flow

### Data Flow with Report Upload

```
User Uploads Report
    │
    ▼
Extraction Complete
    │
    ▼
Form Auto-Population
    │
    ▼
User Reviews/Edits Data
    │
    ▼
Submit Assessment
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Assessment Submission Payload                               │
├─────────────────────────────────────────────────────────────┤
│  {                                                           │
│    "symptoms": "headache, fever",                           │
│    "age": 30,                                               │
│    "gender": "male",                                        │
│                                                              │
│    "report_metadata": {                                     │
│      "report_id": "uuid",                                   │
│      "extraction_job_id": "uuid",                           │
│      "has_extracted_data": true                             │
│    },                                                        │
│                                                              │
│    "extracted_data": {                                      │
│      "symptoms": ["headache", "fever"],                     │
│      "vitals": { "temperature": 38.5 },                     │
│      ...                                                     │
│    },                                                        │
│                                                              │
│    "data_sources": {                                        │
│      "symptomDescription": "extracted",                     │
│      "temperature": "extracted",                            │
│      "age": "manual"                                        │
│    }                                                         │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
Orchestrator Agent
    │
    ├─ Merge extracted + manual data
    ├─ Prioritize user edits
    └─ Process through agent pipeline
    │
    ▼
Store Assessment with Report Reference
```

### Data Merging Strategy

**Algorithm**:
```
FUNCTION merge_data_sources(manual_data, extracted_data, data_sources):
    merged_data = {}
    
    FOR field IN all_fields:
        source = data_sources.get(field)
        
        IF source == "manual":
            // User manually entered/edited
            merged_data[field] = manual_data[field]
        
        ELSE IF source == "extracted":
            // Auto-filled from report
            IF manual_data[field] is not empty:
                // User edited after extraction
                merged_data[field] = manual_data[field]
            ELSE:
                // Use extracted value
                merged_data[field] = extracted_data[field]
        
        ELSE:
            // No source specified, use manual
            merged_data[field] = manual_data[field]
    
    RETURN merged_data
END FUNCTION
```

## Error Handling

### Error Categories

1. **Upload Errors**:
   - File too large (> 10MB)
   - Invalid file format
   - Network failure
   - Storage service unavailable

2. **Extraction Errors**:
   - Unreadable file (corrupted)
   - No medical data found
   - OCR failure
   - Gemini API timeout
   - Partial extraction

3. **Validation Errors**:
   - Invalid data types
   - Out-of-range values
   - Missing required fields

### Error Recovery

```
Error Occurs
    │
    ▼
┌─────────────────────┐
│  Error Handler      │
└──────┬──────────────┘
       │
       ├─ Retryable? (network, timeout)
       │  └─ Yes → Retry with backoff (max 3 attempts)
       │  └─ No → Show error to user
       │
       ├─ Partial Data Available?
       │  └─ Yes → Offer to use partial data
       │  └─ No → Suggest manual entry
       │
       └─ Log Error for Monitoring
```

## Performance Considerations

### Optimization Strategies

1. **Async Processing**: Extraction runs in background
2. **Status Polling**: Frontend polls every 2 seconds
3. **Timeout Handling**: 10-second timeout for extraction
4. **Caching**: Cache extraction results
5. **Parallel Processing**: Multiple reports processed concurrently

### Performance Targets

```
Performance Metrics:
├─ Upload Time: < 5 seconds (for 10MB file)
├─ Extraction Time: < 10 seconds
├─ Status Poll Interval: 2 seconds
├─ Max Poll Attempts: 60 (2 minutes total)
└─ Concurrent Uploads: 10 per user
```

## Security Considerations

### File Security

1. **File Validation**: Type and size checks
2. **Virus Scanning**: (Future enhancement)
3. **Access Control**: User can only access own reports
4. **Signed URLs**: Time-limited download URLs (1 hour)
5. **Encryption**: Files encrypted at rest in Firebase Storage

### Data Privacy

1. **HIPAA Compliance**: Secure storage and transmission
2. **Data Isolation**: User data segregated
3. **Audit Logging**: Track all file access
4. **Data Retention**: Configurable retention policy
5. **Right to Delete**: Users can delete their reports

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Maintained By**: SymptomSense Development Team
