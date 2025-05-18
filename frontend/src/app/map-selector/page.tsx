'use client';

import { useState } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';

// Import MapSelector with no SSR since MapBox GL requires browser environment
const MapSelector = dynamic(() => import('@/components/MapSelector'), {
  ssr: false,
});

interface BBox {
  west: number;
  south: number;
  east: number;
  north: number;
}

export default function MapSelectorPage() {
  const [selectedBBox, setSelectedBBox] = useState<BBox>({
    west: -122.52,
    south: 37.70,
    east: -122.15,
    north: 37.90
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Map Area Selector</h1>
      
      <MapSelector 
        onBBoxSelected={setSelectedBBox}
        initialBBox={selectedBBox}
      />
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">How to Use</h2>
        <ol className="list-decimal pl-6 space-y-2 mb-6">
          <li>Click the <strong>Draw Rectangle</strong> button to enter drawing mode.</li>
          <li>Click and drag on the map to draw a rectangle around your area of interest.</li>
          <li>Release the mouse button to complete your selection.</li>
          <li>The coordinates will be displayed below the map.</li>
          <li>Click <strong>Copy Coordinates</strong> to copy the bounding box values to your clipboard.</li>
          <li>Click <strong>Use for Water Quality Analysis</strong> to analyze the selected area.</li>
          <li>You can also manually adjust the coordinates using the input fields.</li>
        </ol>
        
        <div className="flex justify-center">
          <Link
            href="/"
            className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
          >
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
} 