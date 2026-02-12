// ============================================================================
// History Filters Component
// ============================================================================

import React, { useState } from 'react';
import {
  Box,
  TextField,
  MenuItem,
  Button,
  Stack,
  Paper,
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
    <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
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
        <Stack direction="row" spacing={1}>
          <Button
            variant="contained"
            startIcon={<FilterListIcon />}
            onClick={handleApplyFilters}
            size="small"
          >
            Apply Filters
          </Button>
          
          {hasActiveFilters && (
            <Button
              variant="outlined"
              startIcon={<ClearIcon />}
              onClick={handleClearFilters}
              size="small"
            >
              Clear
            </Button>
          )}
        </Stack>
      </Stack>
    </Paper>
  );
};
