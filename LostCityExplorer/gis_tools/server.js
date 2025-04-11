const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Routes
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'gis_tools' });
});

app.get('/api/gis/capabilities', (req, res) => {
  res.json({
    message: 'GIS tools service is running',
    capabilities: [
      'terrain_analysis',
      'elevation_profiling',
      'water_proximity_analysis',
      'viewshed_analysis'
    ]
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`GIS Tools service running on port ${PORT}`);
}); 