import type { AnalysisParams, AnalysisResults, BBox } from '../types/cyfi';
import type { CyFiAnalysisRequest, CyFiAnalysisResult } from '../types/cyfiBackend';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api';

interface AnalysisError {
  message: string;
  details?: string;
}

export class CyFiApiError extends Error {
  constructor(public error: AnalysisError) {
    super(error.message);
    this.name = 'CyFiApiError';
  }
}

export async function analyzeCyFi(params: AnalysisParams): Promise<AnalysisResults> {
  try {
    // Convert frontend params to backend format
    const backendRequest: CyFiAnalysisRequest = {
      bbox: params.coordinates,
      date: params.timeRange.endDate,
      grid_size: 0.001 // Default grid size
    };

    const response = await fetch(`${API_BASE_URL}/cyfi/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendRequest),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new CyFiApiError(error);
    }

    const data: CyFiAnalysisResult = await response.json();
    
    // Convert backend response to frontend format
    return {
      timestamp: data.timestamp,
      densityCellsPerMl: data.predictions.density_cells_per_ml,
      severity: data.predictions.severity,
      confidence: data.predictions.confidence || 0,
      visualizations: {
        heatmap: '', // TODO: Add visualization URLs when implemented
        trueColor: '',
        ndwi: '',
      },
      metadata: {
        dataSource: 'cyfi',
        processingTime: 0, // TODO: Add processing time calculation
        cloudCoverage: 0, // TODO: Add cloud coverage when implemented
      },
    };
  } catch (error) {
    if (error instanceof CyFiApiError) {
      throw error;
    }
    throw new CyFiApiError({
      message: 'Failed to analyze area',
      details: error instanceof Error ? error.message : 'Unknown error occurred',
    });
  }
}

export async function checkAnalysisStatus(analysisId: string): Promise<{
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  error?: string;
}> {
  const response = await fetch(`${API_BASE_URL}/cyfi/status/${analysisId}`);
  if (!response.ok) {
    throw new CyFiApiError({
      message: 'Failed to check analysis status',
    });
  }
  return response.json();
}

export async function cancelAnalysis(analysisId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/cyfi/cancel/${analysisId}`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new CyFiApiError({
      message: 'Failed to cancel analysis',
    });
  }
} 