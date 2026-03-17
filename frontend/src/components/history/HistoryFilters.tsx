// ============================================================================
// History Filters Component
// ============================================================================

import React, { useState } from 'react';
import {
  Box,
  TextField,
  MenuItem,
  Button,
  Paper,
  Stack,
  useTheme,
  alpha,
} from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';
import ClearIcon from '@mui/icons-material/Clear';

interface HistoryFiltersProps {
  onFilterChange: (filters: FilterValues) => void;
  availableConditions?: string[];
}

export interface FilterValues {
  condition: string;
  startDate: string;
  endDate: string;
}

export const HistoryFilters: React.FC<HistoryFiltersProps> = ({
  onFilterChange,
  availableConditions = [],
}) => {
  const theme = useTheme();
  const [condition, setCondition] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  const handleApplyFilters = () => {
    onFilterChange({
      condition,
      startDate,
      endDate,
    });
  };

  const handleClearFilters = () => {
    setCondition('');
    setStartDate('');
    setEndDate('');
    onFilterChange({
      condition: '',
      startDate: '',
      endDate: '',
    });
  };

  const hasActiveFilters = condition || startDate || endDate;

  return (
    <Paper 
      sx={{ 
        p: 3, 
        mb: 3,
        borderRadius: 4,
        background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.4)} 0%, ${alpha(theme.palette.background.paper, 0.1)} 100%)`,
        backdropFilter: 'blur(10px)',
        border: '1px solid',
        borderColor: alpha(theme.palette.divider, 0.2),
        boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.05)}`,
      }}
    >
      <Stack spacing={2}>
        <Box display="flex" alignItems="center" gap={1} mb={1}>
          <FilterListIcon color="action" />
          <Box component="span" fontWeight="bold">
            Filter Assessments
          </Box>
        </Box>

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          {/* Condition Filter */}
          <TextField
            select
            label="Condition"
            value={condition}
            onChange={(e) => setCondition(e.target.value)}
            size="small"
            sx={{ minWidth: 200 }}
          >
            <MenuItem value="">All Conditions</MenuItem>
            {availableConditions.map((cond) => (
              <MenuItem key={cond} value={cond}>
                {cond}
              </MenuItem>
            ))}
          </TextField>

          {/* Start Date Filter */}
          <TextField
            type="date"
            label="Start Date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            size="small"
            InputLabelProps={{
              shrink: true,
            }}
            sx={{ minWidth: 160 }}
          />

          {/* End Date Filter */}
          <TextField
            type="date"
            label="End Date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            size="small"
            InputLabelProps={{
              shrink: true,
            }}
            sx={{ minWidth: 160 }}
          />
        </Stack>

        {/* Action Buttons */}
        <Stack direction="row" spacing={1.5}>
          <Button
            variant="contained"
            startIcon={<FilterListIcon />}
            onClick={handleApplyFilters}
            size="medium"
            sx={{
              borderRadius: 3,
              textTransform: 'none',
              fontWeight: 600,
              boxShadow: `0 4px 12px ${alpha(theme.palette.primary.main, 0.3)}`,
            }}
          >
            Apply Filters
          </Button>
          
          {hasActiveFilters && (
            <Button
              variant="outlined"
              startIcon={<ClearIcon />}
              onClick={handleClearFilters}
              size="medium"
              sx={{
                borderRadius: 3,
                textTransform: 'none',
                fontWeight: 600,
                color: theme.palette.text.primary,
                borderColor: alpha(theme.palette.text.primary, 0.3),
                backdropFilter: 'blur(10px)',
              }}
            >
              Clear
            </Button>
          )}
        </Stack>
      </Stack>
    </Paper>
  );
};
