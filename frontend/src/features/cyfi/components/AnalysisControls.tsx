'use client';

import React from 'react';
import {
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import type { AnalysisParams } from '../types/cyfi';

interface AnalysisControlsProps {
  params: AnalysisParams;
  onParamsChange: (params: AnalysisParams) => void;
  onAnalyze: () => void;
  isLoading: boolean;
}

export default function AnalysisControls({
  params,
  onParamsChange,
  onAnalyze,
  isLoading
}: AnalysisControlsProps) {
  const handleDateChange = (date: Date | null, field: 'start' | 'end') => {
    if (date) {
      const timeRange = [...params.timeRange];
      timeRange[field === 'start' ? 0 : 1] = date;
      onParamsChange({ ...params, timeRange });
    }
  };

  return (
    <Stack spacing={3}>
      <Typography variant="h6" gutterBottom>
        Analysis Parameters
      </Typography>

      <Box>
        <Typography variant="subtitle2" gutterBottom>
          Selected Coordinates
        </Typography>
        <Stack direction="row" spacing={2}>
          <TextField
            label="Latitude"
            value={params.coordinates.lat}
            disabled
            size="small"
            fullWidth
          />
          <TextField
            label="Longitude"
            value={params.coordinates.lon}
            disabled
            size="small"
            fullWidth
          />
        </Stack>
      </Box>

      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <Stack spacing={2}>
          <DatePicker
            label="Start Date"
            value={params.timeRange[0]}
            onChange={(date) => handleDateChange(date, 'start')}
            slotProps={{ textField: { size: 'small' } }}
          />
          <DatePicker
            label="End Date"
            value={params.timeRange[1]}
            onChange={(date) => handleDateChange(date, 'end')}
            slotProps={{ textField: { size: 'small' } }}
          />
        </Stack>
      </LocalizationProvider>

      <FormControl fullWidth size="small">
        <InputLabel>Data Source</InputLabel>
        <Select
          value={params.dataSource}
          label="Data Source"
          onChange={(e) => onParamsChange({ ...params, dataSource: e.target.value as 'sentinel2' | 'cyfi' | 'combined' })}
        >
          <MenuItem value="sentinel2">Sentinel-2</MenuItem>
          <MenuItem value="cyfi">CyFi</MenuItem>
          <MenuItem value="combined">Combined</MenuItem>
        </Select>
      </FormControl>

      <Button
        variant="contained"
        onClick={onAnalyze}
        disabled={isLoading}
        fullWidth
      >
        {isLoading ? 'Analyzing...' : 'Run Analysis'}
      </Button>
    </Stack>
  );
} 