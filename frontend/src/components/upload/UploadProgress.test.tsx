// ============================================================================
// UploadProgress Unit Tests
// Feature: ai-health-frontend
// ============================================================================

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { UploadProgress, FileUploadStatus } from './UploadProgress';

describe('UploadProgress Component', () => {
  it('should render nothing when no files are provided', () => {
    const { container } = render(<UploadProgress files={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it('should display upload progress for files', () => {
    const files: FileUploadStatus[] = [
      { fileName: 'test1.pdf', progress: 50, status: 'uploading' },
      { fileName: 'test2.jpg', progress: 100, status: 'completed' },
    ];

    render(<UploadProgress files={files} />);

    expect(screen.getByText('Upload Progress')).toBeInTheDocument();
    expect(screen.getByText('test1.pdf')).toBeInTheDocument();
    expect(screen.getByText('test2.jpg')).toBeInTheDocument();
  });

  it('should display overall progress when provided', () => {
    const files: FileUploadStatus[] = [
      { fileName: 'test1.pdf', progress: 50, status: 'uploading' },
      { fileName: 'test2.jpg', progress: 100, status: 'completed' },
    ];

    render(<UploadProgress files={files} overallProgress={75} />);

    expect(screen.getByText('Overall Progress')).toBeInTheDocument();
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('should display file status correctly', () => {
    const files: FileUploadStatus[] = [
      { fileName: 'pending.pdf', progress: 0, status: 'pending' },
      { fileName: 'uploading.jpg', progress: 50, status: 'uploading' },
      { fileName: 'completed.png', progress: 100, status: 'completed' },
      { fileName: 'error.dcm', progress: 0, status: 'error', error: 'Upload failed' },
    ];

    render(<UploadProgress files={files} />);

    expect(screen.getByText('Pending')).toBeInTheDocument();
    expect(screen.getByText('Uploading... 50%')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
    // The error message is displayed instead of "Failed" status text
    expect(screen.getByText('Upload failed')).toBeInTheDocument();
  });

  it('should display error messages for failed uploads', () => {
    const files: FileUploadStatus[] = [
      { fileName: 'error.pdf', progress: 0, status: 'error', error: 'Network error occurred' },
    ];

    render(<UploadProgress files={files} />);

    expect(screen.getByText('Network error occurred')).toBeInTheDocument();
  });

  it('should display file count summary', () => {
    const files: FileUploadStatus[] = [
      { fileName: 'test1.pdf', progress: 100, status: 'completed' },
      { fileName: 'test2.jpg', progress: 100, status: 'completed' },
      { fileName: 'test3.png', progress: 50, status: 'uploading' },
      { fileName: 'test4.dcm', progress: 0, status: 'error', error: 'Failed' },
    ];

    render(<UploadProgress files={files} />);

    expect(screen.getByText('Total: 4')).toBeInTheDocument();
    expect(screen.getByText('Completed: 2')).toBeInTheDocument();
    expect(screen.getByText('Failed: 1')).toBeInTheDocument();
  });

  it('should show progress bars for uploading files', () => {
    const files: FileUploadStatus[] = [
      { fileName: 'uploading.pdf', progress: 50, status: 'uploading' },
    ];

    const { container } = render(<UploadProgress files={files} />);

    // Check for progress bar element
    const progressBars = container.querySelectorAll('[role="progressbar"]');
    expect(progressBars.length).toBeGreaterThan(0);
  });

  it('should show indeterminate progress for pending files', () => {
    const files: FileUploadStatus[] = [
      { fileName: 'pending.pdf', progress: 0, status: 'pending' },
    ];

    const { container } = render(<UploadProgress files={files} />);

    // Check for progress bar element
    const progressBars = container.querySelectorAll('[role="progressbar"]');
    expect(progressBars.length).toBeGreaterThan(0);
  });

  it('should not show overall progress when no active uploads', () => {
    const files: FileUploadStatus[] = [
      { fileName: 'completed.pdf', progress: 100, status: 'completed' },
      { fileName: 'error.jpg', progress: 0, status: 'error', error: 'Failed' },
    ];

    render(<UploadProgress files={files} overallProgress={100} />);

    // Overall progress should not be shown when all uploads are done
    expect(screen.queryByText('Overall Progress')).not.toBeInTheDocument();
  });

  it('should display appropriate icons for different statuses', () => {
    const files: FileUploadStatus[] = [
      { fileName: 'completed.pdf', progress: 100, status: 'completed' },
      { fileName: 'error.jpg', progress: 0, status: 'error', error: 'Failed' },
      { fileName: 'uploading.png', progress: 50, status: 'uploading' },
    ];

    const { container } = render(<UploadProgress files={files} />);

    // Check that icons are rendered (MUI icons render as SVG)
    const icons = container.querySelectorAll('svg');
    expect(icons.length).toBeGreaterThan(0);
  });

  it('should handle multiple files with mixed statuses', () => {
    const files: FileUploadStatus[] = [
      { fileName: 'file1.pdf', progress: 100, status: 'completed' },
      { fileName: 'file2.jpg', progress: 75, status: 'uploading' },
      { fileName: 'file3.png', progress: 0, status: 'pending' },
      { fileName: 'file4.dcm', progress: 0, status: 'error', error: 'Upload failed' },
      { fileName: 'file5.pdf', progress: 100, status: 'completed' },
    ];

    render(<UploadProgress files={files} />);

    expect(screen.getByText('Total: 5')).toBeInTheDocument();
    expect(screen.getByText('Completed: 2')).toBeInTheDocument();
    expect(screen.getByText('Failed: 1')).toBeInTheDocument();
  });
});
