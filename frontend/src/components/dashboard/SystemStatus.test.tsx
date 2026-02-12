// ============================================================================
// System Status Component Unit Tests
// Tests for status indicator colors and display
// ============================================================================

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import SystemStatus from './SystemStatus';

describe('SystemStatus Component', () => {
  /**
   * Test: Status indicator colors
   * Requirements: 10.2, 10.3
   */
  describe('Status Indicator Colors', () => {
    it('should display green indicator for operational status', () => {
      const mockStatus = {
        status: 'operational',
        version: '1.0.0',
        timestamp: '2024-01-15T10:00:00Z',
      };

      render(<SystemStatus status={mockStatus} modelInfo={null} loading={false} />);

      // Should display operational label
      expect(screen.getByText('System Operational')).toBeInTheDocument();

      // Should display version
      expect(screen.getByText(/Version: 1.0.0/i)).toBeInTheDocument();
    });

    it('should display yellow/orange indicator for degraded status', () => {
      const mockStatus = {
        status: 'degraded',
        version: '1.0.0',
        timestamp: '2024-01-15T10:00:00Z',
      };

      render(<SystemStatus status={mockStatus} modelInfo={null} loading={false} />);

      // Should display degraded label
      expect(screen.getByText('Service Degraded')).toBeInTheDocument();

      // Should display warning alert
      expect(screen.getByText(/Some services are experiencing issues/i)).toBeInTheDocument();
    });

    it('should display red indicator for error status', () => {
      const mockStatus = {
        status: 'error',
        version: '1.0.0',
        timestamp: '2024-01-15T10:00:00Z',
      };

      render(<SystemStatus status={mockStatus} modelInfo={null} loading={false} />);

      // Should display unavailable label
      expect(screen.getByText('Service Unavailable')).toBeInTheDocument();

      // Should display error alert
      expect(screen.getByText(/System is currently unavailable/i)).toBeInTheDocument();
    });

    it('should display default indicator for unknown status', () => {
      const mockStatus = {
        status: 'unknown',
        version: '1.0.0',
        timestamp: '2024-01-15T10:00:00Z',
      };

      render(<SystemStatus status={mockStatus as any} modelInfo={null} loading={false} />);

      // Should display unknown status label
      expect(screen.getByText('Status Unknown')).toBeInTheDocument();
    });
  });

  /**
   * Test: Model information display
   * Requirements: 10.4, 10.5
   */
  describe('Model Information Display', () => {
    it('should display model information when available', () => {
      const mockStatus = {
        status: 'operational',
        version: '1.0.0',
        timestamp: '2024-01-15T10:00:00Z',
      };

      const mockModelInfo = {
        model_type: 'RandomForest',
        num_diseases: 42,
        model_loaded: true,
      };

      render(<SystemStatus status={mockStatus} modelInfo={mockModelInfo} loading={false} />);

      // Should display model information section
      expect(screen.getByText('Model Information')).toBeInTheDocument();

      // Should display model type
      expect(screen.getByText(/Type: RandomForest/i)).toBeInTheDocument();

      // Should display number of diseases
      expect(screen.getByText(/Diseases: 42/i)).toBeInTheDocument();

      // Should display model loaded status
      expect(screen.getByText(/Status: Loaded/i)).toBeInTheDocument();
    });

    it('should display "Not Loaded" when model is not loaded', () => {
      const mockStatus = {
        status: 'operational',
        version: '1.0.0',
        timestamp: '2024-01-15T10:00:00Z',
      };

      const mockModelInfo = {
        model_type: 'RandomForest',
        num_diseases: 42,
        model_loaded: false,
      };

      render(<SystemStatus status={mockStatus} modelInfo={mockModelInfo} loading={false} />);

      // Should display "Not Loaded" status
      expect(screen.getByText(/Status: Not Loaded/i)).toBeInTheDocument();
    });

    it('should display last updated timestamp when available', () => {
      const mockStatus = {
        status: 'operational',
        version: '1.0.0',
        timestamp: '2024-01-15T10:00:00Z',
      };

      const mockModelInfo = {
        model_type: 'RandomForest',
        num_diseases: 42,
        model_loaded: true,
      };

      render(<SystemStatus status={mockStatus} modelInfo={mockModelInfo} loading={false} />);

      // Should display last updated timestamp
      expect(screen.getByText(/Last Updated:/i)).toBeInTheDocument();
    });

    it('should not display model information section when modelInfo is null', () => {
      const mockStatus = {
        status: 'operational',
        version: '1.0.0',
        timestamp: '2024-01-15T10:00:00Z',
      };

      render(<SystemStatus status={mockStatus} modelInfo={null} loading={false} />);

      // Should not display model information section
      expect(screen.queryByText('Model Information')).not.toBeInTheDocument();
    });
  });

  /**
   * Test: Component status display
   * Requirements: 10.4
   */
  describe('Component Status Display', () => {
    it('should display component statuses when available', () => {
      const mockStatus = {
        status: 'operational',
        version: '1.0.0',
        timestamp: '2024-01-15T10:00:00Z',
        components: {
          orchestrator: { status: 'operational' },
          predictor: { status: 'operational', models_loaded: 3 },
          database: { status: 'operational' },
          gemini_ai: { status: 'operational' },
        },
      };

      render(<SystemStatus status={mockStatus} modelInfo={null} loading={false} />);

      // Should display components section
      expect(screen.getByText('Components')).toBeInTheDocument();

      // Should display orchestrator status
      expect(screen.getByText('Orchestrator')).toBeInTheDocument();

      // Should display predictor with models loaded
      expect(screen.getByText(/Predictor \(3 models\)/i)).toBeInTheDocument();

      // Should display database status
      expect(screen.getByText('Database')).toBeInTheDocument();

      // Should display Gemini AI status
      expect(screen.getByText('Gemini AI')).toBeInTheDocument();
    });

    it('should display error status for failed components', () => {
      const mockStatus = {
        status: 'degraded',
        version: '1.0.0',
        timestamp: '2024-01-15T10:00:00Z',
        components: {
          orchestrator: { status: 'operational' },
          predictor: { status: 'error', models_loaded: 0 },
        },
      };

      render(<SystemStatus status={mockStatus} modelInfo={null} loading={false} />);

      // Should display components section
      expect(screen.getByText('Components')).toBeInTheDocument();

      // Should display predictor with error status
      expect(screen.getByText(/Predictor \(0 models\)/i)).toBeInTheDocument();
    });
  });

  /**
   * Test: Loading state
   * Requirements: 10.1
   */
  describe('Loading State', () => {
    it('should display loading skeleton when loading is true', () => {
      const { container } = render(<SystemStatus status={null} modelInfo={null} loading={true} />);

      // Should display System Status title
      expect(screen.getByText('System Status')).toBeInTheDocument();

      // Should display loading skeleton
      const skeletons = container.querySelectorAll('.MuiSkeleton-root');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  /**
   * Test: Error state
   * Requirements: 10.1
   */
  describe('Error State', () => {
    it('should display warning when status is null and not loading', () => {
      render(<SystemStatus status={null} modelInfo={null} loading={false} />);

      // Should display System Status title
      expect(screen.getByText('System Status')).toBeInTheDocument();

      // Should display warning alert
      expect(screen.getByText('Unable to fetch system status')).toBeInTheDocument();
    });
  });

  /**
   * Test: Degraded service warning
   * Requirements: 10.3
   */
  describe('Service Warnings', () => {
    it('should display warning alert for degraded status', () => {
      const mockStatus = {
        status: 'degraded',
        version: '1.0.0',
        timestamp: '2024-01-15T10:00:00Z',
      };

      render(<SystemStatus status={mockStatus} modelInfo={null} loading={false} />);

      // Should display degraded warning
      expect(screen.getByText(/Some services are experiencing issues/i)).toBeInTheDocument();
    });

    it('should display error alert for unavailable status', () => {
      const mockStatus = {
        status: 'error',
        version: '1.0.0',
        timestamp: '2024-01-15T10:00:00Z',
      };

      render(<SystemStatus status={mockStatus} modelInfo={null} loading={false} />);

      // Should display error alert
      expect(screen.getByText(/System is currently unavailable/i)).toBeInTheDocument();
    });

    it('should not display warning for operational status', () => {
      const mockStatus = {
        status: 'operational',
        version: '1.0.0',
        timestamp: '2024-01-15T10:00:00Z',
      };

      render(<SystemStatus status={mockStatus} modelInfo={null} loading={false} />);

      // Should not display any alerts
      expect(screen.queryByText(/Some services are experiencing issues/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/System is currently unavailable/i)).not.toBeInTheDocument();
    });
  });
});
