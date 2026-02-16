import React from 'react';
import { Box, Typography, LinearProgress, Chip } from '@mui/material';

export interface RiskDriverItemProps {
    factor: string;
    value: string;
    contribution: number; // 0 to 100
    description: string;
    isPrimary?: boolean;
}

export const RiskDriverItem: React.FC<RiskDriverItemProps> = ({
    factor,
    value,
    contribution,
    description,
    isPrimary = false,
}) => {
    // Determine color based on contribution
    const getColor = (value: number) => {
        if (value >= 70) return '#DC2626'; // Red for high contribution
        if (value >= 40) return '#EA580C'; // Orange for medium
        return '#3B82F6'; // Blue for lower
    };

    const barColor = getColor(contribution);

    return (
        <Box sx={{ mb: 4 }}>
            {/* Header Row */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle1" fontWeight={600} color="text.primary">
                        {factor}
                    </Typography>
                    {isPrimary && (
                        <Chip
                            label="Primary Driver"
                            size="small"
                            sx={{
                                bgcolor: '#FEE2E2',
                                color: '#DC2626',
                                fontWeight: 600,
                                fontSize: '0.65rem',
                                height: '20px',
                                borderRadius: '4px',
                            }}
                        />
                    )}
                </Box>
                <Typography variant="body2" fontWeight={600} color="text.primary">
                    Value: <Box component="span" sx={{ color: '#111827' }}>{value}</Box>
                </Typography>
            </Box>

            {/* Progress Bar */}
            <LinearProgress
                variant="determinate"
                value={contribution}
                sx={{
                    height: 8,
                    borderRadius: 4,
                    bgcolor: '#F3F4F6',
                    mb: 1,
                    '& .MuiLinearProgress-bar': {
                        bgcolor: barColor,
                        borderRadius: 4,
                    },
                }}
            />

            {/* Description */}
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.875rem' }}>
                {description}
            </Typography>
        </Box>
    );
};
