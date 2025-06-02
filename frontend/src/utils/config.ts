// Application configuration

// Map configuration
export const MAP_STYLE = "https://demotiles.maplibre.org/style.json";

// Alternative map styles:
// - OpenStreetMap: "https://cdn.jsdelivr.net/gh/openlayers/ol-mapbox-style@main/styles/open-zoomstack-outdoor.json"
// - Maptiler OSM: "https://api.maptiler.com/maps/openstreetmap/style.json"
// - Basic: "https://demotiles.maplibre.org/style.json"

// API endpoint configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:28081/api'; 