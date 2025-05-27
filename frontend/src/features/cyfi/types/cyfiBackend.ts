export interface CyFiAnalysisResult {
    timestamp: string;
    bbox?: {
        west: number;
        south: number;
        east: number;
        north: number;
    };
    location?: {
        latitude: number;
        longitude: number;
    };
    predictions: {
        density_cells_per_ml: number;
        severity: 'low' | 'moderate' | 'high';
        confidence?: number;
    };
    metadata: {
        points_analyzed?: number;
        date_analyzed: string;
        grid_size?: number;
    };
}

export interface CyFiBBox {
    west: number;
    south: number;
    east: number;
    north: number;
}

export interface CyFiAnalysisRequest {
    bbox: CyFiBBox;
    date: string;
    grid_size?: number;
} 