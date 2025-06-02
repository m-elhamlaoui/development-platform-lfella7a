# Lost City - Map Selector Frontend

A Next.js 15.3.1 application with React 19 and MapLibre GL for water quality analysis.

## Getting Started

### Prerequisites

- Node.js 18.17 or later

### Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Install dependencies:
   ```bash
   npm install
   ```

### Map Configuration

This application uses MapLibre GL JS with free OpenStreetMap tiles. No API key or authentication is required.

If you want to use a different map style, you can modify the `MAP_STYLE` constant in the `src/utils/config.ts` file. Some options include:

- OpenStreetMap: `https://cdn.jsdelivr.net/gh/openlayers/ol-mapbox-style@main/styles/open-zoomstack-outdoor.json`
- Maptiler OSM: `https://api.maptiler.com/maps/openstreetmap/style.json`
- Basic Style: `https://demotiles.maplibre.org/style.json`

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Features

- Interactive map with bounding box selection
- Water quality analysis based on selected regions
- Integration with geospatial data

## Built With

- Next.js 15.3.1
- React 19
- MapLibre GL JS / react-map-gl
- Tailwind CSS

## Project Overview

This is the frontend application for the Lost City project, which connects to a Jakarta EE backend. It provides:

- User authentication (login/signup)
- Protected routes with JWT authentication
- User dashboard interface
- Dark mode support with Tailwind CSS

## Backend Integration

The frontend connects to a Jakarta EE backend running on WildFly (http://localhost:28081). All API requests are managed through the API client (`/src/utils/apiClient.ts`), which handles:

- Authentication headers
- CORS configuration
- Error handling
- Response parsing

### CORS Configuration

The frontend uses credentials mode for cross-origin requests:

```typescript
// API client configuration with CORS settings
const requestOptions: RequestInit = {
  ...options,
  headers,
  mode: 'cors',
  credentials: 'include',
};
```

This requires the backend to be configured with specific CORS headers that allow the frontend origin (http://localhost:3000) rather than using wildcard (*) origins.

### JWT Authentication

User authentication is managed through JSON Web Tokens (JWT). The `authService.ts` handles:

- Login/registration requests
- Token storage in localStorage
- User data extraction from JWT claims
- Session management

After login, the JWT token contains claims with the user's ID, username, and email, which are displayed in the dashboard.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
