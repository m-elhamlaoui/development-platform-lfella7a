# GIS Tools Development Guide - Node.js & CesiumJS

This directory contains the GIS (Geographic Information System) tools for the Lost City Explorer application, built with Node.js and CesiumJS.

## Setup Instructions

### Prerequisites

- Node.js 18.x or later
- npm 9.x or later
- Docker (for containerized development)
- Basic knowledge of geospatial data formats and operations

### Project Setup

1. The directory already contains:
   - `package.json`: Basic Node.js project configuration with dependencies
   - `server.js`: Express server with basic endpoints
   - `public/index.html`: Minimal CesiumJS implementation
   - `Dockerfile`: Configuration for containerized development

2. Install dependencies:

```bash
npm install
```

3. Run the development server:

```bash
npm run dev
```

### Project Structure

Organize your codebase as follows:

```
gis_tools/
├── public/                      # Static files served by Express
│   ├── index.html               # Main HTML file with CesiumJS
│   ├── js/                      # Client-side JavaScript
│   │   ├── terrain-analysis.js  # Terrain analysis tools
│   │   ├── water-proximity.js   # Water proximity analysis
│   │   ├── viewshed.js          # Viewshed analysis tools
│   │   └── utils.js             # Utility functions
│   ├── css/                     # Stylesheets
│   └── assets/                  # Static assets (images, etc.)
├── server/                      # Server-side code
│   ├── routes/                  # API routes
│   │   ├── terrain.js           # Terrain analysis endpoints
│   │   ├── proximity.js         # Proximity analysis endpoints
│   │   └── viewshed.js          # Viewshed analysis endpoints
│   ├── services/                # Business logic
│   │   ├── gis-processing.js    # GIS processing functions
│   │   └── data-access.js       # Data access functions
│   ├── models/                  # Data models
│   └── utils/                   # Utility functions
├── data/                        # Sample data for development
├── server.js                    # Express server entry point
├── package.json                 # Node.js dependencies
└── Dockerfile                   # Docker configuration
```

### Key Implementation Tasks

1. Implement terrain analysis tools:
   - Slope and aspect calculation
   - Elevation profiling
   - Terrain visualization enhancements

2. Develop water proximity analysis:
   - Distance calculation to water sources
   - Water flow simulation
   - Watershed delineation

3. Create viewshed analysis tools:
   - Line-of-sight calculation
   - Visibility analysis from points of interest
   - Optimal viewpoint identification

4. Implement API endpoints for:
   - Processing geospatial data
   - Executing GIS operations
   - Retrieving analysis results

### CesiumJS Integration

The `public/index.html` file already contains a basic CesiumJS implementation. Extend it with custom tools:

1. Create terrain analysis tools:

```javascript
// public/js/terrain-analysis.js
function calculateSlope(viewer, position) {
    // Implementation for slope calculation
    const terrainProvider = viewer.terrainProvider;
    // ... calculation logic
    return slopeValue;
}

// Add UI control for terrain analysis
function addTerrainAnalysisUI(viewer) {
    // Create terrain analysis UI components
    const button = document.createElement('button');
    button.textContent = 'Analyze Terrain';
    button.onclick = () => {
        // Run terrain analysis
    };
    document.querySelector('.toolbar').appendChild(button);
}
```

2. Integrate with your HTML:

```html
<script src="js/terrain-analysis.js"></script>
<script>
    // Initialize terrain analysis tools
    document.addEventListener('DOMContentLoaded', () => {
        addTerrainAnalysisUI(viewer);
    });
</script>
```

### Docker Development

The Dockerfile is already configured. To build and run:

```bash
docker build -t lostcity-gis .
docker run -p 3001:3001 lostcity-gis
```

Or use docker-compose from the project root:

```bash
cd ..
docker-compose up -d gis_tools
```

This will start the GIS Tools service at http://localhost:3001.

### API Endpoints Implementation

Implement GIS analysis endpoints in Express:

```javascript
// server/routes/terrain.js
const express = require('express');
const router = express.Router();
const gisService = require('../services/gis-processing');

router.post('/analyze/elevation', (req, res) => {
    const { coordinates } = req.body;
    
    try {
        const elevationProfile = gisService.calculateElevationProfile(coordinates);
        res.json({
            success: true,
            elevationProfile
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

module.exports = router;
```

Register these routes in your `server.js`:

```javascript
const terrainRoutes = require('./server/routes/terrain');
app.use('/api/gis/terrain', terrainRoutes);
```

## Integration Points

The GIS Tools service will need to interact with:
- The backend service for data access and storage
- The ML/AI service for incorporating AI-detected features
- The frontend for visualizing GIS analysis results

## Additional Resources

- [CesiumJS Documentation](https://cesium.com/docs/)
- [Turf.js Documentation](https://turfjs.org/) (recommended for geospatial operations)
- [Express.js Documentation](https://expressjs.com/)
- [GDAL JavaScript Bindings](https://github.com/naturalatlas/node-gdal) (for advanced GIS operations) 