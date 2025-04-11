# Frontend Development Guide - React.js

This directory contains the frontend application for the Lost City Explorer, built with React.js.

## Setup Instructions

### Prerequisites

- Node.js 18.x or later
- npm 9.x or later
- Docker (for containerized development)

### Project Setup

1. Initialize a new React application:

```bash
npx create-react-app .
```

2. Install additional dependencies:

```bash
# UI Libraries
npm install @mui/material @emotion/react @emotion/styled

# Mapping and Visualization
npm install leaflet react-leaflet three @react-three/fiber @react-three/drei

# State Management
npm install @reduxjs/toolkit react-redux

# Routing
npm install react-router-dom

# API Communication
npm install axios

# Form Handling
npm install react-hook-form
```

3. Create an nginx configuration file (`nginx.conf`) in the project root:

```nginx
server {
    listen 80;
    
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Project Structure

Organize your codebase as follows:

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── common/         # Shared components (buttons, inputs, etc.)
│   │   ├── layout/         # Layout components (header, sidebar, etc.)
│   │   ├── maps/           # Map-related components
│   │   └── visualizations/ # Data visualization components
│   ├── pages/              # Page components
│   ├── services/           # API services
│   ├── store/              # Redux store configuration
│   ├── hooks/              # Custom React hooks
│   ├── utils/              # Utility functions
│   ├── assets/             # Images, fonts, etc.
│   ├── styles/             # Global styles
│   ├── App.js              # Main application component
│   └── index.js            # Application entry point
├── package.json            # Dependencies and scripts
├── nginx.conf              # Nginx configuration for production
└── Dockerfile              # Docker configuration
```

### Key Implementation Tasks

1. Implement map visualization components:
   - Interactive map using Leaflet.js
   - Layer controls for different satellite imagery sources
   - Drawing tools for marking potential archaeological sites

2. Create 3D terrain visualization:
   - Three.js / WebGL rendering of terrain data
   - Controls for rotation, zoom, and perspective
   - Overlays for archaeological feature highlighting

3. Develop user interface for:
   - Authentication and user management
   - Search and filtering of satellite imagery
   - Annotation and collaboration tools
   - Results display and export

4. Implement integration with:
   - Backend REST APIs for data retrieval
   - ML/AI service for analysis results
   - GIS Tools service for spatial analysis

### Docker Development

The Dockerfile is already configured for a production build. To develop locally:

1. Build and run the container:

```bash
docker build -t lostcity-frontend .
docker run -p 3000:80 lostcity-frontend
```

2. Or use docker-compose from the project root:

```bash
cd ..
docker-compose up -d
```

This will start the frontend service at http://localhost:3000.

### Environment Configuration

Create `.env` files for different environments:

```
# .env.development
REACT_APP_API_URL=http://localhost:8080
REACT_APP_ML_API_URL=http://localhost:5000
REACT_APP_GIS_API_URL=http://localhost:3001

# .env.production
REACT_APP_API_URL=/api
REACT_APP_ML_API_URL=/ml-api
REACT_APP_GIS_API_URL=/gis-api
```

### Testing

Set up tests for your components:

```bash
npm test
```

Include component tests with React Testing Library and integration tests for critical user flows.

## Integration Points

The frontend will need to interact with:
- The backend service for authentication and data management
- The ML/AI service for image analysis results
- The GIS Tools service for spatial analysis tools

## Additional Resources

- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [Leaflet.js Documentation](https://leafletjs.com/reference.html)
- [Three.js Documentation](https://threejs.org/docs/) 