import React from 'react';
import type { BBox } from '@/utils/mapDrawingHelper';
import Map, { Source, Layer } from 'react-map-gl';
import type { FillLayer } from 'react-map-gl';

interface Props {
  geojson: {
    type: 'FeatureCollection';
    features: Array<{
      type: 'Feature';
      geometry: {
        type: 'Polygon';
        coordinates: number[][][];
      };
      properties: {
        analysisType: string;
        metrics: Record<string, number>;
        confidence: number;
      };
    }>;
  };
  bbox: BBox;
  layerStyle: {
    fillColor: string;
    fillOpacity: number;
    color: string;
  };
}

export default function MapComponent({ geojson, bbox, layerStyle }: Props) {
  const [viewport, setViewport] = React.useState({
    longitude: (bbox.east + bbox.west) / 2,
    latitude: (bbox.north + bbox.south) / 2,
    zoom: 10,
  });

  const layerConfig: FillLayer = {
    id: 'data',
    type: 'fill',
    paint: {
      'fill-color': layerStyle.fillColor,
      'fill-opacity': layerStyle.fillOpacity,
    },
  };

  const outlineLayer: FillLayer = {
    id: 'outline',
    type: 'line',
    paint: {
      'line-color': layerStyle.color,
      'line-width': 2,
    },
  };

  return (
    <Map
      {...viewport}
      onMove={evt => setViewport(evt.viewState)}
      style={{ width: '100%', height: '100%' }}
      mapStyle="mapbox://styles/mapbox/satellite-v9"
    >
      <Source type="geojson" data={geojson}>
        <Layer {...layerConfig} />
        <Layer {...outlineLayer} />
      </Source>
    </Map>
  );
} 