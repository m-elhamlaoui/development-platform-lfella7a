# Project Structure Documentation

## Overview

The project is a web-based application for water quality analysis using Sentinel satellite data. It consists of three main components:

1. Frontend (React/Next.js)
2. Backend (FastAPI)
3. GIS Processing (Python)

## Directory Structure

```
lostcity/
├── frontend/                # Next.js frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── MapSelector.tsx    # Map interface for AOI selection
│   │   │   └── MapSelector.css    # Styles for map component
│   │   ├── utils/
│   │   │   ├── mapDrawingHelper.ts # Map drawing utilities
│   │   │   └── config.ts          # Configuration settings
│   │   └── types/                 # TypeScript type definitions
│   └── public/                    # Static assets
│
├── backend/                # FastAPI backend service
│   ├── src/
│   │   └── main/
│   │       └── python/
│   │           └── bloombuddy/    # BloomBuddy service
│   │               ├── service.py        # Main API service
│   │               ├── models.py         # Data models
│   │               ├── data_retrieval.py # Sentinel data fetching
│   │               ├── preprocessing.py   # Data preprocessing
│   │               ├── inference.py      # ML model inference
│   │               └── vectorization.py  # GeoJSON conversion
│   └── requirements.txt    # Python dependencies
│
└── GIS/                   # GIS processing scripts and utilities
```

## Component Interactions

### 1. Frontend (Map Interface)

The frontend provides an interactive map interface where users can:

- Draw rectangles to select Areas of Interest (AOI)
- View the selected area with visual feedback
- Copy coordinates to clipboard
- Navigate to water quality analysis with selected coordinates

Key Components:
- `MapSelector.tsx`: Main map component with drawing capabilities
  - Uses MapLibre GL JS for map rendering
  - Implements custom drawing controls
  - Handles coordinate transformations
  - Provides real-time visual feedback
  - Manages state for drawing mode and selection

- `mapDrawingHelper.ts`: Utilities for coordinate processing and GeoJSON conversion
  - Handles bounding box calculations
  - Converts between coordinate formats
  - Manages map interaction modes
  - Provides GeoJSON conversion utilities

### 2. Backend (BloomBuddy Service)

The backend service processes requests and coordinates with Sentinel Hub:

#### API Endpoints:
- POST `/bloombuddy`: Main endpoint for water quality analysis
  - Input: 
    ```typescript
    {
      aoi: number[][][] // GeoJSON polygon coordinates
      date?: string     // Optional date in YYYY-MM-DD format
    }
    ```
  - Output:
    ```typescript
    {
      geojson: {
        type: "FeatureCollection"
        features: Array<{
          type: "Feature"
          geometry: {
            type: "Polygon"
            coordinates: number[][][]
          }
          properties: {
            area_ha: number
            severity_mean?: number
          }
        }>
      }
      summary: {
        bloom_km2: number
        severity_mean?: number
      }
    }
    ```

#### Processing Pipeline:
1. **Data Retrieval** (`data_retrieval.py`)
   - Authenticates with Sentinel Hub using OAuth2.0
   - Fetches relevant satellite bands (B02, B03, B04, B08)
   - Handles cloud masking using Scene Classification Layer (SCL)
   - Manages API rate limits and retries
   - Implements caching for frequently accessed areas

2. **Preprocessing** (`preprocessing.py`)
   - Normalizes band data to [0,1] range
   - Applies 3x3 median filter for noise reduction
   - Computes water quality indices:
     - Normalized Difference Water Index (NDWI)
     - Normalized Difference Vegetation Index (NDVI)
     - Modified Chlorophyll Absorption Ratio Index (MCARI)
   - Handles missing data and artifacts

3. **Inference** (`inference.py`)
   - Supports multiple ML models:
     - CyFi: Estimates cell density (cells/mL)
     - Se2WaQ: Binary bloom detection
   - Generates density maps
   - Computes severity levels (0-3)
   - Handles model versioning and loading

4. **Vectorization** (`vectorization.py`)
   - Converts raster predictions to vector format
   - Implements polygon simplification
   - Calculates area statistics
   - Filters small polygons (< 0.05 ha)
   - Merges adjacent features
   - Computes zonal statistics for severity

### 3. GIS Processing

The GIS module contains specialized scripts for:
- Coordinate system transformations
  - Supports EPSG:4326 (WGS84) and local projections
  - Handles coordinate precision and validation
- Spatial analysis
  - Area calculations
  - Polygon operations
  - Spatial indexing
- Data validation and filtering
  - Geometry checks
  - Topology validation
  - Area threshold filtering

## Data Flow

1. User selects AOI on the map interface
   - Draws rectangle using custom controls
   - Real-time coordinate updates
   - Visual feedback with semi-transparent overlay

