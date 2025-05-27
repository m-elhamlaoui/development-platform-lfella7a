'use client';

import { useState } from 'react';
import {
  Box,
  Paper,
  Tab,
  Tabs,
  Typography,
  CircularProgress,
  Stack,
  Tooltip,
  IconButton
} from '@mui/material';
import { Download as DownloadIcon } from '@mui/icons-material';
import type { AnalysisResults } from '../types/cyfi';
import { LineChart } from '@mui/x-charts/LineChart';

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
      id={`viz-tabpanel-${index}`}
      aria-labelledby={`viz-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

interface VisualizationPanelProps {
  results: AnalysisResults;
  isLoading?: boolean;
}

export default function VisualizationPanel({ results, isLoading = false }: VisualizationPanelProps) {
  const [selectedTab, setSelectedTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const handleDownload = (imageUrl: string, type: string) => {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `cyfi-${type}-${new Date().toISOString()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper sx={{ width: '100%', mt: 2 }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={selectedTab} onChange={handleTabChange} aria-label="visualization tabs">
          <Tab label="Heatmap" id="viz-tab-0" />
          <Tab label="NDWI" id="viz-tab-1" />
          <Tab label="True Color" id="viz-tab-2" />
          <Tab label="Time Series" id="viz-tab-3" />
        </Tabs>
      </Box>

      {/* Heatmap View */}
      <TabPanel value={selectedTab} index={0}>
        <Stack spacing={2}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Algal Bloom Density Heatmap</Typography>
            <Tooltip title="Download Heatmap">
              <IconButton onClick={() => handleDownload(results.visualizations.heatmap, 'heatmap')}>
                <DownloadIcon />
              </IconButton>
            </Tooltip>
          </Box>
          <Box
            component="img"
            src={results.visualizations.heatmap}
            alt="Algal bloom density heatmap"
            sx={{
              width: '100%',
              height: 'auto',
              borderRadius: 1,
              boxShadow: 1
            }}
          />
          <Typography variant="body2" color="text.secondary">
            Density scale: cells/mL
          </Typography>
        </Stack>
      </TabPanel>

      {/* NDWI View */}
      <TabPanel value={selectedTab} index={1}>
        <Stack spacing={2}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Normalized Difference Water Index</Typography>
            <Tooltip title="Download NDWI">
              <IconButton onClick={() => handleDownload(results.visualizations.ndwi, 'ndwi')}>
                <DownloadIcon />
              </IconButton>
            </Tooltip>
          </Box>
          <Box
            component="img"
            src={results.visualizations.ndwi}
            alt="NDWI visualization"
            sx={{
              width: '100%',
              height: 'auto',
              borderRadius: 1,
              boxShadow: 1
            }}
          />
          <Typography variant="body2" color="text.secondary">
            NDWI values: -1 (no water) to 1 (clear water)
          </Typography>
        </Stack>
      </TabPanel>

      {/* True Color View */}
      <TabPanel value={selectedTab} index={2}>
        <Stack spacing={2}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">True Color Satellite Image</Typography>
            <Tooltip title="Download True Color Image">
              <IconButton onClick={() => handleDownload(results.visualizations.trueColor, 'true-color')}>
                <DownloadIcon />
              </IconButton>
            </Tooltip>
          </Box>
          <Box
            component="img"
            src={results.visualizations.trueColor}
            alt="True color satellite image"
            sx={{
              width: '100%',
              height: 'auto',
              borderRadius: 1,
              boxShadow: 1
            }}
          />
          <Typography variant="body2" color="text.secondary">
            Natural color representation from Sentinel-2 imagery
          </Typography>
        </Stack>
      </TabPanel>

      {/* Time Series View */}
      <TabPanel value={selectedTab} index={3}>
        <Stack spacing={2}>
          <Typography variant="h6">Historical Density Trends</Typography>
          <Box sx={{ width: '100%', height: 300 }}>
            <LineChart
              xAxis={[{ 
                data: [1, 2, 3, 4, 5],  // Replace with actual timestamps
                label: 'Time' 
              }]}
              series={[
                {
                  data: [2000, 3000, 5000, 4000, 7000],  // Replace with actual density values
                  label: 'Cells/mL',
                },
              ]}
              width={500}
              height={300}
            />
          </Box>
          <Typography variant="body2" color="text.secondary">
            Algal bloom density over time
          </Typography>
        </Stack>
      </TabPanel>
    </Paper>
  );
} 