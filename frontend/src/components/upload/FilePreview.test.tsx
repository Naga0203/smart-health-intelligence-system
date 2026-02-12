// ============================================================================
// FilePreview Unit Tests
// Feature: ai-health-frontend
// ============================================================================

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { FilePreview } from './FilePreview';

describe('FilePreview Component', () => {
  const mockOnRemove = vi.fn();

  it('should render nothing when no files are provided', () => {
    const { container } = render(<FilePreview files={[]} onRemove={mockOnRemove} />);
    expect(container.firstChild).toBeNull();
  });

  it('should display file previews for uploaded files', () => {
    const files = [
      new File(['content1'], 'test1.pdf', { type: 'application/pdf' }),
      new File(['content2'], 'test2.jpg', { type: 'image/jpeg' }),
    ];

    render(<FilePreview files={files} onRemove={mockOnRemove} />);

    expect(screen.getByText('Selected Files (2)')).toBeInTheDocument();
    expect(screen.getByText('test1.pdf')).toBeInTheDocument();
    expect(screen.getByText('test2.jpg')).toBeInTheDocument();
  });

  it('should display file size and format', () => {
    const file = new File(['x'.repeat(1024)], 'test.pdf', { type: 'application/pdf' });

    render(<FilePreview files={[file]} onRemove={mockOnRemove} />);

    expect(screen.getByText('1 KB')).toBeInTheDocument();
    expect(screen.getByText('PDF')).toBeInTheDocument();
  });

  it('should call onRemove when remove button is clicked', () => {
    const files = [
      new File(['content'], 'test.pdf', { type: 'application/pdf' }),
    ];

    render(<FilePreview files={files} onRemove={mockOnRemove} />);

    const removeButton = screen.getByLabelText('Remove test.pdf');
    fireEvent.click(removeButton);

    expect(mockOnRemove).toHaveBeenCalledWith(0);
  });

  it('should display appropriate icons for different file types', () => {
    const files = [
      new File(['content'], 'test.pdf', { type: 'application/pdf' }),
      new File(['content'], 'test.jpg', { type: 'image/jpeg' }),
      new File(['content'], 'test.dcm', { type: 'application/dicom' }),
    ];

    render(<FilePreview files={files} onRemove={mockOnRemove} />);

    // All files should be displayed
    expect(screen.getByText('test.pdf')).toBeInTheDocument();
    expect(screen.getByText('test.jpg')).toBeInTheDocument();
    expect(screen.getByText('test.dcm')).toBeInTheDocument();
  });

  it('should handle removal of multiple files correctly', () => {
    const files = [
      new File(['content1'], 'test1.pdf', { type: 'application/pdf' }),
      new File(['content2'], 'test2.jpg', { type: 'image/jpeg' }),
      new File(['content3'], 'test3.png', { type: 'image/png' }),
    ];

    render(<FilePreview files={files} onRemove={mockOnRemove} />);

    // Remove second file
    const removeButton = screen.getByLabelText('Remove test2.jpg');
    fireEvent.click(removeButton);

    expect(mockOnRemove).toHaveBeenCalledWith(1);
  });

  it('should display file count in header', () => {
    const files = [
      new File(['content1'], 'test1.pdf', { type: 'application/pdf' }),
      new File(['content2'], 'test2.jpg', { type: 'image/jpeg' }),
      new File(['content3'], 'test3.png', { type: 'image/png' }),
    ];

    render(<FilePreview files={files} onRemove={mockOnRemove} />);

    expect(screen.getByText('Selected Files (3)')).toBeInTheDocument();
  });

  it('should format file sizes correctly', () => {
    const files = [
      new File(['x'.repeat(500)], 'small.pdf', { type: 'application/pdf' }),
      new File(['x'.repeat(1024)], 'medium.pdf', { type: 'application/pdf' }),
      new File(['x'.repeat(1024 * 1024)], 'large.pdf', { type: 'application/pdf' }),
    ];

    render(<FilePreview files={files} onRemove={mockOnRemove} />);

    // Check that file sizes are displayed
    expect(screen.getByText('500 Bytes')).toBeInTheDocument();
    expect(screen.getByText('1 KB')).toBeInTheDocument();
    expect(screen.getByText('1 MB')).toBeInTheDocument();
  });

  it('should display file extensions as chips', () => {
    const files = [
      new File(['content'], 'test.pdf', { type: 'application/pdf' }),
      new File(['content'], 'test.jpg', { type: 'image/jpeg' }),
    ];

    render(<FilePreview files={files} onRemove={mockOnRemove} />);

    expect(screen.getByText('PDF')).toBeInTheDocument();
    expect(screen.getByText('JPG')).toBeInTheDocument();
  });

  it('should render in grid layout for multiple files', () => {
    const files = [
      new File(['content1'], 'test1.pdf', { type: 'application/pdf' }),
      new File(['content2'], 'test2.jpg', { type: 'image/jpeg' }),
      new File(['content3'], 'test3.png', { type: 'image/png' }),
      new File(['content4'], 'test4.dcm', { type: 'application/dicom' }),
    ];

    const { container } = render(<FilePreview files={files} onRemove={mockOnRemove} />);

    // Check that all files are rendered
    expect(screen.getByText('test1.pdf')).toBeInTheDocument();
    expect(screen.getByText('test2.jpg')).toBeInTheDocument();
    expect(screen.getByText('test3.png')).toBeInTheDocument();
    expect(screen.getByText('test4.dcm')).toBeInTheDocument();
  });
});
