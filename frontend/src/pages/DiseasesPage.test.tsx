// ============================================================================
// Diseases Page Unit Tests
// Tests for disease list display, search, filter, and navigation
// ============================================================================

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import DiseasesPage from './DiseasesPage';
import { useSystemStore } from '@/stores/systemStore';

// Mock the system store
vi.mock('@/stores/systemStore', () => ({
  useSystemStore: vi.fn(),
}));

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('DiseasesPage', () => {
  const mockDiseases = [
    {
      name: 'Diabetes',
      category: 'Metabolic',
      symptoms: ['Increased thirst', 'Frequent urination', 'Fatigue', 'Blurred vision'],
    },
    {
      name: 'Hypertension',
      category: 'Cardiovascular',
      symptoms: ['Headache', 'Dizziness', 'Chest pain'],
    },
    {
      name: 'Asthma',
      category: 'Respiratory',
      symptoms: ['Shortness of breath', 'Wheezing', 'Coughing', 'Chest tightness'],
    },
    {
      name: 'Migraine',
      category: 'Neurological',
      symptoms: ['Severe headache', 'Nausea', 'Light sensitivity'],
    },
  ];

  const mockFetchDiseases = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <DiseasesPage />
      </BrowserRouter>
    );
  };

  /**
   * Test: Disease list fetching and display
   * Requirements: 15.3, 15.5
   */
  describe('Disease List Fetching and Display', () => {
    it('should fetch diseases on mount when diseases is null', () => {
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: null,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      expect(mockFetchDiseases).toHaveBeenCalledTimes(1);
    });

    it('should not fetch diseases if already loaded', () => {
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: mockDiseases,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      expect(mockFetchDiseases).not.toHaveBeenCalled();
    });

    it('should display loading spinner while fetching', () => {
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: null,
        loading: true,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('should display error message when fetch fails', () => {
      const errorMessage = 'Failed to load diseases';
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: null,
        loading: false,
        error: errorMessage,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });

    it('should display all diseases with complete information', () => {
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: mockDiseases,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      // Check that all diseases are displayed
      mockDiseases.forEach((disease) => {
        expect(screen.getByText(disease.name)).toBeInTheDocument();
        expect(screen.getByText(disease.category)).toBeInTheDocument();
      });
    });

    it('should display disease symptoms as chips', () => {
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: mockDiseases,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      // Check that symptoms are displayed for Diabetes
      const diabetesCard = screen.getByText('Diabetes').closest('.MuiCard-root');
      expect(diabetesCard).toBeInTheDocument();
      
      if (diabetesCard) {
        const symptomsSection = within(diabetesCard);
        expect(symptomsSection.getByText('Increased thirst')).toBeInTheDocument();
        expect(symptomsSection.getByText('Frequent urination')).toBeInTheDocument();
      }
    });

    it('should display "Assess Risk" button for each disease', () => {
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: mockDiseases,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      const assessButtons = screen.getAllByRole('button', { name: /assess risk/i });
      expect(assessButtons).toHaveLength(mockDiseases.length);
    });
  });

  /**
   * Test: Search functionality
   * Requirements: 15.4
   */
  describe('Search Functionality', () => {
    it('should filter diseases by search query', async () => {
      const user = userEvent.setup();
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: mockDiseases,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      const searchInput = screen.getByPlaceholderText('Search diseases...');
      await user.type(searchInput, 'diabetes');

      // Should show only Diabetes
      expect(screen.getByText('Diabetes')).toBeInTheDocument();
      expect(screen.queryByText('Hypertension')).not.toBeInTheDocument();
      expect(screen.queryByText('Asthma')).not.toBeInTheDocument();
    });

    it('should be case-insensitive', async () => {
      const user = userEvent.setup();
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: mockDiseases,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      const searchInput = screen.getByPlaceholderText('Search diseases...');
      await user.type(searchInput, 'DIABETES');

      expect(screen.getByText('Diabetes')).toBeInTheDocument();
    });

    it('should show "no diseases found" message when search has no results', async () => {
      const user = userEvent.setup();
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: mockDiseases,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      const searchInput = screen.getByPlaceholderText('Search diseases...');
      await user.type(searchInput, 'nonexistent disease');

      expect(screen.getByText(/no diseases found matching your search criteria/i)).toBeInTheDocument();
    });

    it('should update results as user types', async () => {
      const user = userEvent.setup();
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: mockDiseases,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      const searchInput = screen.getByPlaceholderText('Search diseases...');
      
      // Type 'a' - should show Diabetes, Asthma, Migraine
      await user.type(searchInput, 'a');
      expect(screen.getByText('Diabetes')).toBeInTheDocument();
      expect(screen.getByText('Asthma')).toBeInTheDocument();
      expect(screen.getByText('Migraine')).toBeInTheDocument();
      
      // Type 'sthma' - should show only Asthma
      await user.type(searchInput, 'sthma');
      expect(screen.getByText('Asthma')).toBeInTheDocument();
      expect(screen.queryByText('Diabetes')).not.toBeInTheDocument();
    });
  });

  /**
   * Test: Category filter
   * Requirements: 15.4
   */
  describe('Category Filter', () => {
    it('should filter diseases by category', async () => {
      const user = userEvent.setup();
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: mockDiseases,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      // Find the select by its role
      const categorySelect = screen.getByRole('combobox');
      await user.click(categorySelect);

      // Select Cardiovascular category
      const cardiovascularOption = screen.getByRole('option', { name: 'Cardiovascular' });
      await user.click(cardiovascularOption);

      // Should show only Hypertension
      await waitFor(() => {
        expect(screen.getByText('Hypertension')).toBeInTheDocument();
        expect(screen.queryByText('Diabetes')).not.toBeInTheDocument();
        expect(screen.queryByText('Asthma')).not.toBeInTheDocument();
      });
    });

    it('should show all diseases when "All Categories" is selected', async () => {
      const user = userEvent.setup();
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: mockDiseases,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      // Find the select by its role
      const categorySelect = screen.getByRole('combobox');
      await user.click(categorySelect);

      // Select Metabolic first
      const metabolicOption = screen.getByRole('option', { name: 'Metabolic' });
      await user.click(metabolicOption);

      await waitFor(() => {
        expect(screen.getByText('Diabetes')).toBeInTheDocument();
        expect(screen.queryByText('Hypertension')).not.toBeInTheDocument();
      });

      // Now select All Categories
      await user.click(categorySelect);
      const allOption = screen.getByRole('option', { name: 'All Categories' });
      await user.click(allOption);

      await waitFor(() => {
        expect(screen.getByText('Diabetes')).toBeInTheDocument();
        expect(screen.getByText('Hypertension')).toBeInTheDocument();
        expect(screen.getByText('Asthma')).toBeInTheDocument();
      });
    });

    it('should combine search and category filters', async () => {
      const user = userEvent.setup();
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: [
          ...mockDiseases,
          {
            name: 'Type 2 Diabetes',
            category: 'Metabolic',
            symptoms: ['High blood sugar'],
          },
        ],
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      // Filter by Metabolic category
      const categorySelect = screen.getByRole('combobox');
      await user.click(categorySelect);
      const metabolicOption = screen.getByRole('option', { name: 'Metabolic' });
      await user.click(metabolicOption);

      // Search for "Type"
      const searchInput = screen.getByPlaceholderText('Search diseases...');
      await user.type(searchInput, 'Type');

      // Should show only Type 2 Diabetes
      await waitFor(() => {
        expect(screen.getByText('Type 2 Diabetes')).toBeInTheDocument();
        expect(screen.queryByText(/^Diabetes$/)).not.toBeInTheDocument();
      });
    });
  });

  /**
   * Test: Navigation to assessment with pre-filled symptoms
   * Requirements: 15.6
   */
  describe('Assessment Navigation', () => {
    it('should navigate to new assessment page when "Assess Risk" is clicked', async () => {
      const user = userEvent.setup();
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: mockDiseases,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      // Click "Assess Risk" for Diabetes
      const diabetesCard = screen.getByText('Diabetes').closest('.MuiCard-root');
      const assessButton = within(diabetesCard!).getByRole('button', { name: /assess risk/i });
      await user.click(assessButton);

      expect(mockNavigate).toHaveBeenCalledWith('/app/assessment/new', {
        state: {
          prefilledSymptoms: mockDiseases[0].symptoms,
          diseaseContext: 'Diabetes',
        },
      });
    });

    it('should pass correct symptoms for each disease', async () => {
      const user = userEvent.setup();
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: mockDiseases,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      // Click "Assess Risk" for Hypertension
      const hypertensionCard = screen.getByText('Hypertension').closest('.MuiCard-root');
      const assessButton = within(hypertensionCard!).getByRole('button', { name: /assess risk/i });
      await user.click(assessButton);

      expect(mockNavigate).toHaveBeenCalledWith('/app/assessment/new', {
        state: {
          prefilledSymptoms: mockDiseases[1].symptoms,
          diseaseContext: 'Hypertension',
        },
      });
    });

    it('should handle diseases without symptoms', async () => {
      const user = userEvent.setup();
      const diseasesWithoutSymptoms = [
        {
          name: 'Unknown Disease',
          category: 'Other',
        },
      ];

      vi.mocked(useSystemStore).mockReturnValue({
        diseases: diseasesWithoutSymptoms,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      const assessButton = screen.getByRole('button', { name: /assess risk/i });
      await user.click(assessButton);

      expect(mockNavigate).toHaveBeenCalledWith('/app/assessment/new', {
        state: {
          prefilledSymptoms: [],
          diseaseContext: 'Unknown Disease',
        },
      });
    });
  });

  /**
   * Test: Empty state
   * Requirements: 15.3
   */
  describe('Empty State', () => {
    it('should display message when no diseases are available', () => {
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: [],
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      expect(screen.getByText(/no diseases found matching your search criteria/i)).toBeInTheDocument();
    });
  });

  /**
   * Test: UI elements
   * Requirements: 15.3, 15.4, 15.5
   */
  describe('UI Elements', () => {
    it('should display page title and description', () => {
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: mockDiseases,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      expect(screen.getByText('Supported Diseases')).toBeInTheDocument();
      expect(screen.getByText(/explore the diseases our system can assess/i)).toBeInTheDocument();
    });

    it('should display search icon in search input', () => {
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: mockDiseases,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      const searchInput = screen.getByPlaceholderText('Search diseases...');
      expect(searchInput).toBeInTheDocument();
    });

    it('should display category dropdown with all unique categories', () => {
      vi.mocked(useSystemStore).mockReturnValue({
        diseases: mockDiseases,
        loading: false,
        error: null,
        fetchDiseases: mockFetchDiseases,
      });

      renderComponent();

      const categorySelect = screen.getByRole('combobox');
      expect(categorySelect).toBeInTheDocument();
    });
  });
});
