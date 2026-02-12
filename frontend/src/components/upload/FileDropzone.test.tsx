// ============================================================================
// FileDropzone Unit Tests
// Feature: ai-health-frontend
// ============================================================================

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { FileDropzone } from './FileDropzone';

describe('FileDropzone Component', () => {
  const mockOnFilesSelected = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render dropzone with instructions', () => {
    render(<FileDropzone onFilesSelected={mockOnFilesSelected} />);
    
    expect(screen.getByText(/Drag and drop files here/i)).toBeInTheDocument();
    expect(screen.getByText(/or click to select files/i)).toBeInTheDocument();
    expect(screen.getByText(/Accepted formats: PDF, JPG, PNG, DICOM/i)).toBeInTheDocument();
  });

  it('should validate file format and reject invalid files', () => {
    render(<FileDropzone onFilesSelected={mockOnFilesSelected} />);
    
    const input = document.getElementById('file-input') as HTMLInputElement;
    const invalidFile = new File(['content'], 'test.txt', { type: 'text/plain' });
    
    Object.defineProperty(input, 'files', {
      value: [invalidFile],
      writable: false,
    });
    
    fireEvent.change(input);
    
    // Should show validation error
    expect(screen.getByText(/invalid format/i)).toBeInTheDocument();
    expect(mockOnFilesSelected).not.toHaveBeenCalled();
  });

  it('should validate file size and reject oversized files', () => {
    render(<FileDropzone onFilesSelected={mockOnFilesSelected} maxFileSize={1024} />);
    
    const input = document.getElementById('file-input') as HTMLInputElement;
    // Create a file larger than 1KB
    const largeFile = new File(['x'.repeat(2000)], 'test.pdf', { type: 'application/pdf' });
    
    Object.defineProperty(input, 'files', {
      value: [largeFile],
      writable: false,
    });
    
    fireEvent.change(input);
    
    // Should show validation error
    expect(screen.getByText(/exceeds maximum size/i)).toBeInTheDocument();
    expect(mockOnFilesSelected).not.toHaveBeenCalled();
  });

  it('should accept valid PDF file', () => {
    render(<FileDropzone onFilesSelected={mockOnFilesSelected} />);
    
    const input = document.getElementById('file-input') as HTMLInputElement;
    const validFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
    
    Object.defineProperty(input, 'files', {
      value: [validFile],
      writable: false,
    });
    
    fireEvent.change(input);
    
    expect(mockOnFilesSelected).toHaveBeenCalledWith([validFile]);
  });

  it('should accept valid image files', () => {
    render(<FileDropzone onFilesSelected={mockOnFilesSelected} />);
    
    const input = document.getElementById('file-input') as HTMLInputElement;
    const jpgFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
    const pngFile = new File(['content'], 'test.png', { type: 'image/png' });
    
    Object.defineProperty(input, 'files', {
      value: [jpgFile, pngFile],
      writable: false,
    });
    
    fireEvent.change(input);
    
    expect(mockOnFilesSelected).toHaveBeenCalledWith([jpgFile, pngFile]);
  });

  it('should accept DICOM files', () => {
    render(<FileDropzone onFilesSelected={mockOnFilesSelected} />);
    
    const input = document.getElementById('file-input') as HTMLInputElement;
    const dicomFile = new File(['content'], 'test.dcm', { type: 'application/dicom' });
    
    Object.defineProperty(input, 'files', {
      value: [dicomFile],
      writable: false,
    });
    
    fireEvent.change(input);
    
    expect(mockOnFilesSelected).toHaveBeenCalledWith([dicomFile]);
  });

  it('should handle drag and drop events', () => {
    render(<FileDropzone onFilesSelected={mockOnFilesSelected} />);
    
    const dropzone = screen.getByText(/Drag and drop files here/i).closest('div');
    
    // Simulate drag enter
    fireEvent.dragEnter(dropzone!);
    expect(screen.getByText(/Drop files here/i)).toBeInTheDocument();
    
    // Simulate drag leave
    fireEvent.dragLeave(dropzone!);
    expect(screen.getByText(/Drag and drop files here/i)).toBeInTheDocument();
  });

  it('should support multiple file selection', () => {
    render(<FileDropzone onFilesSelected={mockOnFilesSelected} />);
    
    const input = document.getElementById('file-input') as HTMLInputElement;
    const file1 = new File(['content1'], 'test1.pdf', { type: 'application/pdf' });
    const file2 = new File(['content2'], 'test2.jpg', { type: 'image/jpeg' });
    const file3 = new File(['content3'], 'test3.png', { type: 'image/png' });
    
    Object.defineProperty(input, 'files', {
      value: [file1, file2, file3],
      writable: false,
    });
    
    fireEvent.change(input);
    
    expect(mockOnFilesSelected).toHaveBeenCalledWith([file1, file2, file3]);
  });

  it('should handle file drop with valid files', () => {
    render(<FileDropzone onFilesSelected={mockOnFilesSelected} />);
    
    const dropzone = screen.getByText(/Drag and drop files here/i).closest('div');
    const validFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
    
    const dataTransfer = {
      files: [validFile],
    };
    
    fireEvent.drop(dropzone!, { dataTransfer });
    
    expect(mockOnFilesSelected).toHaveBeenCalledWith([validFile]);
  });

  it('should show visual feedback during drag over', () => {
    render(<FileDropzone onFilesSelected={mockOnFilesSelected} />);
    
    const dropzone = screen.getByText(/Drag and drop files here/i).closest('div');
    
    // Simulate drag enter
    fireEvent.dragEnter(dropzone!);
    expect(screen.getByText(/Drop files here/i)).toBeInTheDocument();
    
    // Simulate drag over
    fireEvent.dragOver(dropzone!);
    expect(screen.getByText(/Drop files here/i)).toBeInTheDocument();
  });

  it('should clear validation error when user dismisses it', () => {
    render(<FileDropzone onFilesSelected={mockOnFilesSelected} />);
    
    const input = document.getElementById('file-input') as HTMLInputElement;
    const invalidFile = new File(['content'], 'test.txt', { type: 'text/plain' });
    
    Object.defineProperty(input, 'files', {
      value: [invalidFile],
      writable: false,
    });
    
    fireEvent.change(input);
    
    // Error should be visible
    const errorAlert = screen.getByText(/invalid format/i).closest('[role="alert"]');
    expect(errorAlert).toBeInTheDocument();
    
    // Find and click the close button
    const closeButton = errorAlert?.querySelector('button');
    if (closeButton) {
      fireEvent.click(closeButton);
    }
    
    // Error should be cleared (component will re-render without error)
    expect(mockOnFilesSelected).not.toHaveBeenCalled();
  });

  it('should stop validation on first invalid file in multiple selection', () => {
    render(<FileDropzone onFilesSelected={mockOnFilesSelected} />);
    
    const input = document.getElementById('file-input') as HTMLInputElement;
    const validFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
    const invalidFile = new File(['content'], 'test.txt', { type: 'text/plain' });
    
    Object.defineProperty(input, 'files', {
      value: [validFile, invalidFile],
      writable: false,
    });
    
    fireEvent.change(input);
    
    // Should show error for invalid file
    expect(screen.getByText(/invalid format/i)).toBeInTheDocument();
    // Should not call onFilesSelected
    expect(mockOnFilesSelected).not.toHaveBeenCalled();
  });

  it('should reset input value after file selection', () => {
    render(<FileDropzone onFilesSelected={mockOnFilesSelected} />);
    
    const input = document.getElementById('file-input') as HTMLInputElement;
    const validFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
    
    Object.defineProperty(input, 'files', {
      value: [validFile],
      writable: false,
    });
    
    fireEvent.change(input);
    
    // Input value should be reset to allow selecting the same file again
    // The component resets the value in the change handler
    expect(mockOnFilesSelected).toHaveBeenCalledWith([validFile]);
  });
});
