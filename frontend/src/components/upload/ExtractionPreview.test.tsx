// ============================================================================
// ExtractionPreview Unit Tests
// Feature: ai-health-frontend
// ============================================================================

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ExtractionPreview, ExtractedData } from './ExtractionPreview';

describe('ExtractionPreview Component', () => {
  const mockOnConfirm = vi.fn();
  const mockOnCancel = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render nothing when no extracted data is provided', () => {
    const { container } = render(
      <ExtractionPreview
        extractedData={[]}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );
    expect(container.firstChild).toBeNull();
  });

  it('should display extracted data preview', () => {
    const extractedData: ExtractedData[] = [
      {
        fileName: 'test.pdf',
        confidence: 85,
        method: 'OCR',
        extractedFeatures: ['symptoms', 'vitals'],
        symptoms: ['fever', 'cough'],
      },
    ];

    render(
      <ExtractionPreview
        extractedData={extractedData}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText('Extracted Data Preview')).toBeInTheDocument();
    expect(screen.getByText('test.pdf')).toBeInTheDocument();
  });

  it('should display confidence indicator', () => {
    const extractedData: ExtractedData[] = [
      {
        fileName: 'test.pdf',
        confidence: 85,
        method: 'OCR',
        extractedFeatures: ['symptoms'],
      },
    ];

    render(
      <ExtractionPreview
        extractedData={extractedData}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText(/High Confidence/i)).toBeInTheDocument();
    expect(screen.getByText(/85%/i)).toBeInTheDocument();
  });

  it('should show warning for low confidence extractions', () => {
    const extractedData: ExtractedData[] = [
      {
        fileName: 'test.pdf',
        confidence: 40,
        method: 'OCR',
        extractedFeatures: ['symptoms'],
      },
    ];

    render(
      <ExtractionPreview
        extractedData={extractedData}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    // Use getAllByText since "Low Confidence" appears multiple times
    const lowConfidenceElements = screen.getAllByText(/Low Confidence/i);
    expect(lowConfidenceElements.length).toBeGreaterThan(0);
    expect(screen.getByText(/review the data carefully/i)).toBeInTheDocument();
  });

  it('should display extracted symptoms', () => {
    const extractedData: ExtractedData[] = [
      {
        fileName: 'test.pdf',
        confidence: 85,
        method: 'OCR',
        extractedFeatures: ['symptoms'],
        symptoms: ['fever', 'cough', 'headache'],
      },
    ];

    render(
      <ExtractionPreview
        extractedData={extractedData}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText('Symptoms Detected:')).toBeInTheDocument();
    expect(screen.getByText('fever')).toBeInTheDocument();
    expect(screen.getByText('cough')).toBeInTheDocument();
    expect(screen.getByText('headache')).toBeInTheDocument();
  });

  it('should display extracted vitals', () => {
    const extractedData: ExtractedData[] = [
      {
        fileName: 'test.pdf',
        confidence: 85,
        method: 'OCR',
        extractedFeatures: ['vitals'],
        vitals: {
          temperature: 98.6,
          bloodPressureSystolic: 120,
          bloodPressureDiastolic: 80,
          heartRate: 72,
          respiratoryRate: 16,
        },
      },
    ];

    render(
      <ExtractionPreview
        extractedData={extractedData}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText('Vitals:')).toBeInTheDocument();
    expect(screen.getByText(/Temperature: 98.6°F/i)).toBeInTheDocument();
    expect(screen.getByText(/Blood Pressure: 120\/80 mmHg/i)).toBeInTheDocument();
    expect(screen.getByText(/Heart Rate: 72 bpm/i)).toBeInTheDocument();
    expect(screen.getByText(/Respiratory Rate: 16 breaths\/min/i)).toBeInTheDocument();
  });

  it('should display extracted demographics', () => {
    const extractedData: ExtractedData[] = [
      {
        fileName: 'test.pdf',
        confidence: 85,
        method: 'OCR',
        extractedFeatures: ['demographics'],
        demographics: {
          age: 35,
          gender: 'male',
        },
      },
    ];

    render(
      <ExtractionPreview
        extractedData={extractedData}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText('Demographics:')).toBeInTheDocument();
    expect(screen.getByText(/Age: 35/i)).toBeInTheDocument();
    expect(screen.getByText(/Gender: male/i)).toBeInTheDocument();
  });

  it('should display medical history', () => {
    const extractedData: ExtractedData[] = [
      {
        fileName: 'test.pdf',
        confidence: 85,
        method: 'OCR',
        extractedFeatures: ['medical_history'],
        medicalHistory: ['diabetes', 'hypertension'],
      },
    ];

    render(
      <ExtractionPreview
        extractedData={extractedData}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText('Medical History:')).toBeInTheDocument();
    expect(screen.getByText('diabetes')).toBeInTheDocument();
    expect(screen.getByText('hypertension')).toBeInTheDocument();
  });

  it('should display additional notes', () => {
    const extractedData: ExtractedData[] = [
      {
        fileName: 'test.pdf',
        confidence: 85,
        method: 'OCR',
        extractedFeatures: ['notes'],
        notes: 'Patient reports feeling unwell for 3 days',
      },
    ];

    render(
      <ExtractionPreview
        extractedData={extractedData}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText('Additional Notes:')).toBeInTheDocument();
    expect(screen.getByText('Patient reports feeling unwell for 3 days')).toBeInTheDocument();
  });

  it('should call onConfirm when confirm button is clicked', () => {
    const extractedData: ExtractedData[] = [
      {
        fileName: 'test.pdf',
        confidence: 85,
        method: 'OCR',
        extractedFeatures: ['symptoms'],
      },
    ];

    render(
      <ExtractionPreview
        extractedData={extractedData}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    const confirmButton = screen.getByText('Confirm and Submit for Analysis');
    fireEvent.click(confirmButton);

    expect(mockOnConfirm).toHaveBeenCalledTimes(1);
  });

  it('should call onCancel when cancel button is clicked', () => {
    const extractedData: ExtractedData[] = [
      {
        fileName: 'test.pdf',
        confidence: 85,
        method: 'OCR',
        extractedFeatures: ['symptoms'],
      },
    ];

    render(
      <ExtractionPreview
        extractedData={extractedData}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalledTimes(1);
  });

  it('should disable buttons when loading', () => {
    const extractedData: ExtractedData[] = [
      {
        fileName: 'test.pdf',
        confidence: 85,
        method: 'OCR',
        extractedFeatures: ['symptoms'],
      },
    ];

    render(
      <ExtractionPreview
        extractedData={extractedData}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
        loading={true}
      />
    );

    const confirmButton = screen.getByText('Submitting...');
    const cancelButton = screen.getByText('Cancel');

    expect(confirmButton).toBeDisabled();
    expect(cancelButton).toBeDisabled();
  });

  it('should handle multiple files with different confidence levels', () => {
    const extractedData: ExtractedData[] = [
      {
        fileName: 'high-confidence.pdf',
        confidence: 85,
        method: 'OCR',
        extractedFeatures: ['symptoms'],
        symptoms: ['fever'],
      },
      {
        fileName: 'medium-confidence.pdf',
        confidence: 60,
        method: 'OCR',
        extractedFeatures: ['symptoms'],
        symptoms: ['cough'],
      },
      {
        fileName: 'low-confidence.pdf',
        confidence: 40,
        method: 'OCR',
        extractedFeatures: ['symptoms'],
        symptoms: ['headache'],
      },
    ];

    render(
      <ExtractionPreview
        extractedData={extractedData}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText('high-confidence.pdf')).toBeInTheDocument();
    expect(screen.getByText('medium-confidence.pdf')).toBeInTheDocument();
    expect(screen.getByText('low-confidence.pdf')).toBeInTheDocument();
    expect(screen.getByText(/High Confidence/i)).toBeInTheDocument();
    expect(screen.getByText(/Medium Confidence/i)).toBeInTheDocument();
    // Use getAllByText since "Low Confidence" appears multiple times
    const lowConfidenceElements = screen.getAllByText(/Low Confidence/i);
    expect(lowConfidenceElements.length).toBeGreaterThan(0);
  });

  it('should show warning when any file has low confidence', () => {
    const extractedData: ExtractedData[] = [
      {
        fileName: 'good.pdf',
        confidence: 85,
        method: 'OCR',
        extractedFeatures: ['symptoms'],
      },
      {
        fileName: 'bad.pdf',
        confidence: 40,
        method: 'OCR',
        extractedFeatures: ['symptoms'],
      },
    ];

    render(
      <ExtractionPreview
        extractedData={extractedData}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    // Should show warning at the top
    const warnings = screen.getAllByText(/low confidence/i);
    expect(warnings.length).toBeGreaterThan(0);
  });

  it('should display extraction method', () => {
    const extractedData: ExtractedData[] = [
      {
        fileName: 'test.pdf',
        confidence: 85,
        method: 'Advanced OCR with ML',
        extractedFeatures: ['symptoms'],
      },
    ];

    render(
      <ExtractionPreview
        extractedData={extractedData}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText(/Extraction Method: Advanced OCR with ML/i)).toBeInTheDocument();
  });

  it('should display extracted features list', () => {
    const extractedData: ExtractedData[] = [
      {
        fileName: 'test.pdf',
        confidence: 85,
        method: 'OCR',
        extractedFeatures: ['symptoms', 'vitals', 'demographics'],
      },
    ];

    render(
      <ExtractionPreview
        extractedData={extractedData}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText(/Extracted Features: symptoms, vitals, demographics/i)).toBeInTheDocument();
  });
});
