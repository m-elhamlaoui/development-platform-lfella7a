import React from 'react';
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Tabs,
  Tab,
  Chip,
} from '@mui/material';
import type { Sen2CoralResults } from '../types/sen2coral';
import dynamic from 'next/dynamic';

const MapSelector = dynamic(() => import('@/components/MapSelector'), {
  ssr: false,
  loading: () => <CircularProgress />,
});

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
      id={`sen2coral-tabpanel-${index}`}
      aria-labelledby={`sen2coral-tab-${index}`}
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

interface MetricCardProps {
  label: string;
  value: number;
  unit?: string;
  color?: string;
}

function MetricCard({ label, value, unit, color }: MetricCardProps) {
  return (
    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: color || 'background.paper', mb: 2 }}>
      <Typography variant="h6" gutterBottom>
        {label}
      </Typography>
      <Typography variant="h4">
        {value.toFixed(2)}{unit && ` ${unit}`}
      </Typography>
    </Paper>
  );
}

interface Props {
  results: Sen2CoralResults;
  isLoading?: boolean;
}

export default function Sen2CoralVisualization({ results, isLoading }: Props) {
  const [selectedTab, setSelectedTab] = React.useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper sx={{ mt: 3 }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={selectedTab} onChange={handleTabChange} aria-label="sen2coral analysis tabs">
          {results.waterQuality && <Tab label="Water Quality" />}
          {results.habitat && <Tab label="Habitat" />}
          {results.bathymetry && <Tab label="Bathymetry" />}
          {results.changeDetection && <Tab label="Change Detection" />}
        </Tabs>
      </Box>

      {/* Water Quality Tab */}
      {results.waterQuality && (
        <TabPanel value={selectedTab} index={0}>
          <Box sx={{ display: 'flex', gap: 3 }}>
            <Box sx={{ flex: '2 1 0', minWidth: 0 }}>
              <Box sx={{ height: 400 }}>
                <MapSelector
                  initialBBox={results.bbox}
                />
              </Box>
            </Box>
            <Box sx={{ flex: '1 1 0', minWidth: 0 }}>
              <MetricCard
                label="Water Clarity"
                value={results.waterQuality.clarity}
                unit="%"
                color="#e3f2fd"
              />
              <MetricCard
                label="Turbidity"
                value={results.waterQuality.turbidity}
                unit="NTU"
                color="#e8f5e9"
              />
              <MetricCard
                label="Chlorophyll"
                value={results.waterQuality.chlorophyll}
                unit="μg/L"
                color="#f3e5f5"
              />
            </Box>
          </Box>
        </TabPanel>
      )}

      {/* Habitat Tab */}
      {results.habitat && (
        <TabPanel value={selectedTab} index={1}>
          <Box sx={{ display: 'flex', gap: 3 }}>
            <Box sx={{ flex: '2 1 0', minWidth: 0 }}>
              <Box sx={{ height: 400 }}>
                <MapSelector
                  initialBBox={results.bbox}
                />
              </Box>
            </Box>
            <Box sx={{ flex: '1 1 0', minWidth: 0 }}>
              <MetricCard
                label="Coral Cover"
                value={results.habitat.coralCover}
                unit="%"
                color="#ffebee"
              />
              <MetricCard
                label="Seagrass Cover"
                value={results.habitat.seagrassCover}
                unit="%"
                color="#e8f5e9"
              />
              <MetricCard
                label="Sand Cover"
                value={results.habitat.sandCover}
                unit="%"
                color="#fff3e0"
              />
            </Box>
          </Box>
        </TabPanel>
      )}

      {/* Bathymetry Tab */}
      {results.bathymetry && (
        <TabPanel value={selectedTab} index={2}>
          <Box sx={{ display: 'flex', gap: 3 }}>
            <Box sx={{ flex: '2 1 0', minWidth: 0 }}>
              <Box sx={{ height: 400 }}>
                <MapSelector
                  initialBBox={results.bbox}
                />
              </Box>
            </Box>
            <Box sx={{ flex: '1 1 0', minWidth: 0 }}>
              <MetricCard
                label="Mean Depth"
                value={results.bathymetry.meanDepth}
                unit="m"
                color="#e3f2fd"
              />
              <MetricCard
                label="Depth Range"
                value={results.bathymetry.maxDepth - results.bathymetry.minDepth}
                unit="m"
                color="#bbdefb"
              />
              <MetricCard
                label="Confidence"
                value={results.bathymetry.depthConfidence * 100}
                unit="%"
                color="#90caf9"
              />
            </Box>
          </Box>
        </TabPanel>
      )}

      {/* Change Detection Tab */}
      {results.changeDetection && (
        <TabPanel value={selectedTab} index={3}>
          <Box sx={{ display: 'flex', gap: 3 }}>
            <Box sx={{ flex: '2 1 0', minWidth: 0 }}>
              <Box sx={{ height: 400 }}>
                <MapSelector
                  initialBBox={results.bbox}
                />
              </Box>
            </Box>
            <Box sx={{ flex: '1 1 0', minWidth: 0 }}>
              <MetricCard
                label="Water Quality Change"
                value={results.changeDetection.waterQualityChange}
                unit="%"
                color="#f3e5f5"
              />
              <MetricCard
                label="Habitat Change"
                value={results.changeDetection.habitatChange}
                unit="%"
                color="#e1bee7"
              />
              <MetricCard
                label="Change Confidence"
                value={results.changeDetection.changeConfidence * 100}
                unit="%"
                color="#ce93d8"
              />
            </Box>
          </Box>
        </TabPanel>
      )}

      {/* Metadata Section */}
      <Box sx={{ p: 3, borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="subtitle2" gutterBottom>
          Analysis Metadata
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Chip
            label={`Processing Time: ${results.metadata.processingTime.toFixed(1)}s`}
            variant="outlined"
          />
          <Chip
            label={`Cloud Cover: ${results.metadata.cloudCover.toFixed(1)}%`}
            variant="outlined"
          />
          <Chip
            label={`Data Quality: ${results.metadata.dataQuality.toFixed(1)}%`}
            variant="outlined"
          />
          <Chip
            label={`Algorithm: v${results.metadata.algorithmVersion}`}
            variant="outlined"
          />
        </Box>
      </Box>
    </Paper>
  );
} 