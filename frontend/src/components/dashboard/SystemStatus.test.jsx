import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import SystemStatus from './SystemStatus';

describe('SystemStatus', () => {
  it('should render loading skeleton when loading', () => {
    render(<SystemStatus status={null} loading={true} />);

    expect(screen.getByText('System Status')).toBeInTheDocument();
  });

  it('should render warning alert when status is null', () => {
    render(<SystemStatus status={null} loading={false} />);

    expect(screen.getByText('System Status')).toBeInTheDocument();
    expect(screen.getByText('Unable to fetch system status')).toBeInTheDocument();
  });

  it('should display green indicator for operational status', () => {
    const operationalStatus = {
      status: 'operational',
      version: '1.0.0',
      components: {
        orchestrator: { status: 'operational' },
        predictor: { status: 'operational', models_loaded: 5 },
        database: { status: 'operational' },
        gemini_ai: { status: 'operational' },
      },
    };

    render(<SystemStatus status={operationalStatus} loading={false} />);

    expect(screen.getByText('System Operational')).toBeInTheDocument();
    expect(screen.getByText('Version: 1.0.0')).toBeInTheDocument();
  });

  it('should display yellow indicator for degraded status', () => {
    const degradedStatus = {
      status: 'degraded',
      version: '1.0.0',
      components: {
        orchestrator: { status: 'operational' },
        predictor: { status: 'error', models_loaded: 0 },
        database: { status: 'operational' },
        gemini_ai: { status: 'operational' },
      },
    };

    render(<SystemStatus status={degradedStatus} loading={false} />);

    expect(screen.getByText('Service Degraded')).toBeInTheDocument();
    expect(screen.getByText('Some services are experiencing issues. Functionality may be limited.')).toBeInTheDocument();
  });

  it('should display red indicator for error status', () => {
    const errorStatus = {
      status: 'error',
      version: '1.0.0',
      components: {
        orchestrator: { status: 'error' },
        predictor: { status: 'error', models_loaded: 0 },
        database: { status: 'error' },
        gemini_ai: { status: 'error' },
      },
    };

    render(<SystemStatus status={errorStatus} loading={false} />);

    expect(screen.getByText('Service Unavailable')).toBeInTheDocument();
    expect(screen.getByText('System is currently unavailable. Please try again later.')).toBeInTheDocument();
  });

  it('should display component status with correct colors', () => {
    const mixedStatus = {
      status: 'degraded',
      version: '1.0.0',
      components: {
        orchestrator: { status: 'operational' },
        predictor: { status: 'error', models_loaded: 0 },
        database: { status: 'operational' },
        gemini_ai: { status: 'operational' },
      },
    };

    render(<SystemStatus status={mixedStatus} loading={false} />);

    // Check that components are displayed
    expect(screen.getByText('Orchestrator')).toBeInTheDocument();
    expect(screen.getByText(/Predictor/)).toBeInTheDocument();
    expect(screen.getByText('Database')).toBeInTheDocument();
    expect(screen.getByText('Gemini AI')).toBeInTheDocument();

    // Check that models loaded is displayed
    expect(screen.getByText(/0 models/)).toBeInTheDocument();
  });

  it('should display correct status indicator colors for operational', () => {
    const operationalStatus = {
      status: 'operational',
      version: '1.0.0',
      components: {},
    };

    const { container } = render(<SystemStatus status={operationalStatus} loading={false} />);

    // Check for success color icon (CheckCircle)
    const successIcon = container.querySelector('[data-testid="CheckCircleIcon"]');
    expect(successIcon).toBeInTheDocument();
  });

  it('should display correct status indicator colors for degraded', () => {
    const degradedStatus = {
      status: 'degraded',
      version: '1.0.0',
      components: {},
    };

    const { container } = render(<SystemStatus status={degradedStatus} loading={false} />);

    // Check for warning color icon (Warning)
    const warningIcon = container.querySelector('[data-testid="WarningIcon"]');
    expect(warningIcon).toBeInTheDocument();
  });

  it('should display correct status indicator colors for error', () => {
    const errorStatus = {
      status: 'error',
      version: '1.0.0',
      components: {},
    };

    const { container } = render(<SystemStatus status={errorStatus} loading={false} />);

    // Check for error color icon (Error)
    const errorIcon = container.querySelector('[data-testid="ErrorIcon"]');
    expect(errorIcon).toBeInTheDocument();
  });

  it('should handle unknown status gracefully', () => {
    const unknownStatus = {
      status: 'unknown',
      version: '1.0.0',
      components: {},
    };

    render(<SystemStatus status={unknownStatus} loading={false} />);

    expect(screen.getByText('Status Unknown')).toBeInTheDocument();
  });

  it('should display version information', () => {
    const status = {
      status: 'operational',
      version: '2.5.3',
      components: {},
    };

    render(<SystemStatus status={status} loading={false} />);

    expect(screen.getByText('Version: 2.5.3')).toBeInTheDocument();
  });
});
