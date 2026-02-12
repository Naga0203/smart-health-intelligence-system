// ============================================================================
// TreatmentTabs Unit Tests
// ============================================================================

import { describe, it, expect, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TreatmentTabs } from './TreatmentTabs';
import type { TreatmentInfo } from '@/types';

describe('TreatmentTabs', () => {
  const mockTreatmentInfo: TreatmentInfo = {
    allopathy: [
      {
        category: 'Medication',
        recommendations: ['Take prescribed medication', 'Follow dosage instructions'],
        notes: 'Consult your doctor',
        approach: 'Evidence-based medicine',
        focus: 'Symptom management',
      },
    ],
    ayurveda: [
      {
        category: 'Herbal Remedies',
        recommendations: ['Turmeric supplements', 'Ashwagandha'],
        notes: 'Consult Ayurvedic practitioner',
        approach: 'Holistic healing',
        focus: 'Balance doshas',
      },
    ],
    homeopathy: [
      {
        category: 'Remedies',
        recommendations: ['Arnica montana', 'Belladonna'],
        notes: 'Consult homeopathic practitioner',
        approach: 'Like cures like',
        focus: 'Individualized treatment',
      },
    ],
    lifestyle: [
      {
        category: 'Diet',
        recommendations: ['Eat balanced meals', 'Stay hydrated'],
        notes: 'Maintain consistency',
        approach: 'Preventive care',
        focus: 'Overall wellness',
      },
    ],
  };

  /**
   * Test: Treatment tabs rendering
   * Requirements: 7.1
   */
  it('should render all four treatment tabs', () => {
    render(<TreatmentTabs treatmentInfo={mockTreatmentInfo} confidence="HIGH" />);

    // Should display all four tabs
    expect(screen.getByRole('tab', { name: /modern medicine/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /ayurveda/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /homeopathy/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /lifestyle/i })).toBeInTheDocument();
  });

  /**
   * Test: Tab switching maintains context
   * Requirements: 7.6
   */
  it('should maintain assessment context when switching tabs', async () => {
    render(<TreatmentTabs treatmentInfo={mockTreatmentInfo} confidence="HIGH" />);
    const user = userEvent.setup();

    // Initially, Modern Medicine tab should be active
    const modernMedicinePanel = screen.getByRole('tabpanel', { name: /modern medicine/i });
    expect(modernMedicinePanel).toBeVisible();
    expect(within(modernMedicinePanel).getByText('Medication')).toBeInTheDocument();

    // Click on Ayurveda tab
    const ayurvedaTab = screen.getByRole('tab', { name: /ayurveda/i });
    await user.click(ayurvedaTab);

    // Ayurveda panel should now be visible
    const ayurvedaPanel = screen.getByRole('tabpanel', { name: /ayurveda/i });
    expect(ayurvedaPanel).toBeVisible();
    expect(within(ayurvedaPanel).getByText('Herbal Remedies')).toBeInTheDocument();

    // Click on Homeopathy tab
    const homeopathyTab = screen.getByRole('tab', { name: /homeopathy/i });
    await user.click(homeopathyTab);

    // Homeopathy panel should now be visible
    const homeopathyPanel = screen.getByRole('tabpanel', { name: /homeopathy/i });
    expect(homeopathyPanel).toBeVisible();
    expect(within(homeopathyPanel).getByText('Remedies')).toBeInTheDocument();

    // Click on Lifestyle tab
    const lifestyleTab = screen.getByRole('tab', { name: /lifestyle/i });
    await user.click(lifestyleTab);

    // Lifestyle panel should now be visible
    const lifestylePanel = screen.getByRole('tabpanel', { name: /lifestyle/i });
    expect(lifestylePanel).toBeVisible();
    expect(within(lifestylePanel).getByText('Diet')).toBeInTheDocument();

    // Switch back to Modern Medicine
    const modernMedicineTab = screen.getByRole('tab', { name: /modern medicine/i });
    await user.click(modernMedicineTab);

    // Modern Medicine panel should be visible again with same content
    const modernMedicinePanelAgain = screen.getByRole('tabpanel', { name: /modern medicine/i });
    expect(modernMedicinePanelAgain).toBeVisible();
    expect(within(modernMedicinePanelAgain).getByText('Medication')).toBeInTheDocument();
    expect(within(modernMedicinePanelAgain).getByText('Take prescribed medication')).toBeInTheDocument();
  });

  /**
   * Test: Treatment tabs hidden when confidence is LOW
   * Requirements: 7.5
   */
  it('should not render treatment tabs when confidence level is LOW', () => {
    const { container } = render(<TreatmentTabs treatmentInfo={mockTreatmentInfo} confidence="LOW" />);

    // Should not render any tabs
    expect(screen.queryByRole('tab', { name: /modern medicine/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('tab', { name: /ayurveda/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('tab', { name: /homeopathy/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('tab', { name: /lifestyle/i })).not.toBeInTheDocument();

    // Container should be empty
    expect(container.firstChild).toBeNull();
  });

  /**
   * Test: Treatment tabs visible when confidence is MEDIUM
   * Requirements: 7.5
   */
  it('should render treatment tabs when confidence level is MEDIUM', () => {
    render(<TreatmentTabs treatmentInfo={mockTreatmentInfo} confidence="MEDIUM" />);

    // Should display all four tabs
    expect(screen.getByRole('tab', { name: /modern medicine/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /ayurveda/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /homeopathy/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /lifestyle/i })).toBeInTheDocument();
  });

  /**
   * Test: Treatment tabs visible when confidence is HIGH
   * Requirements: 7.5
   */
  it('should render treatment tabs when confidence level is HIGH', () => {
    render(<TreatmentTabs treatmentInfo={mockTreatmentInfo} confidence="HIGH" />);

    // Should display all four tabs
    expect(screen.getByRole('tab', { name: /modern medicine/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /ayurveda/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /homeopathy/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /lifestyle/i })).toBeInTheDocument();
  });

  /**
   * Test: Disclaimer presence on each tab - Modern Medicine
   * Requirements: 7.4
   */
  it('should display disclaimer on Modern Medicine tab', () => {
    render(<TreatmentTabs treatmentInfo={mockTreatmentInfo} confidence="HIGH" />);

    // Modern Medicine tab should be active by default
    const modernMedicinePanel = screen.getByRole('tabpanel', { name: /modern medicine/i });
    
    // Should display disclaimer
    expect(within(modernMedicinePanel).getByText('Educational Information Only')).toBeInTheDocument();
    expect(within(modernMedicinePanel).getByText(/this information is educational only/i)).toBeInTheDocument();
  });

  /**
   * Test: Disclaimer presence on each tab - Ayurveda
   * Requirements: 7.4
   */
  it('should display disclaimer on Ayurveda tab', async () => {
    render(<TreatmentTabs treatmentInfo={mockTreatmentInfo} confidence="HIGH" />);
    const user = userEvent.setup();

    // Click on Ayurveda tab
    const ayurvedaTab = screen.getByRole('tab', { name: /ayurveda/i });
    await user.click(ayurvedaTab);

    const ayurvedaPanel = screen.getByRole('tabpanel', { name: /ayurveda/i });
    
    // Should display disclaimer
    expect(within(ayurvedaPanel).getByText('Educational Information Only')).toBeInTheDocument();
    expect(within(ayurvedaPanel).getByText(/this information is educational only/i)).toBeInTheDocument();
  });

  /**
   * Test: Disclaimer presence on each tab - Homeopathy
   * Requirements: 7.4
   */
  it('should display disclaimer on Homeopathy tab', async () => {
    render(<TreatmentTabs treatmentInfo={mockTreatmentInfo} confidence="HIGH" />);
    const user = userEvent.setup();

    // Click on Homeopathy tab
    const homeopathyTab = screen.getByRole('tab', { name: /homeopathy/i });
    await user.click(homeopathyTab);

    const homeopathyPanel = screen.getByRole('tabpanel', { name: /homeopathy/i });
    
    // Should display disclaimer
    expect(within(homeopathyPanel).getByText('Educational Information Only')).toBeInTheDocument();
    expect(within(homeopathyPanel).getByText(/this information is educational only/i)).toBeInTheDocument();
  });

  /**
   * Test: Disclaimer presence on each tab - Lifestyle
   * Requirements: 7.4
   */
  it('should display disclaimer on Lifestyle tab', async () => {
    render(<TreatmentTabs treatmentInfo={mockTreatmentInfo} confidence="HIGH" />);
    const user = userEvent.setup();

    // Click on Lifestyle tab
    const lifestyleTab = screen.getByRole('tab', { name: /lifestyle/i });
    await user.click(lifestyleTab);

    const lifestylePanel = screen.getByRole('tabpanel', { name: /lifestyle/i });
    
    // Should display disclaimer
    expect(within(lifestylePanel).getByText('Educational Information Only')).toBeInTheDocument();
    expect(within(lifestylePanel).getByText(/this information is educational only/i)).toBeInTheDocument();
  });

  /**
   * Test: Empty treatment info handling
   * Requirements: 7.1
   */
  it('should handle empty treatment info gracefully', () => {
    const emptyTreatmentInfo: TreatmentInfo = {
      allopathy: [],
      ayurveda: [],
      homeopathy: [],
      lifestyle: [],
    };

    render(<TreatmentTabs treatmentInfo={emptyTreatmentInfo} confidence="HIGH" />);

    // Should still render tabs
    expect(screen.getByRole('tab', { name: /modern medicine/i })).toBeInTheDocument();

    // Should display empty state message
    expect(screen.getByText(/no modern medicine treatment information available/i)).toBeInTheDocument();
  });

  /**
   * Test: Undefined treatment info handling
   * Requirements: 7.1
   */
  it('should handle undefined treatment arrays gracefully', () => {
    const partialTreatmentInfo: TreatmentInfo = {
      allopathy: undefined,
      ayurveda: undefined,
      homeopathy: undefined,
      lifestyle: undefined,
    };

    render(<TreatmentTabs treatmentInfo={partialTreatmentInfo} confidence="HIGH" />);

    // Should still render tabs
    expect(screen.getByRole('tab', { name: /modern medicine/i })).toBeInTheDocument();

    // Should display empty state message
    expect(screen.getByText(/no modern medicine treatment information available/i)).toBeInTheDocument();
  });

  /**
   * Test: Tab accessibility attributes
   * Requirements: 7.1
   */
  it('should have proper accessibility attributes for tabs', () => {
    render(<TreatmentTabs treatmentInfo={mockTreatmentInfo} confidence="HIGH" />);

    // Check tab attributes
    const modernMedicineTab = screen.getByRole('tab', { name: /modern medicine/i });
    expect(modernMedicineTab).toHaveAttribute('id', 'treatment-tab-0');
    expect(modernMedicineTab).toHaveAttribute('aria-controls', 'treatment-tabpanel-0');

    const ayurvedaTab = screen.getByRole('tab', { name: /ayurveda/i });
    expect(ayurvedaTab).toHaveAttribute('id', 'treatment-tab-1');
    expect(ayurvedaTab).toHaveAttribute('aria-controls', 'treatment-tabpanel-1');

    // Check tabpanel attributes
    const modernMedicinePanel = screen.getByRole('tabpanel', { name: /modern medicine/i });
    expect(modernMedicinePanel).toHaveAttribute('id', 'treatment-tabpanel-0');
    expect(modernMedicinePanel).toHaveAttribute('aria-labelledby', 'treatment-tab-0');
  });
});
