/**
 * Map Drawing Helper
 * Provides utility functions for drawing operations on a map
 */

import { MapLayerMouseEvent, MapRef } from 'react-map-gl/maplibre';

export interface BBox {
  west: number;
  south: number;
  east: number;
  north: number;
}

/**
 * Initializes a drawing mode for the map
 * This disables the map's default drag behavior to allow drawing
 */
export function initializeDrawingMode(mapRef: MapRef | null): void {
  if (!mapRef) return;
  
  // Store the map's canvas element
  const canvas = mapRef.getCanvas();
  
  // Disable default touch behavior
  if (canvas) {
    canvas.style.touchAction = 'none';
  }
}

/**
 * Disables drawing mode and restores normal map behavior
 */
export function disableDrawingMode(mapRef: MapRef | null): void {
  if (!mapRef) return;
  
  // Restore the map's canvas element's default behavior
  const canvas = mapRef.getCanvas();
  
  if (canvas) {
    canvas.style.touchAction = 'auto';
  }
}

/**
 * Calculates a bounding box from two points
 */
export function calculateBoundingBox(
  startPoint: [number, number],
  endPoint: [number, number]
): BBox {
  return {
    west: Math.min(startPoint[0], endPoint[0]),
    south: Math.min(startPoint[1], endPoint[1]),
    east: Math.max(startPoint[0], endPoint[0]),
    north: Math.max(startPoint[1], endPoint[1]),
  };
}

/**
 * Converts a bounding box to a GeoJSON polygon
 */
export function bboxToGeoJSON(bbox: BBox): GeoJSON.Feature {
  return {
    type: 'Feature',
    properties: {},
    geometry: {
      type: 'Polygon',
      coordinates: [
        [
          [bbox.west, bbox.south],
          [bbox.east, bbox.south],
          [bbox.east, bbox.north],
          [bbox.west, bbox.north],
          [bbox.west, bbox.south],
        ],
      ],
    },
  };
}

/**
 * Formats coordinates to a readable string
 */
export function formatCoordinates(bbox: BBox, decimals: number = 6): string {
  return `[${bbox.west.toFixed(decimals)}, ${bbox.south.toFixed(decimals)}, ${bbox.east.toFixed(decimals)}, ${bbox.north.toFixed(decimals)}]`;
} 