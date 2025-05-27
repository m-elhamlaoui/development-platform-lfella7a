import type { BBox } from '@/utils/mapDrawingHelper';

export type Sen2CoralDataSource = 'sentinel2' | 'sambuca' | 'combined';

export interface Sen2CoralAnalysisParams {
  coordinates: BBox;
  timeRange: {
    startDate: string;
    endDate: string;
  };
  dataSource: Sen2CoralDataSource;
  analysisType: 'water_quality' | 'habitat' | 'bathymetry' | 'change_detection';
  options?: {
    cloudMaskThreshold?: number;
    waterQualityIndices?: string[];
    habitatClasses?: string[];
    depthRange?: {
      min: number;
      max: number;
    };
  };
}

export interface WaterQualityMetrics {
  ndwi: number;
  clarity: number;
  turbidity: number;
  chlorophyll: number;
  dissolvedOrganics: number;
}

export interface HabitatMetrics {
  coralCover: number;
  seagrassCover: number;
  sandCover: number;
  rockCover: number;
  classification: Record<string, number>;
}

export interface BathymetryMetrics {
  meanDepth: number;
  minDepth: number;
  maxDepth: number;
  depthConfidence: number;
}

export interface ChangeDetectionMetrics {
  waterQualityChange: number;
  habitatChange: number;
  depthChange: number;
  changeConfidence: number;
}

export interface Sen2CoralResults {
  bbox: BBox;
  timestamp: string;
  waterQuality?: WaterQualityMetrics;
  habitat?: HabitatMetrics;
  bathymetry?: BathymetryMetrics;
  changeDetection?: ChangeDetectionMetrics;
  geojson: {
    type: 'FeatureCollection';
    features: Array<{
      type: 'Feature';
      geometry: {
        type: 'Polygon';
        coordinates: number[][][];
      };
      properties: {
        analysisType: string;
        metrics: Record<string, number>;
        confidence: number;
      };
    }>;
  };
  metadata: {
    processingTime: number;
    cloudCover: number;
    dataQuality: number;
    algorithmVersion: string;
  };
}

export class Sen2CoralApiError extends Error {
  constructor(public error: { code: string; message: string }) {
    super(error.message);
    this.name = 'Sen2CoralApiError';
  }
} 