import React from 'react';
import { Chip } from '@mui/material';

export type RiskLevel = 'high' | 'elevated' | 'medium' | 'low';

interface RiskLevelBadgeProps {
    level: RiskLevel;
    size?: 'small' | 'medium';
}

export const RiskLevelBadge: React.FC<RiskLevelBadgeProps> = ({ level, size = 'medium' }) => {

    const getColors = (level: RiskLevel) => {
        switch (level) {
            case 'high':
                return {
                    bg: '#FEE2E2', // red-100
                    text: '#DC2626', // red-600
                };
            case 'elevated':
                return {
                    bg: '#FFEDD5', // orange-100
                    text: '#EA580C', // orange-600
                };
            case 'medium':
                return {
                    bg: '#FEF3C7', // yellow-100
                    text: '#D97706', // yellow-600
                };
            case 'low':
                return {
                    bg: '#DCFCE7', // green-100
                    text: '#16A34A', // green-600
                };
            default:
                return {
                    bg: '#F3F4F6', // gray-100
                    text: '#4B5563', // gray-600
                };
        }
    };

    const colors = getColors(level);

    const getLabel = (level: RiskLevel) => {
        switch (level) {
            case 'high': return 'High Risk';
            case 'elevated': return 'Elevated Risk';
            case 'medium': return 'Medium Risk';
            case 'low': return 'Low Risk';
            default: return 'Unknown';
        }
    };

    return (
        <Chip
            label={getLabel(level)}
            size={size}
            sx={{
                bgcolor: colors.bg,
                color: colors.text,
                fontWeight: 600,
                borderRadius: '6px',
                fontSize: size === 'small' ? '0.75rem' : '0.875rem',
                height: size === 'small' ? '24px' : '32px',
                '& .MuiChip-label': {
                    px: 1.5,
                },
            }}
        />
    );
};
