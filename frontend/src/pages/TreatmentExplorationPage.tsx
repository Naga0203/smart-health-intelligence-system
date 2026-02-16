// ============================================================================
// Treatment Exploration Page - Multi-system treatment overview
// ============================================================================

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Box,
    Container,
    Typography,
    Grid,
    Card,
    CardContent,
    Chip,
    Button,
    Tabs,
    Tab,
    Alert,
    Paper,
    Stack,
    Divider,
} from '@mui/material';
import {
    ArrowBack as ArrowBackIcon,
    InfoOutlined as InfoIcon,
    LocalPharmacy as DrugIcon,
    Shield as ShieldIcon,
    MedicalServices as ProcedureIcon,
    SelfImprovement as BehavioralIcon,
    Spa as LeafIcon,
    WaterDrop as DropIcon,
    AccessibilityNew as BodyIcon,
    MenuBook as BookIcon,
    MonitorHeart as MonitorHeartIcon, // Changed from HeartIcon to MonitorHeartIcon as per instruction
} from '@mui/icons-material';

// --- Types ---

type SeverityLevel = 'Mild' | 'Moderate' | 'Severe' | 'Severe / Chronic' | 'Mild / Adjunct' | 'General';
type TreatmentSystem = 'Modern Medicine' | 'Ayurveda' | 'Homeopathy' | 'Lifestyle';

interface TreatmentCard {
    id: string;
    title: string;
    description: string;
    severity: SeverityLevel;
    icon: React.ReactNode;
    actionLabel?: string;
}

interface TreatmentData {
    description: string;
    systems: {
        [key in TreatmentSystem]: TreatmentCard[];
    };
}

// --- Mock Data ---

const MOCK_DATA: Record<string, TreatmentData> = {
    'Migraine': {
        description: 'A comparative overview of potential treatment pathways. Treatments for migraine typically involve a combination of acute relief, preventive strategies, and lifestyle adjustments.',
        systems: {
            'Modern Medicine': [
                {
                    id: 'acute',
                    title: 'Acute Pharmacotherapy',
                    description: 'First-line treatment often involves NSAIDs (ibuprofen, naproxen) for mild attacks. For moderate to severe migraine, triptans (e.g., sumatriptan) are considered the standard of care to abort attacks.',
                    severity: 'Moderate',
                    icon: <DrugIcon color="primary" />,
                    actionLabel: 'View Clinical Guidelines'
                },
                {
                    id: 'preventive',
                    title: 'Preventive Medication',
                    description: 'Indicated for patients with frequent attacks (> 4/month). Options include beta-blockers (propranolol), anti-epileptics (topiramate), and CGRP monoclonal antibodies for refractory cases.',
                    severity: 'Severe / Chronic',
                    icon: <ShieldIcon color="secondary" />,
                    actionLabel: 'View Efficacy Studies'
                },
                {
                    id: 'procedural',
                    title: 'Procedural Interventions',
                    description: 'Interventions such as OnabotulinumtoxinA (Botox) injections are FDA-approved for chronic migraine. Nerve blocks (e.g., occipital nerve block) provide temporary relief for specific presentations.',
                    severity: 'Severe',
                    icon: <ProcedureIcon color="error" />,
                    actionLabel: 'View Procedure Details'
                },
                {
                    id: 'behavioral',
                    title: 'Behavioral Therapy',
                    description: 'Cognitive Behavioral Therapy (CBT) and Biofeedback are often prescribed alongside medication to help manage pain perception and reduce stress-induced triggers.',
                    severity: 'Mild / Adjunct',
                    icon: <BehavioralIcon color="warning" />,
                    actionLabel: 'View Therapy Protocols'
                }
            ],
            'Ayurveda': [
                {
                    id: 'shodhana',
                    title: 'Shodhana Therapy',
                    description: 'Purification procedures like Nasya (nasal administration of medicated oils) and Virechana (purgation) to balance doshas, specifically Pitta and Vata implicated in migraines.',
                    severity: 'Moderate',
                    icon: <LeafIcon color="success" />,
                    actionLabel: 'View Ayurvedic Protocols'
                },
                {
                    id: 'shamana',
                    title: 'Shamana Aushadhi',
                    description: 'Palliative oral medications using herbs like Pathyadi Kadha, Godanti Bhasma, and Shirashooladivajra Rasa to alleviate pain and reduce recurrence.',
                    severity: 'Mild',
                    icon: <LeafIcon color="success" />,
                    actionLabel: 'View Herbal Formulations'
                }
            ],
            'Homeopathy': [
                {
                    id: 'constitutional',
                    title: 'Constitutional Treatment',
                    description: 'Holistic approach selecting remedies (e.g., Natrum Mur, Belladonna, Sanguinaria) based on individual symptom patterns, triggers, and patient constitution.',
                    severity: 'General',
                    icon: <DropIcon color="info" />,
                    actionLabel: 'View Remedy Profiles'
                }
            ],
            'Lifestyle': [
                {
                    id: 'trigger_mgmt',
                    title: 'Trigger Management',
                    description: 'Identification and avoidance of dietary triggers (aged cheese, caffeine, alcohol), regulating sleep schedules, and managing stress levels.',
                    severity: 'General',
                    icon: <BodyIcon color="action" />,
                    actionLabel: 'View Lifestyle Guide'
                },
                {
                    id: 'yoga',
                    title: 'Yoga & Pranayama',
                    description: 'Practices like Sheetali Pranayama and specific asanas (e.g., Hastapadasana) to improve circulation and reduce tension.',
                    severity: 'Mild / Adjunct',
                    icon: <BodyIcon color="action" />,
                    actionLabel: 'View Routine'
                }
            ]
        }
    }
};

