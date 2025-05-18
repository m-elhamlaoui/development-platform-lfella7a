'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  Box,
  Container,
  Paper,
  Typography,
  Alert,
  Stack,
  Button,
  TextField,
  CircularProgress,
  LinearProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
} from '@mui/material';
import MapSelector from '@/components/MapSelector';
import type { BBox } from '@/utils/mapDrawingHelper';
import { analyzeSen2Coral, checkSen2CoralStatus, getSen2CoralCapabilities } from '@/features/cyfi/api/sen2coralApi';
import type { Sen2CoralAnalysisParams, Sen2CoralResults } from '@/features/cyfi/types/sen2coral';
import Sen2CoralVisualization from '@/features/cyfi/components/Sen2CoralVisualization';
import { toast } from 'react-hot-toast';

interface Sen2CoralState {
  analysisParams: {
    coordinates: BBox | null;
    timeRange: {
      startDate: string;
      endDate: string;
    };
    dataSource: 'sentinel2' | 'sambuca' | 'combined';
    analysisType: 'water_quality' | 'habitat' | 'bathymetry' | 'change_detection';
    options: {
      cloudMaskThreshold: number;
      waterQualityIndices: string[];
      habitatClasses: string[];
    };
  };
  capabilities: {
    analysisTypes: string[];
    waterQualityIndices: string[];
    habitatClasses: string[];
  } | null;
  results: Sen2CoralResults | null;
  ui: {
    isAnalyzing: boolean;
    progress: number;
    errorMessages: {
      analysis: string | null;
      coordinates: string | null;
      dates: string | null;
    };
  };
}

const initialState: Sen2CoralState = {
  analysisParams: {
    coordinates: null,
    timeRange: {
      startDate: '',
      endDate: '',
    },
    dataSource: 'sentinel2',
    analysisType: 'water_quality',
    options: {
      cloudMaskThreshold: 20,
      waterQualityIndices: ['ndwi', 'clarity', 'turbidity'],
      habitatClasses: ['coral', 'seagrass', 'sand'],
    },
  },
  capabilities: null,
  results: null,
  ui: {
    isAnalyzing: false,
    progress: 0,
    errorMessages: {
      analysis: null,
      coordinates: null,
      dates: null,
    },
  },
};

