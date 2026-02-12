import React, { useState } from 'react';
import { Box, Tabs, Tab, Paper } from '@mui/material';
import { TreatmentInfo } from '@/types';
import { AllopathyPanel } from './AllopathyPanel';
import { AyurvedaPanel } from './AyurvedaPanel';
import { HomeopathyPanel } from './HomeopathyPanel';
import { LifestylePanel } from './LifestylePanel';

interface TreatmentTabsProps {
  treatmentInfo: TreatmentInfo;
  confidence: 'LOW' | 'MEDIUM' | 'HIGH';
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`treatment-tabpanel-${index}`}
      aria-labelledby={`treatment-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `treatment-tab-${index}`,
    'aria-controls': `treatment-tabpanel-${index}`,
  };
}

export const TreatmentTabs: React.FC<TreatmentTabsProps> = ({ treatmentInfo, confidence }) => {
  const [value, setValue] = useState(0);

  // Hide treatment tabs when confidence level is LOW
  if (confidence === 'LOW') {
    return null;
  }

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <Paper elevation={2} sx={{ mt: 4 }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs 
          value={value} 
          onChange={handleChange} 
          aria-label="treatment system tabs"
          variant="fullWidth"
          sx={{
            '& .MuiTab-root': {
              textTransform: 'none',
              fontWeight: 500,
            }
          }}
        >
          <Tab label="Modern Medicine" {...a11yProps(0)} />
          <Tab label="Ayurveda" {...a11yProps(1)} />
          <Tab label="Homeopathy" {...a11yProps(2)} />
          <Tab label="Lifestyle" {...a11yProps(3)} />
        </Tabs>
      </Box>

      <Box sx={{ p: 3 }}>
        <TabPanel value={value} index={0}>
          <AllopathyPanel treatments={treatmentInfo?.allopathy || []} />
        </TabPanel>
        <TabPanel value={value} index={1}>
          <AyurvedaPanel treatments={treatmentInfo?.ayurveda || []} />
        </TabPanel>
        <TabPanel value={value} index={2}>
          <HomeopathyPanel treatments={treatmentInfo?.homeopathy || []} />
        </TabPanel>
        <TabPanel value={value} index={3}>
          <LifestylePanel treatments={treatmentInfo?.lifestyle || []} />
        </TabPanel>
      </Box>
    </Paper>
  );
};

export default TreatmentTabs;
