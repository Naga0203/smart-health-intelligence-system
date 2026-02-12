// ============================================================================
// File Upload Validation Utility
// ============================================================================
// Provides validation for uploaded files including type, size, and basic security checks

/**
 * Allowed file types for medical reports
 */
export const ALLOWED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
  'application/dicom': ['.dcm', '.dicom'],
};

/**
 * Maximum file size (10MB)
 */
export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB in bytes

/**
 * Validation error types
 */
export enum FileValidationError {
  INVALID_TYPE = 'INVALID_TYPE',
  FILE_TOO_LARGE = 'FILE_TOO_LARGE',
  INVALID_NAME = 'INVALID_NAME',
  SUSPICIOUS_CONTENT = 'SUSPICIOUS_CONTENT',
}

/**
 * Validation result
 */
export interface ValidationResult {
  valid: boolean;
  error?: FileValidationError;
  message?: string;
}

/**
 * Sanitize file name to prevent path traversal and script injection
 */
export function sanitizeFileName(fileName: string): string {
  // Remove path separators
  let sanitized = fileName.replace(/[/\\]/g, '_');
  
  // Remove null bytes
  sanitized = sanitized.replace(/\0/g, '');
  
  // Remove leading dots (hidden files)
  sanitized = sanitized.replace(/^\.+/, '');
  
  // Limit length
  if (sanitized.length > 255) {
    const ext = sanitized.substring(sanitized.lastIndexOf('.'));
    sanitized = sanitized.substring(0, 255 - ext.length) + ext;
  }
  
  return sanitized || 'unnamed_file';
}

/**
 * Validate file type
 */
export function validateFileType(file: File): ValidationResult {
  const fileType = file.type.toLowerCase();
  const fileName = file.name.toLowerCase();
  
  // Check MIME type
  const allowedTypes = Object.keys(ALLOWED_FILE_TYPES);
  const isValidMimeType = allowedTypes.includes(fileType);
  
  // Check file extension
  const fileExtension = fileName.substring(fileName.lastIndexOf('.'));
  const isValidExtension = Object.values(ALLOWED_FILE_TYPES)
    .flat()
    .some(ext => fileExtension === ext);
  
  if (!isValidMimeType && !isValidExtension) {
    return {
      valid: false,
      error: FileValidationError.INVALID_TYPE,
      message: 'Invalid file type. Only PDF, JPG, PNG, and DICOM files are allowed.',
    };
  }
  
  return { valid: true };
}

/**
 * Validate file size
 */
export function validateFileSize(file: File): ValidationResult {
  if (file.size > MAX_FILE_SIZE) {
    const maxSizeMB = MAX_FILE_SIZE / (1024 * 1024);
    return {
      valid: false,
      error: FileValidationError.FILE_TOO_LARGE,
      message: `File size exceeds ${maxSizeMB}MB limit.`,
    };
  }
  
  return { valid: true };
}

/**
 * Validate file name for suspicious patterns
 */
export function validateFileName(file: File): ValidationResult {
  const fileName = file.name;
  
  // Check for suspicious patterns
  const suspiciousPatterns = [
    /\.\./,           // Path traversal
    /[<>:"|?*]/,      // Invalid characters
    /\0/,             // Null bytes
    /\.exe$/i,        // Executable
    /\.bat$/i,        // Batch file
    /\.cmd$/i,        // Command file
    /\.sh$/i,         // Shell script
    /\.js$/i,         // JavaScript
    /\.html$/i,       // HTML
    /\.php$/i,        // PHP
  ];
  
  for (const pattern of suspiciousPatterns) {
    if (pattern.test(fileName)) {
      return {
        valid: false,
        error: FileValidationError.INVALID_NAME,
        message: 'File name contains invalid or suspicious characters.',
      };
    }
  }
  
  return { valid: true };
}

/**
 * Basic content validation (check file header/magic bytes)
 */
export async function validateFileContent(file: File): Promise<ValidationResult> {
  return new Promise((resolve) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      const arrayBuffer = e.target?.result as ArrayBuffer;
      if (!arrayBuffer) {
        resolve({
          valid: false,
          error: FileValidationError.SUSPICIOUS_CONTENT,
          message: 'Unable to read file content.',
        });
        return;
      }
      
      const bytes = new Uint8Array(arrayBuffer);
      
      // Check for common file signatures (magic bytes)
      const signatures: { [key: string]: number[] } = {
        pdf: [0x25, 0x50, 0x44, 0x46], // %PDF
        jpeg: [0xFF, 0xD8, 0xFF],       // JPEG
        png: [0x89, 0x50, 0x4E, 0x47],  // PNG
      };
      
      // Verify file signature matches declared type
      let hasValidSignature = false;
      
      for (const [type, signature] of Object.entries(signatures)) {
        if (file.type.includes(type)) {
          const matches = signature.every((byte, index) => bytes[index] === byte);
          if (matches) {
            hasValidSignature = true;
            break;
          }
        }
      }
      
      // For DICOM files, we skip signature check as it's more complex
      if (file.type.includes('dicom') || file.name.endsWith('.dcm')) {
        hasValidSignature = true;
      }
      
      if (!hasValidSignature && file.type !== '') {
        resolve({
          valid: false,
          error: FileValidationError.SUSPICIOUS_CONTENT,
          message: 'File content does not match declared file type.',
        });
        return;
      }
      
      resolve({ valid: true });
    };
    
    reader.onerror = () => {
      resolve({
        valid: false,
        error: FileValidationError.SUSPICIOUS_CONTENT,
        message: 'Error reading file content.',
      });
    };
    
    // Read first 8 bytes for signature check
    reader.readAsArrayBuffer(file.slice(0, 8));
  });
}

/**
 * Comprehensive file validation
 */
export async function validateFile(file: File): Promise<ValidationResult> {
  // Validate file type
  const typeResult = validateFileType(file);
  if (!typeResult.valid) return typeResult;
  
  // Validate file size
  const sizeResult = validateFileSize(file);
  if (!sizeResult.valid) return sizeResult;
  
  // Validate file name
  const nameResult = validateFileName(file);
  if (!nameResult.valid) return nameResult;
  
  // Validate file content
  const contentResult = await validateFileContent(file);
  if (!contentResult.valid) return contentResult;
  
  return { valid: true };
}

/**
 * Validate multiple files
 */
export async function validateFiles(files: File[]): Promise<{
  valid: boolean;
  results: Array<{ file: File; result: ValidationResult }>;
}> {
  const results = await Promise.all(
    files.map(async (file) => ({
      file,
      result: await validateFile(file),
    }))
  );
  
  const allValid = results.every(({ result }) => result.valid);
  
  return { valid: allValid, results };
}
