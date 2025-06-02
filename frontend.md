# WaterWatch Frontend Documentation

## Overview

The WaterWatch frontend is a modern **Next.js 15.3.1** application built with **React 19** that provides an interactive web interface for water quality monitoring and algal bloom detection using satellite imagery. The application integrates with a Jakarta EE backend and provides real-time analysis capabilities through multiple data sources and machine learning models.

## Technology Stack

### Core Framework
- **Next.js 15.3.1** - React framework with App Router
- **React 19** - Latest React with concurrent features
- **TypeScript 5.3.3** - Type-safe development

### UI & Styling
- **Material-UI (MUI) 7.1.0** - Component library with emotion styling
- **Tailwind CSS 3.4.17** - Utility-first CSS framework
- **Styled Components 6.1.18** - CSS-in-JS styling
- **React Hot Toast 2.4.1** - Toast notifications

### Mapping & Geospatial
- **MapLibre GL 4.7.1** - Open-source mapping library
- **React Map GL 7.1.7** - React wrapper for MapLibre
- **Leaflet 1.9.4** - Alternative mapping library
- **React Leaflet 5.0.0** - React components for Leaflet

### Date & Time
- **MUI X Date Pickers Pro 8.3.1** - Advanced date/time selection
- **date-fns 4.1.0** - Date utility library

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── cyfi-analysis/      # CyFi ML analysis page
│   │   ├── dashboard/          # User dashboard
│   │   ├── documentation/      # API documentation
│   │   ├── login/             # Authentication pages
│   │   ├── map-selector/      # Interactive map selection
│   │   ├── register/          # User registration
│   │   ├── water-quality/     # Main analysis interface
│   │   ├── api/               # API route handlers
│   │   ├── layout.tsx         # Root layout component
│   │   ├── page.tsx           # Landing page
│   │   └── globals.css        # Global styles
│   ├── components/            # Reusable UI components
│   │   ├── MapComponent.tsx   # Basic map component
│   │   ├── MapSelector.tsx    # Interactive map with drawing
│   │   ├── Navbar.tsx         # Navigation component
│   │   └── Providers.tsx      # Context providers
│   ├── features/              # Feature-based modules
│   │   └── cyfi/              # CyFi integration module
│   │       ├── api/           # CyFi API clients
│   │       ├── components/    # CyFi-specific components
│   │       └── types/         # CyFi type definitions
│   ├── services/              # Business logic services
│   │   └── authService.ts     # Authentication service
│   ├── utils/                 # Utility functions
│   │   ├── apiClient.ts       # HTTP client with auth
│   │   ├── config.ts          # App configuration
│   │   └── mapDrawingHelper.ts # Map interaction utilities
│   ├── types/                 # TypeScript type definitions
│   └── styles/                # Additional stylesheets
├── public/                    # Static assets
│   ├── results/               # Analysis result images
│   ├── css/                   # External CSS files
│   └── *.png, *.svg          # Images and icons
├── package.json               # Dependencies and scripts
├── next.config.js            # Next.js configuration
├── tailwind.config.js        # Tailwind CSS configuration
└── tsconfig.json             # TypeScript configuration
```

## Core Features

### 1. **Interactive Map Selection**
- **MapLibre GL** integration with free OpenStreetMap tiles
- **Bounding box drawing** for area selection
- **Coordinate validation** and real-time feedback
- **Multiple map styles** support
- **Responsive design** for mobile and desktop

### 2. **Water Quality Analysis**
- **Multi-satellite data sources**:
  - Sentinel-2 (L1C and L2A)
  - Landsat 8/9 and legacy missions
  - MODIS and HLS datasets
- **NDWI (Normalized Difference Water Index)** analysis
- **Machine Learning** water quality assessment
- **Sen2Coral** integration for coral reef analysis
- **Real-time processing** with progress indicators

### 3. **CyFi Integration**
- **Cyanobacteria detection** using ML models
- **Batch processing** capabilities
- **Real-time predictions** for single locations
- **Risk level classification** (Low, Moderate, High, Very High)
- **Confidence scoring** for predictions

### 4. **User Authentication**
- **JWT-based authentication** with Jakarta EE backend
- **Protected routes** with automatic redirects
- **Session management** with localStorage
- **Cross-tab synchronization** for logout events
- **Mock authentication** for development

### 5. **Data Visualization**
- **Interactive charts** and metrics
- **Satellite imagery display** with multiple bands
- **Color-coded analysis results**
- **Downloadable reports** and images
- **Responsive image galleries**

## Key Components

### Navigation (`Navbar.tsx`)
```typescript
// Features:
- Dynamic authentication state
- Responsive mobile menu
- Active route highlighting
- Logout functionality
- Cross-tab session sync
```

### Map Selector (`MapSelector.tsx`)
```typescript
// Capabilities:
- Bounding box drawing
- Coordinate input/output
- Map style switching
- Touch/mouse interaction
- Validation feedback
```

### API Client (`apiClient.ts`)
```typescript
// Features:
- Automatic JWT token handling
- CORS configuration
- Error handling and parsing
- Type-safe request methods
- Request/response interceptors
```

### Authentication Service (`authService.ts`)
```typescript
// Functionality:
- Login/registration flows
- JWT token management
- User session handling
- Mock authentication mode
- Token parsing and validation
```

## API Integration

### Backend Communication
- **Base URL**: `http://localhost:28080/auth-backend/api`
- **Authentication**: Bearer JWT tokens
- **CORS Mode**: Credentials included
- **Error Handling**: Structured error responses
- **Request Types**: JSON with automatic serialization

