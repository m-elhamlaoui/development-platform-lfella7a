export interface BBox {
  west: number;
  south: number;
  east: number;
  north: number;
}

export type DataSource = 'sentinel2' | 'cyfi' | 'combined';

export interface AnalysisParams {
  coordinates: BBox;
  timeRange: {
    startDate: string;
    endDate: string;
  };
  dataSource: DataSource;
}

export interface AnalysisResults {
  timestamp: string;
  densityCellsPerMl: number;
  severity: 'low' | 'moderate' | 'high';
  confidence: number;
  visualizations: {
    heatmap: string;
    trueColor: string;
    ndwi: string;
  };
  metadata: {
    dataSource: string;
    processingTime: number;
    cloudCoverage: number;
  };
}

export interface UIState {
  viewMode: 'map' | 'list';
  selectedTab: string;
  loadingStates: Record<string, boolean>;
  errorMessages: Record<string, string>;
}

export interface CyFiState {
  analysisParams: AnalysisParams;
  results: AnalysisResults | null;
  ui: UIState;
} 