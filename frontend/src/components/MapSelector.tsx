'use client';

import { useEffect, useState, useRef } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import Map, { Source, Layer, MapRef, MapLayerMouseEvent, NavigationControl } from 'react-map-gl/maplibre';
import { MAP_STYLE } from '@/utils/config';
import { 
  BBox, 
  initializeDrawingMode, 
  disableDrawingMode, 
  calculateBoundingBox, 
  bboxToGeoJSON,
  formatCoordinates 
} from '@/utils/mapDrawingHelper';
import './MapSelector.css';
import Link from 'next/link';

interface MapSelectorProps {
  onBBoxSelected?: (bbox: BBox) => void;
  initialBBox?: BBox;
}

export default function MapSelector({ onBBoxSelected, initialBBox }: MapSelectorProps) {
  const [bbox, setBbox] = useState<BBox>(initialBBox || {
    west: -122.52,
    south: 37.70,
    east: -122.15,
    north: 37.90
  });
  const [drawing, setDrawing] = useState(false);
  const [startPoint, setStartPoint] = useState<[number, number] | null>(null);
  const mapRef = useRef<MapRef | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Enable/disable drawing mode when the drawing state changes
  useEffect(() => {
    if (drawing) {
      initializeDrawingMode(mapRef.current);
    } else {
      disableDrawingMode(mapRef.current);
    }
    
    // Log the drawing state for debugging
    console.log('Drawing state:', drawing);
    console.log('Start point:', startPoint);
  }, [drawing, startPoint]);

  const copyBBoxToClipboard = () => {
    const bboxText = formatCoordinates(bbox);
    navigator.clipboard.writeText(bboxText).then(() => {
      toast.success('Coordinates copied to clipboard!');
    }).catch(err => {
      toast.error('Failed to copy coordinates');
      console.error('Failed to copy: ', err);
    });
  };

  const toggleDrawing = () => {
    if (drawing) {
      // If currently drawing, cancel it
      setDrawing(false);
      setStartPoint(null);
      setIsDragging(false);
    } else {
      // Start drawing mode
      setDrawing(true);
      toast.success('Drawing mode active. Click and drag to draw a rectangle.');
    }
  };

  const handleMouseDown = (e: MapLayerMouseEvent) => {
    if (!drawing) return;
    
    console.log('Mouse down at:', e.lngLat);
    
    // Set the starting point for drawing
    setStartPoint([e.lngLat.lng, e.lngLat.lat]);
    setIsDragging(true);
    
    // Prevent default map dragging behavior when in drawing mode
    e.preventDefault();
  };

  const handleMouseMove = (e: MapLayerMouseEvent) => {
    if (!drawing || !startPoint || !isDragging) return;
    
    console.log('Mouse move at:', e.lngLat);
    
    // Update the bbox in real-time as the user drags
    const currentBbox = calculateBoundingBox(
      startPoint,
      [e.lngLat.lng, e.lngLat.lat]
    );
    
    setBbox(currentBbox);
  };

  const handleMouseUp = (e: MapLayerMouseEvent) => {
    if (!drawing || !startPoint || !isDragging) return;
    
    console.log('Mouse up at:', e.lngLat);
    
    // Finalize the box
    const finalBbox = calculateBoundingBox(
      startPoint,
      [e.lngLat.lng, e.lngLat.lat]
    );
    
    setBbox(finalBbox);
    
    if (onBBoxSelected) {
      onBBoxSelected(finalBbox);
    }
    
    // Only reset dragging state but keep drawing mode active
    setIsDragging(false);
    setStartPoint(null);
    
    toast.success('Rectangle drawn successfully!');
  };

  // Convert the bbox to GeoJSON for the map
  const bboxGeoJSON = bboxToGeoJSON(bbox);

  // Layer styling for the bounding box
  const bboxLayerStyle = {
    id: 'bbox-layer',
    type: 'fill',
    paint: {
      'fill-color': '#0080ff',
      'fill-opacity': 0.2
    }
  };

  const bboxOutlineStyle = {
    id: 'bbox-outline',
    type: 'line',
    paint: {
      'line-color': '#0080ff',
      'line-width': 2
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <h2 className="text-xl font-semibold mb-4">Bounding Box Selector</h2>
      
      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-2">
          Draw a rectangle on the map to select an area for analysis, or enter coordinates manually.
        </p>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={toggleDrawing}
            className={`px-4 py-2 rounded-md ${
              drawing 
                ? 'bg-red-500 hover:bg-red-600 text-white' 
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            }`}
          >
            {drawing ? 'Cancel Drawing' : 'Draw Rectangle'}
          </button>
          <button
            type="button"
            onClick={copyBBoxToClipboard}
            className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-md"
          >
            Copy Coordinates
          </button>
          <Link
            href={{
              pathname: '/water-quality',
              query: {
                west: bbox.west,
                south: bbox.south,
                east: bbox.east,
                north: bbox.north
              }
            }}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-md"
          >
            Use for Water Quality Analysis
          </Link>
        </div>
      </div>
      
      <div className={`map-container mb-6 ${drawing ? 'drawing' : ''}`}>
        <Map
          ref={mapRef}
          initialViewState={{
            longitude: (bbox.east + bbox.west) / 2,
            latitude: (bbox.north + bbox.south) / 2,
            zoom: 10
          }}
          mapStyle={MAP_STYLE}
          style={{ width: '100%', height: '100%' }}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          dragRotate={!drawing}
          dragPan={!isDragging}
          cursor={drawing ? (isDragging ? 'crosshair' : 'crosshair') : 'grab'}
          interactiveLayerIds={drawing ? [] : undefined}
        >
          <NavigationControl position="top-right" />
          <Source id="bbox-source" type="geojson" data={bboxGeoJSON as any}>
            <Layer {...bboxLayerStyle as any} />
            <Layer {...bboxOutlineStyle as any} />
          </Source>
          
          {startPoint && isDragging && (
            <div className="absolute bg-blue-500 text-white text-xs px-2 py-1 rounded-md z-20" 
                 style={{ 
                   left: '50%', 
                   bottom: '10px',
                   transform: 'translateX(-50%)',
                 }}>
              Drawing: {(bbox.east - bbox.west).toFixed(4)} × {(bbox.north - bbox.south).toFixed(4)} degrees
            </div>
          )}
        </Map>
        {drawing && (
          <div className="drawing-instructions">
            Click and drag to draw a bounding box
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">West (Longitude)</label>
          <input
            type="number"
            value={bbox.west}
            onChange={(e) => setBbox({...bbox, west: parseFloat(e.target.value)})}
            step="0.000001"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">East (Longitude)</label>
          <input
            type="number"
            value={bbox.east}
            onChange={(e) => setBbox({...bbox, east: parseFloat(e.target.value)})}
            step="0.000001"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">South (Latitude)</label>
          <input
            type="number"
            value={bbox.south}
            onChange={(e) => setBbox({...bbox, south: parseFloat(e.target.value)})}
            step="0.000001"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">North (Latitude)</label>
          <input
            type="number"
            value={bbox.north}
            onChange={(e) => setBbox({...bbox, north: parseFloat(e.target.value)})}
            step="0.000001"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
      </div>
      
      <div className="mt-4">
        <p className="text-sm text-gray-600 mb-2">Coordinates in WGS84 format:</p>
        <pre className="bbox-display">
          {formatCoordinates(bbox)}
        </pre>
      </div>
      
      <Toaster position="bottom-center" />
    </div>
  );
} 