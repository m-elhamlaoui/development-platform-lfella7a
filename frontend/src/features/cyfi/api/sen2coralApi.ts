import { Sen2CoralAnalysisParams, Sen2CoralResults, Sen2CoralApiError } from '../types/sen2coral';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function analyzeSen2Coral(params: Sen2CoralAnalysisParams): Promise<Sen2CoralResults> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/sen2coral/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Sen2CoralApiError(error);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Sen2CoralApiError) {
      throw error;
    }
    throw new Sen2CoralApiError({
      code: 'UNKNOWN_ERROR',
      message: 'An unexpected error occurred while analyzing the data',
    });
  }
}

export async function checkSen2CoralStatus(jobId: string): Promise<{
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  result?: Sen2CoralResults;
  error?: string;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/sen2coral/status/${jobId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Sen2CoralApiError(error);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Sen2CoralApiError) {
      throw error;
    }
    throw new Sen2CoralApiError({
      code: 'STATUS_CHECK_ERROR',
      message: 'Failed to check analysis status',
    });
  }
}

export async function getSen2CoralCapabilities(): Promise<{
  analysisTypes: string[];
  waterQualityIndices: string[];
  habitatClasses: string[];
  maxArea: number;
  supportedSatellites: string[];
  processingLimits: {
    maxCloudCover: number;
    maxTimeRange: number;
    maxResolution: number;
  };
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/sen2coral/capabilities`);

    if (!response.ok) {
      const error = await response.json();
      throw new Sen2CoralApiError(error);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Sen2CoralApiError) {
      throw error;
    }
    throw new Sen2CoralApiError({
      code: 'CAPABILITIES_ERROR',
      message: 'Failed to fetch Sen2Coral capabilities',
    });
  }
} 