### Water Quality API
```typescript
POST /api/water-quality
{
  bboxCoords: [west, south, east, north],
  timeInterval: [startDate, endDate],
  dataSource: string
}
```

### CyFi Analysis API
```typescript
POST /api/cyfi/predict
{
  latitude: number,
  longitude: number,
  date: string
}
```

## Configuration

### Environment Variables
```bash
# Map configuration
MAP_STYLE=https://demotiles.maplibre.org/style.json

# API endpoints
NEXT_PUBLIC_API_URL=http://localhost:28080
NEXT_PUBLIC_BACKEND_URL=http://localhost:28081

# Feature flags
NEXT_PUBLIC_ENABLE_MOCK_AUTH=false
NEXT_PUBLIC_ENABLE_DEBUG=false
```

### Next.js Configuration
```javascript
// next.config.js
{
  reactStrictMode: true,
  transpilePackages: ['maplibre-gl', 'react-map-gl'],
  images: { remotePatterns: [{ protocol: 'https', hostname: '**' }] },
  experimental: {
    optimizePackageImports: ['maplibre-gl', 'react-map-gl']
  }
}
```

## Development Workflow

### Getting Started
```bash
# Install dependencies
npm install

# Copy MapLibre CSS
npm run copy-maplibre-css

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Development Features
- **Hot Module Replacement** for instant updates
- **TypeScript checking** in real-time
- **ESLint integration** for code quality
- **Automatic CSS optimization** with Tailwind
- **Image optimization** with Next.js Image component

## Styling Architecture

### Design System
- **Material-UI components** for consistent UI
- **Tailwind utilities** for custom styling
- **CSS-in-JS** with styled-components
- **Dark mode support** (planned)
- **Responsive breakpoints** for all devices

### Color Palette
```css
/* Primary Colors */
--blue-50: #eff6ff;
--blue-600: #2563eb;
--blue-800: #1e40af;
--blue-900: #1e3a8a;

/* Status Colors */
--green-600: #059669;  /* Success */
--red-600: #dc2626;    /* Error */
--yellow-600: #d97706; /* Warning */
```

## Performance Optimizations

### Code Splitting
- **Automatic route-based splitting** with Next.js
- **Dynamic imports** for heavy components
- **Lazy loading** for map components
- **Bundle analysis** with webpack-bundle-analyzer

### Image Optimization
- **Next.js Image component** with automatic optimization
- **WebP conversion** for modern browsers
- **Responsive images** with multiple sizes
- **Lazy loading** with intersection observer

### Caching Strategy
- **Static asset caching** with long-term headers
- **API response caching** with SWR patterns
- **Browser caching** for map tiles
- **Service worker** for offline capabilities (planned)

## Security Features

### Authentication Security
- **JWT token validation** on every request
- **Automatic token refresh** (planned)
- **Secure token storage** considerations
- **CSRF protection** with SameSite cookies
- **XSS prevention** with Content Security Policy

### API Security
- **CORS configuration** for cross-origin requests
- **Request validation** with TypeScript
- **Error message sanitization**
- **Rate limiting** (backend-handled)

## Testing Strategy

### Unit Testing (Planned)
- **Jest** for JavaScript testing
- **React Testing Library** for component testing
- **MSW** for API mocking
- **Coverage reporting** with Istanbul

### Integration Testing (Planned)
- **Cypress** for end-to-end testing
- **API integration tests**
- **Map interaction testing**
- **Authentication flow testing**

## Deployment

### Build Process
```bash
# Production build
npm run build

# Static export (if needed)
npm run export

# Docker deployment
docker build -t waterwatch-frontend .
docker run -p 3000:3000 waterwatch-frontend
```

### Deployment Targets
- **Vercel** (recommended for Next.js)
- **Netlify** for static deployment
- **Docker containers** for self-hosting
- **AWS S3 + CloudFront** for static hosting

## Browser Support

### Supported Browsers
- **Chrome 90+**
- **Firefox 88+**
- **Safari 14+**
- **Edge 90+**

### Progressive Enhancement
- **Core functionality** works without JavaScript
- **Enhanced features** with modern browser APIs
- **Graceful degradation** for older browsers
- **Mobile-first responsive design**

## Future Enhancements

### Planned Features
- **Real-time data streaming** with WebSockets
- **Offline capabilities** with service workers
- **Advanced data visualization** with D3.js
- **Export functionality** for analysis results
- **User preferences** and saved locations
- **Collaborative features** for team analysis

### Technical Improvements
- **Performance monitoring** with Web Vitals
- **Error tracking** with Sentry
- **Analytics integration** with Google Analytics
- **A/B testing** framework
- **Internationalization** (i18n) support

## Troubleshooting

### Common Issues

#### Map Not Loading
```bash
# Check MapLibre CSS is copied
npm run copy-maplibre-css

# Verify network connectivity
# Check browser console for errors
```

#### Authentication Errors
```bash
# Clear localStorage
localStorage.clear()

# Check backend connectivity
curl http://localhost:28080/auth-backend/api/health
```

#### Build Failures
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Debug Mode
```javascript
// Enable debug logging
localStorage.setItem('debug', 'waterwatch:*')

// Check API responses
console.log('API Response:', response)
```

## Contributing

### Code Standards
- **TypeScript** for all new code
- **ESLint** configuration compliance
- **Prettier** for code formatting
- **Conventional commits** for git messages

### Component Guidelines
- **Functional components** with hooks
- **TypeScript interfaces** for props
- **Error boundaries** for error handling
- **Accessibility** considerations (WCAG 2.1)

---

*This documentation covers the complete frontend architecture of the WaterWatch application. For backend integration details, see `backend.md`.* 