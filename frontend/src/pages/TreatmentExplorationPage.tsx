
// ============================================================================
// Treatment Exploration Page - API-driven, fully rendered
// ============================================================================

import React, { useState, useEffect } from 'react';
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
    CircularProgress,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
<<<<<<< HEAD
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
=======
    useTheme,
    alpha,
>>>>>>> d205e2c3b4d37e237e6680a1b659b923cf7962e9
} from '@mui/material';
import {
    ArrowBack as ArrowBackIcon,
    InfoOutlined as InfoIcon,
    LocalPharmacy as DrugIcon,
    Spa as LeafIcon,
    WaterDrop as DropIcon,
    AccessibilityNew as BodyIcon,
<<<<<<< HEAD
    Refresh as RefreshIcon,
    FiberManualRecord as DotIcon,
    Restaurant as DietIcon,
    DirectionsRun as ExerciseIcon,
    SelfImprovement as StressIcon,
    Bedtime as SleepIcon,
    PriorityHigh as UrgentIcon,
    Block as BlockIcon,
    CheckCircleOutline as CheckIcon,
    OpenInNew as LinkIcon,
=======
    MenuBook as BookIcon,
    MonitorHeart as MonitorHeartIcon,
>>>>>>> d205e2c3b4d37e237e6680a1b659b923cf7962e9
} from '@mui/icons-material';
import { apiService } from '@/services/api';

<<<<<<< HEAD
// ---- Types ----
=======
import ClinicalGuidelinesModal from '@/components/ClinicalGuidelinesModal';

// --- Types ---
>>>>>>> d205e2c3b4d37e237e6680a1b659b923cf7962e9

type TreatmentSystem = 'Modern Medicine' | 'Ayurveda' | 'Homeopathy' | 'Lifestyle';

interface TreatmentData {
    disease: string;
    systems?: Record<string, any>;
    clinical_guidelines?: { guidelines?: string; sources?: any[]; success?: boolean };
    evidence_analysis?: string;
    disclaimer?: string;
    treatment_info?: string;
    sources?: any[];
    [key: string]: any;
}

// ---- Constants ----

const systemIcons: Record<string, React.ReactNode> = {
    'Modern Medicine': <DrugIcon />,
    'Ayurveda': <LeafIcon />,
    'Homeopathy': <DropIcon />,
    'Lifestyle': <BodyIcon />,
};

const systemKeys: Record<TreatmentSystem, string> = {
    'Modern Medicine': 'allopathy',
    'Ayurveda': 'ayurveda',
    'Homeopathy': 'homeopathy',
    'Lifestyle': 'lifestyle',
};

const priorityColor: Record<string, 'error' | 'warning' | 'success' | 'default'> = {
    high: 'error',
    medium: 'warning',
    low: 'success',
};

// ---- Sub-components ----

/** Renders a plain text block, splitting on newlines into paragraphs */
function TextContent({ text }: { text: string }) {
    const paragraphs = text.split(/\n+/).filter(Boolean);
    return (
        <Stack spacing={1.5}>
            {paragraphs.map((p, i) => (
                <Typography key={i} variant="body2" color="text.secondary" sx={{ lineHeight: 1.8 }}>
                    {p}
                </Typography>
            ))}
        </Stack>
    );
}

/** Renders a list of items with a bullet */
function BulletList({ items }: { items: string[] }) {
    return (
        <List dense disablePadding>
            {items.map((item, i) => (
                <ListItem key={i} disableGutters sx={{ alignItems: 'flex-start', py: 0.25 }}>
                    <ListItemIcon sx={{ minWidth: 24, mt: 0.5 }}>
                        <DotIcon sx={{ fontSize: 8, color: 'primary.main' }} />
                    </ListItemIcon>
                    <ListItemText
                        primary={item}
                        primaryTypographyProps={{ variant: 'body2', color: 'text.secondary', lineHeight: 1.7 }}
                    />
                </ListItem>
            ))}
        </List>
    );
}

