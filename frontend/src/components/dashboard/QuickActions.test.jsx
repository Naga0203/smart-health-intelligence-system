import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import QuickActions from './QuickActions';

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('QuickActions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render quick actions card with title', () => {
    render(
      <BrowserRouter>
        <QuickActions />
      </BrowserRouter>
    );

    expect(screen.getByText('Quick Actions')).toBeInTheDocument();
  });

  it('should render both action buttons', () => {
    render(
      <BrowserRouter>
        <QuickActions />
      </BrowserRouter>
    );

    expect(screen.getByText('New Symptom Analysis')).toBeInTheDocument();
    expect(screen.getByText('Upload Medical Report')).toBeInTheDocument();
  });

  it('should navigate to new assessment page when New Symptom Analysis button is clicked', () => {
    render(
      <BrowserRouter>
        <QuickActions />
      </BrowserRouter>
    );

    const newAssessmentButton = screen.getByText('New Symptom Analysis');
    fireEvent.click(newAssessmentButton);

    expect(mockNavigate).toHaveBeenCalledWith('/app/assessment/new');
  });

  it('should navigate to upload page when Upload Medical Report button is clicked', () => {
    render(
      <BrowserRouter>
        <QuickActions />
      </BrowserRouter>
    );

    const uploadButton = screen.getByText('Upload Medical Report');
    fireEvent.click(uploadButton);

    expect(mockNavigate).toHaveBeenCalledWith('/app/upload');
  });

  it('should have correct button variants', () => {
    const { container } = render(
      <BrowserRouter>
        <QuickActions />
      </BrowserRouter>
    );

    const buttons = container.querySelectorAll('button');
    
    // First button (New Symptom Analysis) should be contained variant
    expect(buttons[0]).toHaveClass('MuiButton-contained');
    
    // Second button (Upload Medical Report) should be outlined variant
    expect(buttons[1]).toHaveClass('MuiButton-outlined');
  });

  it('should display icons on buttons', () => {
    const { container } = render(
      <BrowserRouter>
        <QuickActions />
      </BrowserRouter>
    );

    // Check for Assessment icon
    const assessmentIcon = container.querySelector('[data-testid="AssessmentIcon"]');
    expect(assessmentIcon).toBeInTheDocument();

    // Check for Upload icon
    const uploadIcon = container.querySelector('[data-testid="UploadIcon"]');
    expect(uploadIcon).toBeInTheDocument();
  });

  it('should allow multiple clicks on buttons', () => {
    render(
      <BrowserRouter>
        <QuickActions />
      </BrowserRouter>
    );

    const newAssessmentButton = screen.getByText('New Symptom Analysis');
    
    // Click multiple times
    fireEvent.click(newAssessmentButton);
    fireEvent.click(newAssessmentButton);
    fireEvent.click(newAssessmentButton);

    expect(mockNavigate).toHaveBeenCalledTimes(3);
    expect(mockNavigate).toHaveBeenCalledWith('/app/assessment/new');
  });

  it('should navigate to different pages when different buttons are clicked', () => {
    render(
      <BrowserRouter>
        <QuickActions />
      </BrowserRouter>
    );

    const newAssessmentButton = screen.getByText('New Symptom Analysis');
    const uploadButton = screen.getByText('Upload Medical Report');

    // Click first button
    fireEvent.click(newAssessmentButton);
    expect(mockNavigate).toHaveBeenCalledWith('/app/assessment/new');

    // Click second button
    fireEvent.click(uploadButton);
    expect(mockNavigate).toHaveBeenCalledWith('/app/upload');

    expect(mockNavigate).toHaveBeenCalledTimes(2);
  });
});