// --- Components ---

const SeverityChip = ({ level }: { level: SeverityLevel }) => {
    let color: 'success' | 'warning' | 'error' | 'default' | 'info' = 'default';
    let label = level;

    if (level.includes('Mild')) color = 'success';
    else if (level.includes('Moderate')) color = 'warning';
    else if (level.includes('Severe')) color = 'error';
    else if (level === 'General') color = 'info';

    return (
        <Chip
            label={label}
            size="small"
            color={color}
            variant={level.includes('/') ? 'outlined' : 'filled'}
            sx={{ fontWeight: 500 }}
        />
    );
};

export default function TreatmentExplorationPage() {
    const { diseaseId } = useParams<{ diseaseId: string }>();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState(0);

    // Fallback to "Migraine" if diseaseId is not found (for demo purposes)
    const diseaseName = diseaseId || 'Migraine';
    const data = MOCK_DATA[diseaseName] || MOCK_DATA['Migraine'];

    const systems: TreatmentSystem[] = ['Modern Medicine', 'Ayurveda', 'Homeopathy', 'Lifestyle'];
    const currentSystem = systems[activeTab];
    const treatments = data.systems[currentSystem] || [];

    const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
        setActiveTab(newValue);
    };

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: '#f8f9fa', pb: 8 }}>
            {/* Header / Nav */}
            <Paper elevation={0} sx={{ borderBottom: 1, borderColor: 'divider', px: 3, py: 2, bgcolor: 'white' }}>
                <Container maxWidth="lg">
                    <Box display="flex" alignItems="center" gap={1}>
                        {/* Simple Header based on design */}
                        <MonitorHeartIcon color="primary" />
                        <Typography variant="h6" fontWeight="bold" color="text.primary">
                            Health Intelligence
                        </Typography>
                        <Box flexGrow={1} />
                        {/* Placeholder for Search/User - simplistic for now */}
                    </Box>
                </Container>
            </Paper>

            <Container maxWidth="lg" sx={{ mt: 4 }}>
                {/* Back Button */}
                <Button
                    startIcon={<ArrowBackIcon />}
                    onClick={() => navigate(-1)}
                    sx={{ mb: 2, textTransform: 'none', color: 'text.secondary' }}
                >
                    Back to Diseases
                </Button>

                {/* Disclaimer Banner */}
                <Alert
                    severity="warning"
                    icon={<InfoIcon fontSize="inherit" />}
                    sx={{ mb: 4, bgcolor: '#fff8e1', color: '#5d4037', border: '1px solid #ffe0b2' }}
                    action={
                        <Button color="inherit" size="small" sx={{ textTransform: 'none', bgcolor: 'white' }}>
                            Dismiss
                        </Button>
                    }
                >
                    <Typography variant="subtitle2" fontWeight="bold">For Informational Use Only</Typography>
                    <Typography variant="body2">
                        This overview is generated by AI to assist in exploration. It is not a medical prescription or diagnosis.
                        Always consult a qualified healthcare provider.
                    </Typography>
                </Alert>

                {/* Title Section */}
                <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
                    Treatment Landscape: {diseaseName}
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ maxWidth: '800px', mb: 4 }}>
                    {data.description}
                </Typography>

                {/* Tabs */}
                <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
                    <Tabs
                        value={activeTab}
                        onChange={handleTabChange}
                        textColor="primary"
                        indicatorColor="primary"
                        variant="scrollable"
                        scrollButtons="auto"
                    >
                        <Tab
                            label="Modern Medicine"
                            icon={<DrugIcon />}
                            iconPosition="start"
                            sx={{ textTransform: 'none', fontWeight: 600 }}
                        />
                        <Tab
                            label="Ayurveda"
                            icon={<LeafIcon />}
                            iconPosition="start"
                            sx={{ textTransform: 'none', fontWeight: 600 }}
                        />
                        <Tab
                            label="Homeopathy"
                            icon={<DropIcon />}
                            iconPosition="start"
                            sx={{ textTransform: 'none', fontWeight: 600 }}
                        />
                        <Tab
                            label="Lifestyle"
                            icon={<BodyIcon />}
                            iconPosition="start"
                            sx={{ textTransform: 'none', fontWeight: 600 }}
                        />
                    </Tabs>
                </Box>

                {/* Active View & Legend */}
                <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2} mb={3}>
                    <Chip label={`Active View: ${currentSystem}`} color="primary" variant="outlined" sx={{ bgcolor: '#e3f2fd', border: 'none' }} />

                    <Stack direction="row" spacing={2} alignItems="center">
                        <Typography variant="caption" color="text.secondary">SEVERITY INDICATORS:</Typography>
                        <Box display="flex" alignItems="center" gap={0.5}>
                            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: 'success.main' }} />
                            <Typography variant="caption">Mild</Typography>
                        </Box>
                        <Box display="flex" alignItems="center" gap={0.5}>
                            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: 'warning.main' }} />
                            <Typography variant="caption">Moderate</Typography>
                        </Box>
                        <Box display="flex" alignItems="center" gap={0.5}>
                            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: 'error.main' }} />
                            <Typography variant="caption">Severe</Typography>
                        </Box>
                    </Stack>
                </Box>

                {/* Content Grid */}
                <Grid container spacing={3}>
                    {treatments.map((item) => (
                        <Grid size={{ xs: 12, md: 6 }} key={item.id}>
                            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', borderRadius: 3, boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
                                <CardContent sx={{ flexGrow: 1, p: 3 }}>
                                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                                        <Box
                                            sx={{
                                                p: 1,
                                                borderRadius: 2,
                                                bgcolor: activeTab === 0 ? 'primary.light' : activeTab === 1 ? 'success.light' : activeTab === 2 ? 'info.light' : 'grey.200',
                                                color: 'white',
                                                display: 'flex'
                                            }}
                                        >
                                            {/* Clone icon to enforce color if needed, or rely on inherit */}
                                            {item.icon}
                                        </Box>
                                        <SeverityChip level={item.severity} />
                                    </Box>

                                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                                        {item.title}
                                    </Typography>

                                    <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                                        {item.description}
                                    </Typography>
                                </CardContent>

                                {item.actionLabel && (
                                    <Box sx={{ p: 2, pt: 0 }}>
                                        <Divider sx={{ mb: 2 }} />
                                        <Button
                                            startIcon={<BookIcon />}
                                            size="small"
                                            sx={{ textTransform: 'none' }}
                                        >
                                            {item.actionLabel}
                                        </Button>
                                    </Box>
                                )}
                            </Card>
                        </Grid>
                    ))}
                </Grid>

                {/* Footer CTA */}
                <Box sx={{ mt: 8, textAlign: 'center', pb: 4 }}>
                    <Divider sx={{ mb: 4 }} />
                    <Typography variant="h6" gutterBottom fontWeight="bold">Explore Specialist Options</Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                        Would you like to find a specialist who focuses on integrative approaches for {diseaseName}?
                    </Typography>
                    <Button variant="contained" size="large" sx={{ mt: 2, borderRadius: 50, px: 4, textTransform: 'none', fontWeight: 'bold' }}>
                        Find a Specialist
                    </Button>
                </Box>
            </Container>
        </Box>
    );
}