export default function Sen2CoralAnalysis() {
  const [state, setState] = useState<Sen2CoralState>(initialState);
  const searchParams = useSearchParams();

  // Load capabilities on mount
  useEffect(() => {
    const loadCapabilities = async () => {
      try {
        const capabilities = await getSen2CoralCapabilities();
        setState(prev => ({
          ...prev,
          capabilities: {
            analysisTypes: capabilities.analysisTypes,
            waterQualityIndices: capabilities.waterQualityIndices,
            habitatClasses: capabilities.habitatClasses,
          },
        }));
      } catch (error) {
        console.error('Failed to load capabilities:', error);
        toast.error('Failed to load analysis capabilities');
      }
    };

    loadCapabilities();
  }, []);

  // Handle URL parameters
  useEffect(() => {
    if (!searchParams) return;
    
    const west = searchParams.get('west');
    const south = searchParams.get('south');
    const east = searchParams.get('east');
    const north = searchParams.get('north');

    if (west && south && east && north) {
      setState(prev => ({
        ...prev,
        analysisParams: {
          ...prev.analysisParams,
          coordinates: {
            west: parseFloat(west),
            south: parseFloat(south),
            east: parseFloat(east),
            north: parseFloat(north),
          },
        },
      }));
    }
  }, [searchParams]);

  const handleDateChange = (field: 'startDate' | 'endDate', value: string) => {
    setState(prev => ({
      ...prev,
      analysisParams: {
        ...prev.analysisParams,
        timeRange: {
          ...prev.analysisParams.timeRange,
          [field]: value,
        },
      },
    }));
  };

  const handleBBoxSelected = (bbox: BBox) => {
    setState(prev => ({
      ...prev,
      analysisParams: {
        ...prev.analysisParams,
        coordinates: bbox,
      },
      ui: {
        ...prev.ui,
        errorMessages: {
          ...prev.ui.errorMessages,
          coordinates: null,
        },
      },
    }));
  };

  const handleAnalysisTypeChange = (value: 'water_quality' | 'habitat' | 'bathymetry' | 'change_detection') => {
    setState(prev => ({
      ...prev,
      analysisParams: {
        ...prev.analysisParams,
        analysisType: value,
      },
    }));
  };

  const validateInputs = () => {
    const errors: string[] = [];
    
    // Validate coordinates
    const coords = state.analysisParams.coordinates;
    if (!coords) {
      errors.push('Please select an area on the map');
    } else {
      if (coords.west >= coords.east) {
        errors.push('West longitude must be less than East longitude');
      }
      if (coords.south >= coords.north) {
        errors.push('South latitude must be less than North latitude');
      }
      if (coords.west < -180 || coords.east > 180) {
        errors.push('Longitude must be between -180 and 180 degrees');
      }
      if (coords.south < -90 || coords.north > 90) {
        errors.push('Latitude must be between -90 and 90 degrees');
      }
    }

    // Validate dates
    const { startDate, endDate } = state.analysisParams.timeRange;
    if (!startDate || !endDate) {
      errors.push('Both start and end dates are required');
    } else {
      const start = new Date(startDate);
      const end = new Date(endDate);
      
      if (isNaN(start.getTime()) || isNaN(end.getTime())) {
        errors.push('Invalid date format');
      } else if (start > end) {
        errors.push('Start date must be before end date');
      }
    }

    if (errors.length > 0) {
      setState(prev => ({
        ...prev,
        ui: {
          ...prev.ui,
          errorMessages: {
            ...prev.ui.errorMessages,
            analysis: errors.join('. '),
          },
        },
      }));
      return false;
    }

    setState(prev => ({
      ...prev,
      ui: {
        ...prev.ui,
        errorMessages: {
          analysis: null,
          coordinates: null,
          dates: null,
        },
      },
    }));
    return true;
  };

  const handleAnalyze = async () => {
    if (!validateInputs()) return;

    setState(prev => ({
      ...prev,
      ui: {
        ...prev.ui,
        isAnalyzing: true,
        progress: 0,
        errorMessages: {
          ...prev.ui.errorMessages,
          analysis: null,
        },
      },
    }));

    try {
      const result = await analyzeSen2Coral({
        coordinates: state.analysisParams.coordinates!,
        timeRange: state.analysisParams.timeRange,
        dataSource: state.analysisParams.dataSource,
        analysisType: state.analysisParams.analysisType,
        options: state.analysisParams.options,
      });

      setState(prev => ({
        ...prev,
        results: result,
        ui: {
          ...prev.ui,
          isAnalyzing: false,
          progress: 100,
        },
      }));

      toast.success('Analysis completed successfully!');
    } catch (error) {
      console.error('Analysis failed:', error);
      
      const errorMessage = error instanceof Error 
        ? error.message 
        : 'An unexpected error occurred during analysis';

      setState(prev => ({
        ...prev,
        ui: {
          ...prev.ui,
          isAnalyzing: false,
          progress: 0,
          errorMessages: {
            ...prev.ui.errorMessages,
            analysis: errorMessage,
          },
        },
      }));

      toast.error(errorMessage);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Sen2Coral Analysis
      </Typography>

      <Box sx={{ flexGrow: 1 }}>
        <Stack spacing={3}>
          <Paper sx={{ p: 3 }}>
            <Stack spacing={3}>
              <Typography variant="h6">
                Analysis Parameters
              </Typography>

              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Select Area of Interest
                </Typography>
                <Box sx={{ height: 500, mb: 2 }}>
                  <MapSelector 
                    onBBoxSelected={handleBBoxSelected}
                    initialBBox={state.analysisParams.coordinates || undefined}
                  />
                </Box>
                {state.ui.errorMessages.coordinates && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {state.ui.errorMessages.coordinates}
                  </Alert>
                )}
              </Box>

              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Analysis Configuration
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Analysis Type</InputLabel>
                      <Select
                        value={state.analysisParams.analysisType}
                        onChange={(e) => handleAnalysisTypeChange(e.target.value as any)}
                        disabled={state.ui.isAnalyzing}
                      >
                        <MenuItem value="water_quality">Water Quality</MenuItem>
                        <MenuItem value="habitat">Habitat Mapping</MenuItem>
                        <MenuItem value="bathymetry">Bathymetry</MenuItem>
                        <MenuItem value="change_detection">Change Detection</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Data Source</InputLabel>
                      <Select
                        value={state.analysisParams.dataSource}
                        onChange={(e) => setState(prev => ({
                          ...prev,
                          analysisParams: {
                            ...prev.analysisParams,
                            dataSource: e.target.value as any,
                          },
                        }))}
                        disabled={state.ui.isAnalyzing}
                      >
                        <MenuItem value="sentinel2">Sentinel-2</MenuItem>
                        <MenuItem value="sambuca">Sambuca</MenuItem>
                        <MenuItem value="combined">Combined</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
              </Box>

              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Time Range
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Start Date"
                      type="date"
                      value={state.analysisParams.timeRange.startDate}
                      onChange={(e) => handleDateChange('startDate', e.target.value)}
                      InputLabelProps={{ shrink: true }}
                      disabled={state.ui.isAnalyzing}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="End Date"
                      type="date"
                      value={state.analysisParams.timeRange.endDate}
                      onChange={(e) => handleDateChange('endDate', e.target.value)}
                      InputLabelProps={{ shrink: true }}
                      disabled={state.ui.isAnalyzing}
                    />
                  </Grid>
                </Grid>
                {state.ui.errorMessages.dates && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {state.ui.errorMessages.dates}
                  </Alert>
                )}
              </Box>

              <Box>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleAnalyze}
                  disabled={!state.analysisParams.coordinates || state.ui.isAnalyzing}
                  startIcon={state.ui.isAnalyzing ? <CircularProgress size={20} /> : null}
                >
                  {state.ui.isAnalyzing ? 'Analyzing...' : 'Start Analysis'}
                </Button>
              </Box>

              {state.ui.errorMessages.analysis && (
                <Alert severity="error">
                  {state.ui.errorMessages.analysis}
                </Alert>
              )}

              {state.ui.isAnalyzing && (
                <Box sx={{ width: '100%', mt: 2 }}>
                  <LinearProgress variant="determinate" value={state.ui.progress} />
                  <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
                    {Math.round(state.ui.progress)}% Complete
                  </Typography>
                </Box>
              )}
            </Stack>
          </Paper>

          {state.results && (
            <Sen2CoralVisualization 
              results={state.results}
              isLoading={state.ui.isAnalyzing}
            />
          )}
        </Stack>
      </Box>
    </Container>
  );
} 