2. Frontend converts selection to GeoJSON format
   - Validates coordinate bounds
   - Ensures proper winding order
   - Handles coordinate precision

3. Request sent to backend with coordinates and parameters
   - Includes optional date selection
   - Supports additional analysis parameters
   - Handles request validation

4. Backend retrieves Sentinel data
   - Authenticates with Sentinel Hub
   - Downloads required bands
   - Applies cloud masking
   - Handles error cases

5. Data processed through ML pipeline
   - Preprocessing and normalization
   - Model inference
   - Quality checks

6. Results vectorized and returned to frontend
   - GeoJSON feature generation
   - Property calculation
   - Summary statistics

7. Frontend displays analysis results on map
   - Color-coded polygons
   - Interactive popups
   - Summary statistics display
   - Export capabilities

## Error Handling

### Frontend
- Network error handling
- Invalid geometry validation
- Loading states and feedback
- User input validation

### Backend
- Request validation
- Sentinel Hub API errors
- Model inference errors
- Resource limits
- Timeout handling

## Performance Optimizations

### Frontend
- Debounced coordinate updates
- Efficient GeoJSON processing
- Map layer management
- Caching of recent results

### Backend
- Request caching
- Parallel processing
- Resource pooling
- Memory management
- Response compression

## Security

- API authentication
- Rate limiting
- Input validation
- Secure credential storage
- Error message sanitization

## Monitoring

- API endpoint metrics
- Processing pipeline timing
- Error rate tracking
- Resource utilization
- Model performance metrics

## Configuration

Key configuration files:
- Frontend: `config.ts` (map settings, API endpoints)
- Backend: `.env` (Sentinel Hub credentials)
- GIS: Configuration files for specific processing tasks

## Dependencies

### Frontend
- React/Next.js
- MapLibre GL JS
- TypeScript

### Backend
- FastAPI
- Sentinel Hub SDK
- NumPy/SciPy
- TensorFlow
- Rasterio/Shapely

## Development Setup

1. Frontend:
```bash
cd frontend
npm install
npm run dev
```

2. Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn bloombuddy.service:app --reload
```

## Notes

- The system is designed to handle areas up to 200 km²
- Processing time is typically under 5 seconds
- Cloud-masked areas are automatically filtered
- Results include both vector data (GeoJSON) and summary statistics

## Frontend Details

### Map Configuration
```typescript
// Map style options
- OpenStreetMap: "https://cdn.jsdelivr.net/gh/openlayers/ol-mapbox-style@main/styles/open-zoomstack-outdoor.json"
- Maptiler OSM: "https://api.maptiler.com/maps/openstreetmap/style.json"
- Basic: "https://demotiles.maplibre.org/style.json"

// API configuration
API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:28081/api'
```

### MapLibre Integration
- Custom type definitions for MapLibre GL JS
- Comprehensive map control options:
  - Zoom controls
  - Bearing controls
  - Pitch controls
  - Interactive features
  - Custom attribution
  - Performance optimizations
- Advanced map manipulation methods:
  - Coordinate projection
  - Layer management
  - Camera controls
  - Event handling
  - Style management

## Testing Infrastructure

### Test Configuration
Test configurations are stored in JSON format:
```json
{
  "bboxCoords": [-122.52, 37.70, -122.15, 37.90],
  "timeInterval": ["2023-06-01", "2023-06-30"]
}
```

### Test Data Organization
```
GIS/water_quality/
├── test_config.json     # Test configuration
├── test_data.json      # Test input data
├── test_output.png     # Test result visualization
└── test_output_rgb.png # RGB composite output
```

### Testing Scenarios
1. Coordinate System Tests
   - Boundary conditions
   - Coordinate transformations
   - Edge cases

2. Water Quality Analysis Tests
   - Data retrieval
   - Processing pipeline
   - Output validation

3. Visualization Tests
   - RGB composites
   - Output rendering
   - Visual quality checks

## Environment Configuration

### Frontend Environment Variables
```env
NEXT_PUBLIC_API_URL=http://localhost:28081/api
NEXT_PUBLIC_MAPLIBRE_KEY=your_key_here
```

### Backend Environment Variables
```env
SENTINEL_CLIENT_ID=your_client_id
SENTINEL_CLIENT_SECRET=your_client_secret
MODEL_PATH=/path/to/models
```

### Development Tools
- TypeScript for type safety
- ESLint for code quality
- Prettier for code formatting
- Jest for unit testing
- Cypress for E2E testing

## Deployment

### Frontend Deployment
- Next.js static export
- CDN distribution
- Environment-specific configurations

### Backend Deployment
- FastAPI with Uvicorn
- Model serving optimization
- Cache management
- Load balancing

### Monitoring and Logging
- API endpoint metrics
- Processing pipeline timing
- Error tracking
- Resource utilization
- Model performance metrics 