/** Section card with icon, title, and children */
function SectionCard({
    icon,
    title,
    color = '#f5f5f5',
    children,
}: {
    icon: React.ReactNode;
    title: string;
    color?: string;
    children: React.ReactNode;
}) {
    return (
        <Card elevation={0} sx={{ border: '1px solid #e0e0e0', borderRadius: 2, overflow: 'hidden' }}>
            <Box sx={{ px: 2.5, py: 1.5, bgcolor: color, display: 'flex', alignItems: 'center', gap: 1 }}>
                {icon}
                <Typography variant="subtitle1" fontWeight={700}>{title}</Typography>
            </Box>
            <CardContent sx={{ pt: 2 }}>{children}</CardContent>
        </Card>
    );
}

/** Renders the Lifestyle structured JSON beautifully */
function LifestyleContent({ data }: { data: any }) {
    if (!data) return null;

    // If it's just a text plan (fallback from LLM)
    if (data.text_plan) return <TextContent text={data.text_plan} />;
    // If it's a plain string
    if (typeof data === 'string') return <TextContent text={data} />;
    // If it's the raw treatment_info string
    if (data.treatment_info && typeof data.treatment_info === 'string') {
        return <TextContent text={data.treatment_info} />;
    }

    const {
        diet_plan = [],
        exercise_plan = [],
        stress_management = [],
        sleep_hygiene = [],
        immediate_actions = [],
        contraindications = [],
        personalization_notes,
    } = data;

    return (
        <Stack spacing={3}>
            {/* Immediate Actions */}
            {immediate_actions.length > 0 && (
                <SectionCard icon={<UrgentIcon color="error" />} title="Start Today" color="#fff3e0">
                    <BulletList items={immediate_actions} />
                </SectionCard>
            )}

            {/* Diet Plan */}
            {diet_plan.length > 0 && (
                <SectionCard icon={<DietIcon color="success" />} title="Diet & Nutrition" color="#f1f8e9">
                    <Stack spacing={1.5}>
                        {diet_plan.map((item: any, i: number) => (
                            <Box key={i} sx={{ display: 'flex', gap: 1.5, alignItems: 'flex-start' }}>
                                <CheckIcon sx={{ fontSize: 18, color: 'success.main', mt: 0.3, flexShrink: 0 }} />
                                <Box>
                                    <Typography variant="body2" fontWeight={600} color="text.primary">
                                        {item.recommendation}
                                    </Typography>
                                    {item.evidence && (
                                        <Typography variant="caption" color="text.secondary">
                                            {item.evidence}
                                        </Typography>
                                    )}
                                </Box>
                                {item.priority && (
                                    <Chip
                                        label={item.priority}
                                        size="small"
                                        color={priorityColor[item.priority?.toLowerCase()] || 'default'}
                                        sx={{ ml: 'auto', flexShrink: 0, height: 20, fontSize: '0.65rem' }}
                                    />
                                )}
                            </Box>
                        ))}
                    </Stack>
                </SectionCard>
            )}

            {/* Exercise Plan */}
            {exercise_plan.length > 0 && (
                <SectionCard icon={<ExerciseIcon color="primary" />} title="Physical Activity" color="#e3f2fd">
                    <Stack spacing={1.5}>
                        {exercise_plan.map((item: any, i: number) => (
                            <Box key={i} sx={{ p: 1.5, bgcolor: '#f8f9fa', borderRadius: 1.5 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                                    <Typography variant="body2" fontWeight={600}>{item.activity}</Typography>
                                    {item.priority && (
                                        <Chip
                                            label={item.priority}
                                            size="small"
                                            color={priorityColor[item.priority?.toLowerCase()] || 'default'}
                                            sx={{ height: 20, fontSize: '0.65rem' }}
                                        />
                                    )}
                                </Box>
                                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                                    {item.frequency && (
                                        <Typography variant="caption" color="text.secondary">
                                            📅 {item.frequency}
                                        </Typography>
                                    )}
                                    {item.duration && (
                                        <Typography variant="caption" color="text.secondary">
                                            ⏱ {item.duration}
                                        </Typography>
                                    )}
                                </Box>
                                {item.safety_notes && (
                                    <Typography variant="caption" color="warning.dark" sx={{ display: 'block', mt: 0.5 }}>
                                        ⚠ {item.safety_notes}
                                    </Typography>
                                )}
                            </Box>
                        ))}
                    </Stack>
                </SectionCard>
            )}

            {/* Stress Management */}
            {stress_management.length > 0 && (
                <SectionCard icon={<StressIcon color="secondary" />} title="Stress Management" color="#f3e5f5">
                    <Stack spacing={1.5}>
                        {stress_management.map((item: any, i: number) => (
                            <Box key={i}>
                                <Typography variant="body2" fontWeight={600} color="text.primary">
                                    {item.technique}
                                </Typography>
                                {item.how_to && (
                                    <Typography variant="caption" color="text.secondary" display="block">
                                        {item.how_to}
                                    </Typography>
                                )}
                                {item.evidence && (
                                    <Typography variant="caption" color="text.secondary" fontStyle="italic">
                                        {item.evidence}
                                    </Typography>
                                )}
                            </Box>
                        ))}
                    </Stack>
                </SectionCard>
            )}

            {/* Sleep Hygiene */}
            {sleep_hygiene.length > 0 && (
                <SectionCard icon={<SleepIcon sx={{ color: '#5c6bc0' }} />} title="Sleep Hygiene" color="#e8eaf6">
                    <Stack spacing={1}>
                        {sleep_hygiene.map((item: any, i: number) => (
                            <Box key={i} sx={{ display: 'flex', gap: 1.5, alignItems: 'flex-start' }}>
                                <CheckIcon sx={{ fontSize: 16, color: '#5c6bc0', mt: 0.4, flexShrink: 0 }} />
                                <Box>
                                    <Typography variant="body2" fontWeight={600}>{item.tip}</Typography>
                                    {item.rationale && (
                                        <Typography variant="caption" color="text.secondary">{item.rationale}</Typography>
                                    )}
                                </Box>
                            </Box>
                        ))}
                    </Stack>
                </SectionCard>
            )}

            {/* Contraindications */}
            {contraindications.length > 0 && (
                <SectionCard icon={<BlockIcon color="error" />} title="Avoid These" color="#ffebee">
                    <BulletList items={contraindications} />
                </SectionCard>
            )}

            {/* Personalization note */}
            {personalization_notes && (
                <Paper sx={{ p: 2, bgcolor: '#e8f5e9', border: '1px solid #c8e6c9', borderRadius: 2 }}>
                    <Typography variant="caption" color="text.secondary" fontStyle="italic">
                        💡 {personalization_notes}
                    </Typography>
                </Paper>
            )}
        </Stack>
    );
}

/** Renders allopathy / ayurveda / homeopathy treatment text */
function TreatmentTextContent({ data }: { data: any }) {
    if (!data) return null;

    const text: string =
        typeof data === 'string'
            ? data
            : data.treatment_info || data.guidelines || '';

    if (!text) return null;

    // Split into numbered sections if present (e.g. "1. ...\n2. ...")
    const lines = text.split(/\n+/).filter(Boolean);

    return (
        <Stack spacing={1.5}>
            {lines.map((line, i) => {
                const isHeading = /^#+\s|^\d+\.\s/.test(line);
                return (
                    <Typography
                        key={i}
                        variant={isHeading ? 'subtitle2' : 'body2'}
                        fontWeight={isHeading ? 700 : 400}
                        color={isHeading ? 'text.primary' : 'text.secondary'}
                        sx={{ lineHeight: 1.8 }}
                    >
                        {line.replace(/^#+\s/, '')}
                    </Typography>
                );
            })}
        </Stack>
    );
}

/** Sources list */
function SourcesList({ sources }: { sources: any[] }) {
    if (!sources?.length) return null;
    return (
        <Box mt={2}>
            <Typography variant="caption" color="text.secondary" fontWeight={600} display="block" mb={0.5}>
                Sources
            </Typography>
            <Stack spacing={0.5}>
                {sources.slice(0, 5).map((s: any, i: number) => (
                    <Box key={i} display="flex" alignItems="center" gap={0.5}>
                        <LinkIcon sx={{ fontSize: 12, color: 'primary.main' }} />
                        {s.url ? (
                            <Typography
                                component="a"
                                href={s.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                variant="caption"
                                color="primary.main"
                                sx={{ textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
                            >
                                {s.title || s.source || s.url}
                            </Typography>
                        ) : (
                            <Typography variant="caption" color="text.secondary">
                                {s.title || s.source || `Source ${i + 1}`}
                            </Typography>
                        )}
                    </Box>
                ))}
            </Stack>
        </Box>
    );
}

// ---- Main Component ----

export default function TreatmentExplorationPage() {
    const { diseaseId } = useParams<{ diseaseId: string }>();
    const navigate = useNavigate();
<<<<<<< HEAD
=======
    const theme = useTheme();
    const [activeTab, setActiveTab] = useState(0);
    const [selectedAction, setSelectedAction] = useState<{ type: string; treatment: string; disease: string } | null>(null);
  const [selectedGuideline, setSelectedGuideline] = useState<{ treatment: string; disease: string } | null>(null);
>>>>>>> d205e2c3b4d37e237e6680a1b659b923cf7962e9

    const [activeTab, setActiveTab] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<TreatmentData | null>(null);
    const [guidelinesOpen, setGuidelinesOpen] = useState(false);

    const diseaseName = (diseaseId || '')
        .split('-')
        .map(w => w.charAt(0).toUpperCase() + w.slice(1))
        .join(' ');

    const fetchTreatment = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiService.client.post('/api/treatment/explore/', {
                disease: diseaseName,
                system: 'all',
                include_evidence: true,
            });
            const result = response.data;
            if (result.success && result.data) {
                setData(result.data);
            } else {
                setError(result.message || 'No treatment data returned.');
            }
        } catch (err: any) {
            setError(
                err.response?.data?.message ||
                err.message ||
                'Failed to load treatment information.'
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchTreatment(); }, [diseaseId]);

    const systems: TreatmentSystem[] = ['Modern Medicine', 'Ayurveda', 'Homeopathy', 'Lifestyle'];
    const currentSystem = systems[activeTab];
    const currentKey = systemKeys[currentSystem];

    const getSystemData = () => {
        if (!data) return null;
        if (data.systems) return data.systems[currentKey] || null;
        return data;
    };

<<<<<<< HEAD
    const systemData = getSystemData();
    const guidelines = data?.clinical_guidelines;
    const evidenceAnalysis = data?.evidence_analysis;
    const sources = systemData?.sources || data?.sources || [];

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: '#f8f9fa', pb: 8 }}>
=======
    const handleActionClick = (actionType: string, treatmentTitle: string) => {
        if (actionType === 'View Clinical Guidelines') {
            // Open the Clinical Guidelines modal
            setSelectedGuideline({ treatment: treatmentTitle, disease: normalizedDiseaseName });
        } else {
            // Fallback to generic action dialog
            setSelectedAction({
                type: actionType,
                treatment: treatmentTitle,
                disease: normalizedDiseaseName
            });
        }
    };

    const handleCloseDialog = () => {
        setSelectedAction(null);
    };

    return (
        <Box 
            sx={{ 
                minHeight: '100vh', 
                pb: 8,
                background: `linear-gradient(135deg, ${theme.palette.background.default} 0%, ${theme.palette.background.paper} 100%)`, 
            }}
        >
            {/* Header / Nav */}
            <Paper 
                elevation={0} 
                sx={{ 
                    borderBottom: 1, 
                    borderColor: alpha(theme.palette.divider, 0.1), 
                    px: 3, 
                    py: 2, 
                    background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.6)} 0%, ${alpha(theme.palette.background.paper, 0.3)} 100%)`,
                    backdropFilter: 'blur(20px)',
                    position: 'sticky',
                    top: 0,
                    zIndex: 10,
                    boxShadow: `0 4px 30px ${alpha(theme.palette.common.black, 0.05)}`,
                }}
            >
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

>>>>>>> d205e2c3b4d37e237e6680a1b659b923cf7962e9
            <Container maxWidth="lg" sx={{ mt: 4 }}>
                <Button
                    startIcon={<ArrowBackIcon />}
                    onClick={() => navigate(-1)}
                    sx={{ mb: 2, textTransform: 'none', color: 'text.secondary' }}
                >
                    Back to Diseases
                </Button>

                <Alert
                    severity="warning"
                    icon={<InfoIcon fontSize="inherit" />}
                    sx={{ mb: 4, bgcolor: '#fff8e1', color: '#5d4037', border: '1px solid #ffe0b2' }}
                >
                    <Typography variant="subtitle2" fontWeight="bold">For Informational Use Only</Typography>
                    <Typography variant="body2">
                        This overview is generated by AI to assist in exploration. It is not a medical
                        prescription or diagnosis. Always consult a qualified healthcare provider.
                    </Typography>
                </Alert>

                <Typography variant="h4" fontWeight="bold" gutterBottom>
                    Treatment Landscape: {diseaseName}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
                    Explore evidence-based treatment approaches across multiple medical systems.
                </Typography>

                {loading && (
                    <Box display="flex" alignItems="center" gap={2} mt={4}>
                        <CircularProgress size={28} />
                        <Typography color="text.secondary">
                            Fetching treatment information for {diseaseName}…
                        </Typography>
                    </Box>
                )}

                {!loading && error && (
                    <Alert
                        severity="error"
                        sx={{ mt: 2 }}
                        action={
                            <Button color="inherit" size="small" startIcon={<RefreshIcon />} onClick={fetchTreatment}>
                                Retry
                            </Button>
                        }
                    >
                        {error}
                    </Alert>
                )}

                {!loading && !error && data && (
                    <>
                        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
                            <Tabs
                                value={activeTab}
                                onChange={(_, v) => setActiveTab(v)}
                                textColor="primary"
                                indicatorColor="primary"
                                variant="scrollable"
                                scrollButtons="auto"
                            >
                                {systems.map((sys) => (
                                    <Tab
                                        key={sys}
                                        label={sys}
                                        icon={systemIcons[sys] as React.ReactElement}
                                        iconPosition="start"
                                        sx={{ textTransform: 'none', fontWeight: 600 }}
                                    />
                                ))}
                            </Tabs>
                        </Box>

<<<<<<< HEAD
                        <Grid container spacing={3}>
                            {/* Main content */}
                            <Grid size={{ xs: 12, md: 8 }}>
                                <Card elevation={0} sx={{ border: '1px solid #e0e0e0', borderRadius: 2 }}>
                                    <CardContent sx={{ p: 3 }}>
                                        <Box display="flex" alignItems="center" gap={1} mb={2}>
                                            {systemIcons[currentSystem]}
                                            <Typography variant="h6" fontWeight="bold">
                                                {currentSystem}
=======
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
                        <Grid container spacing={4} sx={{ mt: 2 }}>
                            {treatments.map((item) => (
                                <Grid size={{ xs: 12, md: 6 }} key={item.id}>
                                    <Card 
                                        sx={{ 
                                            height: '100%', 
                                            display: 'flex', 
                                            flexDirection: 'column', 
                                            borderRadius: 4,
                                            background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.4)} 0%, ${alpha(theme.palette.background.paper, 0.1)} 100%)`,
                                            backdropFilter: 'blur(10px)',
                                            border: '1px solid',
                                            borderColor: alpha(theme.palette.divider, 0.2),
                                            transition: 'all 0.3s ease-in-out',
                                            '&:hover': {
                                                transform: 'translateY(-4px)',
                                                boxShadow: `0 12px 40px ${alpha(theme.palette.primary.main, 0.15)}`,
                                                borderColor: alpha(theme.palette.primary.main, 0.3),
                                            },
                                        }}
                                    >
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
>>>>>>> d205e2c3b4d37e237e6680a1b659b923cf7962e9
                                            </Typography>
                                        </Box>
                                        <Divider sx={{ mb: 3 }} />

                                        {systemData ? (
                                            currentSystem === 'Lifestyle'
                                                ? <LifestyleContent data={systemData} />
                                                : <TreatmentTextContent data={systemData} />
                                        ) : (
                                            <Typography color="text.secondary" fontStyle="italic">
                                                No {currentSystem} information available for {diseaseName}.
                                            </Typography>
                                        )}

<<<<<<< HEAD
                                        {sources.length > 0 && (
                                            <>
                                                <Divider sx={{ mt: 3, mb: 1 }} />
                                                <SourcesList sources={sources} />
                                            </>
                                        )}
                                    </CardContent>
                                </Card>
                            </Grid>

                            {/* Sidebar */}
                            <Grid size={{ xs: 12, md: 4 }}>
                                <Stack spacing={2}>
                                    {/* Clinical Guidelines */}
                                    {guidelines && (
                                        <Card elevation={0} sx={{ border: '1px solid #e0e0e0', borderRadius: 2 }}>
                                            <CardContent>
                                                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                                                    📋 Clinical Guidelines
                                                </Typography>
                                                {typeof guidelines.guidelines === 'string' && guidelines.guidelines ? (
                                                    <>
                                                        <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                                                            {guidelines.guidelines.slice(0, 320)}
                                                            {guidelines.guidelines.length > 320 ? '…' : ''}
                                                        </Typography>
                                                        {guidelines.guidelines.length > 320 && (
                                                            <Button
                                                                size="small"
                                                                onClick={() => setGuidelinesOpen(true)}
                                                                sx={{ textTransform: 'none', p: 0, mt: 1 }}
                                                            >
                                                                Read full guidelines
                                                            </Button>
                                                        )}
                                                    </>
                                                ) : (
                                                    <Typography variant="body2" color="text.secondary">
                                                        Guidelines available from authoritative sources.
                                                    </Typography>
                                                )}
                                                {guidelines.sources && guidelines.sources.length > 0 && (
                                                    <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                                                        {guidelines.sources.length} source(s) referenced
                                                    </Typography>
                                                )}
                                            </CardContent>
                                        </Card>
                                    )}

                                    {/* Evidence Analysis */}
                                    {evidenceAnalysis && (
                                        <Card elevation={0} sx={{ border: '1px solid #e0e0e0', borderRadius: 2 }}>
                                            <CardContent>
                                                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                                                    🔬 Evidence Analysis
                                                </Typography>
                                                <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                                                    {evidenceAnalysis.slice(0, 400)}
                                                    {evidenceAnalysis.length > 400 ? '…' : ''}
                                                </Typography>
                                            </CardContent>
                                        </Card>
                                    )}

                                    {/* Disclaimer */}
                                    <Paper sx={{ p: 2, bgcolor: '#fff3e0', border: '1px solid #ffe0b2', borderRadius: 2 }}>
                                        <Typography variant="caption" color="#e65100" sx={{ lineHeight: 1.6, display: 'block' }}>
                                            ⚕️ {data.disclaimer || 'Always consult a qualified healthcare professional before starting any treatment.'}
                                        </Typography>
                                    </Paper>
                                </Stack>
                            </Grid>
                        </Grid>
=======
                        {/* Footer CTA */}
                        <Box sx={{ mt: 8, textAlign: 'center', pb: 4 }}>
                            <Divider sx={{ mb: 4 }} />
                            <Typography variant="h6" gutterBottom fontWeight="bold">Explore Specialist Options</Typography>
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                                Would you like to find a specialist who focuses on integrative approaches for {normalizedDiseaseName}?
                            </Typography>
                            <Button 
                                variant="contained" 
                                size="large" 
                                sx={{ 
                                    mt: 2, 
                                    borderRadius: 50, 
                                    px: 4, 
                                    textTransform: 'none', 
                                    fontWeight: 'bold',
                                    boxShadow: `0 8px 24px ${alpha(theme.palette.primary.main, 0.3)}`,
                                }}
                            >
                                Find a Specialist
                            </Button>
                        </Box>
>>>>>>> d205e2c3b4d37e237e6680a1b659b923cf7962e9
                    </>
                )}
            </Container>

            {/* Full guidelines dialog */}
            <Dialog open={guidelinesOpen} onClose={() => setGuidelinesOpen(false)} maxWidth="md" fullWidth>
                <DialogTitle>Clinical Guidelines — {diseaseName}</DialogTitle>
                <DialogContent dividers>
                    <TreatmentTextContent data={guidelines?.guidelines} />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setGuidelinesOpen(false)}>Close</Button>
                </DialogActions>
            </Dialog>

            {/* Clinical Guidelines Modal */}
            <ClinicalGuidelinesModal
                open={!!selectedGuideline}
                onClose={() => setSelectedGuideline(null)}
                treatmentName={selectedGuideline?.treatment ?? ''}
                diseaseName={selectedGuideline?.disease ?? ''}
            />
        </Box>
    );
}
