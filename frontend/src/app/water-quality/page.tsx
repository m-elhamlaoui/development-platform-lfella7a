'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { toast } from 'react-hot-toast';
import ImageWithFallback from '@/components/ImageWithFallback';

interface AnalysisResults {
  ndwi_analysis: {
    waterCoverage: number;
    clearWater: number;
    moderateQuality: number;
    algalPresence: number;
  };
  ml_analysis?: {
    waterCoverage: number;
    clearWater: number;
    moderateQuality: number;
    algalPresence: number;
  };
  imageUrl: string;
  rgbImageUrl?: string;
  detailedNdwiUrl?: string;
  dataSource?: string;
  mlAnalysisAvailable: boolean;
  error?: string;
}

interface MetricCardProps {
  title: string;
  value: string;
  description: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, description }) => (
  <div className="bg-white rounded-lg shadow p-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
    <p className="text-3xl font-bold text-blue-600">{value || '0%'}</p>
    <p className="text-sm text-gray-500 mt-1">{description}</p>
  </div>
);

export default function WaterQualityAnalysisPage() {
  const searchParams = useSearchParams();
  
  const [coords, setCoords] = useState({
    west: -122.52,
    south: 37.70,
    east: -122.15,
    north: 37.90
  });
  const [timeRange, setTimeRange] = useState({
    start: '2025-06-01',
    end: '2025-06-30'
  });
  const [dataSource, setDataSource] = useState('sentinel2');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'parameters' | 'ndwi' | 'ml'>('parameters');
  const [activeImage, setActiveImage] = useState<'analysis' | 'rgb' | 'ndwi'>('analysis');

  // Handle URL parameters when the component mounts
  useEffect(() => {
    const west = searchParams?.get('west');
    const south = searchParams?.get('south');
    const east = searchParams?.get('east');
    const north = searchParams?.get('north');
    const source = searchParams?.get('source');
    
    if (west && south && east && north) {
      setCoords({
        west: parseFloat(west),
        south: parseFloat(south),
        east: parseFloat(east),
        north: parseFloat(north)
      });
    }
    
    if (source && [
      'sentinel2', 'sentinel2_l1c', 
      'landsat8', 'landsat8_l1', 'landsat7', 'landsat5',
      'hls', 'modis'
    ].includes(source)) {
      setDataSource(source);
    }
  }, [searchParams]);

  useEffect(() => {
    if (results) {
      setActiveTab('ndwi');
    }
  }, [results]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    if (name.includes('coords.')) {
      const coordKey = name.split('.')[1] as keyof typeof coords;
      setCoords(prev => ({ ...prev, [coordKey]: parseFloat(value) }));
    } else if (name.includes('timeRange.')) {
      const timeKey = name.split('.')[1] as keyof typeof timeRange;
      setTimeRange(prev => ({ ...prev, [timeKey]: value }));
    } else if (name === 'dataSource') {
      setDataSource(value);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      // Format coordinates as expected by the backend
      const bboxCoords = [coords.west, coords.south, coords.east, coords.north];
      
      const response = await fetch('/api/water-quality', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          bboxCoords,
          timeInterval: [timeRange.start, timeRange.end],
          dataSource
        }),
      });

      const data = await response.json();
      
      // Add detailed debug logging
      console.log('Water quality analysis response:', {
        fullData: data,
        ndwiAnalysis: data.ndwi_analysis,
        mlAnalysis: data.ml_analysis,
        mlAvailable: data.mlAnalysisAvailable,
        error: data.error
      });
      
      if (data.error) {
        // If we have an error but also an image, display both
        if (data.imageUrl) {
          console.log('Setting results with error:', data);
          setResults(data);
          setError(data.error);
        } else {
          // Otherwise just show the error
          setError(data.error);
        }
      } else {
        console.log('Setting results:', data);
        setResults(data);
        // Only switch to NDWI tab if we're on the parameters tab
        if (activeTab === 'parameters') {
          setActiveTab('ndwi');
        }
      }
      
      // Scroll to results
      if (data.imageUrl) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
      
    } catch (err) {
      setError(`Failed to analyze site: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Add debug effect for results state
  useEffect(() => {
    if (results) {
      console.log('Results state updated:', {
        hasResults: !!results,
        ndwiAnalysis: results.ndwi_analysis,
        waterCoverage: results.ndwi_analysis?.waterCoverage,
        activeTab,
      });
    }
  }, [results, activeTab]);

  // Add debug effect for ML tab state
  useEffect(() => {
    if (results) {
      console.log('Results updated:', {
        mlAnalysisAvailable: results.mlAnalysisAvailable,
        hasMLAnalysis: !!results.ml_analysis,
        activeTab
      });
    }
  }, [results, activeTab]);

  const formatDataSourceName = (source: string): string => {
    switch(source) {
      case 'sentinel2': return 'Sentinel-2 L2A';
      case 'sentinel2_l1c': return 'Sentinel-2 L1C';
      case 'landsat8': return 'Landsat 8/9 L2';
      case 'landsat8_l1': return 'Landsat 8/9 L1';
      case 'landsat7': return 'Landsat 7 ETM+';
      case 'landsat5': return 'Landsat 4-5 TM';
      case 'hls': return 'Harmonized Landsat Sentinel';
      case 'modis': return 'MODIS';
      default: return source;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header with themed background */}
      <div className="relative bg-gradient-to-r from-blue-700 to-blue-500 rounded-lg overflow-hidden mb-8">
        <div className="absolute inset-0 opacity-10">
          <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="1.5" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>
        <div className="relative z-10 px-6 py-12 text-white">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">Water Quality Analysis</h1>
          <p className="text-blue-100 max-w-2xl">
            Monitor water quality and detect algal blooms using satellite imagery. Select an area, time range, and data source to analyze water conditions.
          </p>
        </div>
      </div>
      
      {/* Tabs for Parameters and Results */}
      <div className="mb-6 border-b border-gray-200">
        <div className="flex space-x-6">
          <button
            onClick={() => setActiveTab('parameters')}
            className={`pb-3 px-1 text-lg font-medium transition-colors ${
              activeTab === 'parameters'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-blue-600'
            }`}
          >
            Analysis Parameters
          </button>
          <button
            onClick={() => setActiveTab('ndwi')}
            disabled={!results}
            className={`pb-3 px-1 text-lg font-medium transition-colors ${
              activeTab === 'ndwi'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : results 
                  ? 'text-gray-500 hover:text-blue-600' 
                  : 'text-gray-300 cursor-not-allowed'
            }`}
          >
            NDWI Analysis
          </button>
          <button
            onClick={() => {
              console.log('ML tab clicked', { results, mlAnalysisAvailable: results?.mlAnalysisAvailable });
              setActiveTab('ml');
            }}
            disabled={!results}
            className={`pb-3 px-1 text-lg font-medium transition-colors ${
              activeTab === 'ml'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : results 
                  ? 'text-gray-500 hover:text-blue-600' 
                  : 'text-gray-300 cursor-not-allowed'
            }`}
          >
            ML Analysis
          </button>
        </div>
      </div>
      
      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-red-700 font-medium">{error}</p>
              {results && results.imageUrl && (
                <p className="text-red-700 mt-1">See visualization below for more details.</p>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Analysis Parameters Tab */}
      {activeTab === 'parameters' && (
        <div className="card">
          <div className="mb-6">
            <Link 
              href="/map-selector" 
              className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors shadow-sm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M12 1.586l-4 4V17h8V5.586l-4-4zM2 17V8h8v9H2zm16 0V8h-6v9h6z" clipRule="evenodd" />
              </svg>
              Use Map Selector
            </Link>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-6">
              <div className="space-y-6">
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-md p-5">
                  <h3 className="text-lg font-medium text-blue-800 dark:text-blue-300 mb-3">Bounding Box Coordinates</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="label">West (Longitude)</label>
                      <input
                        type="number"
                        name="coords.west"
                        value={coords.west}
                        onChange={handleInputChange}
                        step="0.01"
                        className="input-field"
                        required
                      />
                    </div>
                    <div>
                      <label className="label">East (Longitude)</label>
                      <input
                        type="number"
                        name="coords.east"
                        value={coords.east}
                        onChange={handleInputChange}
                        step="0.01"
                        className="input-field"
                        required
                      />
                    </div>
                    <div>
                      <label className="label">South (Latitude)</label>
                      <input
                        type="number"
                        name="coords.south"
                        value={coords.south}
                        onChange={handleInputChange}
                        step="0.01"
                        className="input-field"
                        required
                      />
                    </div>
                    <div>
                      <label className="label">North (Latitude)</label>
                      <input
                        type="number"
                        name="coords.north"
                        value={coords.north}
                        onChange={handleInputChange}
                        step="0.01"
                        className="input-field"
                        required
                      />
                    </div>
                  </div>
                </div>
                
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-md p-5">
                  <h3 className="text-lg font-medium text-blue-800 dark:text-blue-300 mb-3">Time Range</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="label">Start Date</label>
                      <input
                        type="date"
                        name="timeRange.start"
                        value={timeRange.start}
                        onChange={handleInputChange}
                        className="input-field"
                        required
                      />
                    </div>
                    <div>
                      <label className="label">End Date</label>
                      <input
                        type="date"
                        name="timeRange.end"
                        value={timeRange.end}
                        onChange={handleInputChange}
                        className="input-field"
                        required
                      />
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    For best results, use a 1-2 month date range
                  </p>
                </div>
              </div>
              
              <div className="space-y-6">
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-md p-5">
                  <h3 className="text-lg font-medium text-blue-800 dark:text-blue-300 mb-3">Data Source</h3>
                  <div>
                    <select
                      name="dataSource"
                      value={dataSource}
                      onChange={handleInputChange}
                      className="select-field"
                      required
                    >
                      <option value="sentinel2">Sentinel-2 L2A (10m resolution, atmospherically corrected)</option>
                      <option value="sentinel2_l1c">Sentinel-2 L1C (10m resolution, non-corrected)</option>
                      <option value="landsat8">Landsat 8/9 L2 (30m resolution, atmospherically corrected)</option>
                      <option value="landsat8_l1">Landsat 8/9 L1 (30m resolution, non-corrected)</option>
                      <option value="landsat7">Landsat 7 ETM+ (30m resolution)</option>
                      <option value="landsat5">Landsat 4-5 TM (30m resolution)</option>
                      <option value="hls">Harmonized Landsat Sentinel (30m resolution)</option>
                      <option value="modis">MODIS (250m resolution)</option>
                    </select>
                    <p className="text-xs text-gray-500 mt-2">
                      Different satellites provide varying resolutions and spectral characteristics.
                    </p>
                  </div>
                </div>
                
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-md p-5">
                  <h3 className="text-lg font-medium text-blue-800 dark:text-blue-300 mb-3">Popular Locations</h3>
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => setCoords({
                        west: -122.52,
                        south: 37.70,
                        east: -122.15,
                        north: 37.90
                      })}
                      className="px-3 py-2 text-sm bg-white text-blue-700 rounded-md hover:bg-blue-50 border border-blue-200 shadow-sm transition-colors"
                    >
                      San Francisco Bay
                    </button>
                    <button
                      type="button"
                      onClick={() => setCoords({
                        west: -74.05,
                        south: 40.60,
                        east: -73.70,
                        north: 40.90
                      })}
                      className="px-3 py-2 text-sm bg-white text-blue-700 rounded-md hover:bg-blue-50 border border-blue-200 shadow-sm transition-colors"
                    >
                      New York Harbor
                    </button>
                    <button
                      type="button"
                      onClick={() => setCoords({
                        west: -118.50,
                        south: 33.70,
                        east: -118.10,
                        north: 34.10
                      })}
                      className="px-3 py-2 text-sm bg-white text-blue-700 rounded-md hover:bg-blue-50 border border-blue-200 shadow-sm transition-colors"
                    >
                      Los Angeles Harbor
                    </button>
                    <button
                      type="button"
                      onClick={() => setCoords({
                        west: -80.25,
                        south: 25.70,
                        east: -80.05,
                        north: 25.90
                      })}
                      className="px-3 py-2 text-sm bg-white text-blue-700 rounded-md hover:bg-blue-50 border border-blue-200 shadow-sm transition-colors"
                    >
                      Miami Harbor
                    </button>
                  </div>
                </div>
                
                <div className="flex justify-center mt-4">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 shadow-md transition-all"
                  >
                    {isLoading ? (
                      <span className="flex items-center justify-center">
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Analyzing...
                      </span>
                    ) : 'Analyze Water Quality'}
                  </button>
                </div>
              </div>
            </div>
          </form>
        </div>
      )}
      
      {/* Results Tab */}
      {activeTab === 'ndwi' && results && (
        <div className="space-y-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4">NDWI Analysis Results</h3>
            {/* Debug info */}
            <div className="text-xs text-gray-500 mb-4">
              Debug: {JSON.stringify(results.ndwi_analysis, null, 2)}
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricCard
                title="Water Coverage"
                value={`${results.ndwi_analysis?.waterCoverage ?? 0}%`}
                description="Total water surface detected"
              />
              <MetricCard
                title="Clear Water"
                value={`${results.ndwi_analysis?.clearWater ?? 0}%`}
                description="High clarity water bodies"
              />
              <MetricCard
                title="Moderate Quality"
                value={`${results.ndwi_analysis?.moderateQuality ?? 0}%`}
                description="Areas requiring attention"
              />
              <MetricCard
                title="Algal Presence"
                value={`${results.ndwi_analysis?.algalPresence ?? 0}%`}
                description="Potential algal growth"
              />
            </div>
          </div>

          {/* Visualization Tabs for NDWI */}
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                {[
                  { id: 'analysis' as const, name: 'NDWI Analysis', imageUrl: results.imageUrl },
                  { id: 'rgb' as const, name: 'True Color', imageUrl: results.rgbImageUrl },
                  { id: 'ndwi' as const, name: 'Detailed NDWI', imageUrl: results.detailedNdwiUrl }
                ].map(tab => tab.imageUrl && (
                  <button
                    key={tab.id}
                    onClick={() => setActiveImage(tab.id)}
                    className={`${
                      activeImage === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                  >
                    {tab.name}
                  </button>
                ))}
              </nav>
            </div>
            <div className="p-4">
              <img
                src={
                  activeImage === 'analysis'
                    ? results.imageUrl
                    : activeImage === 'rgb'
                    ? results.rgbImageUrl
                    : results.detailedNdwiUrl
                }
                alt={`${activeImage} visualization`}
                className="w-full h-auto rounded-lg"
              />
            </div>
          </div>
        </div>
      )}

      {/* ML Analysis Tab */}
      {activeTab === 'ml' && results && (
        <div className="space-y-8">
          {results.mlAnalysisAvailable && results.ml_analysis ? (
            <>
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">ML-Enhanced Analysis Results</h3>
                  <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">ML Enhanced</span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <MetricCard
                    title="Water Coverage"
                    value={`${results.ml_analysis?.waterCoverage || 0}%`}
                    description="ML-detected water surface"
                  />
                  <MetricCard
                    title="Clear Water"
                    value={`${results.ml_analysis?.clearWater || 0}%`}
                    description="High clarity water bodies"
                  />
                  <MetricCard
                    title="Moderate Quality"
                    value={`${results.ml_analysis?.moderateQuality || 0}%`}
                    description="Areas requiring attention"
                  />
                  <MetricCard
                    title="Algal Presence"
                    value={`${results.ml_analysis?.algalPresence || 0}%`}
                    description="Potential algal growth"
                  />
                </div>
              </div>

              {/* Visualization Tabs for ML */}
              <div className="bg-white rounded-lg shadow-lg overflow-hidden">
                <div className="border-b border-gray-200">
                  <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                    {[
                      { id: 'analysis' as const, name: 'ML Analysis', imageUrl: results.imageUrl },
                      { id: 'rgb' as const, name: 'True Color', imageUrl: results.rgbImageUrl },
                      { id: 'ndwi' as const, name: 'Detailed View', imageUrl: results.detailedNdwiUrl }
                    ].map(tab => tab.imageUrl && (
                      <button
                        key={tab.id}
                        onClick={() => setActiveImage(tab.id)}
                        className={`${
                          activeImage === tab.id
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                      >
                        {tab.name}
                      </button>
                    ))}
                  </nav>
                </div>
                <div className="p-4">
                  <img
                    src={
                      activeImage === 'analysis'
                        ? results.imageUrl
                        : activeImage === 'rgb'
                        ? results.rgbImageUrl
                        : results.detailedNdwiUrl
                    }
                    alt={`${activeImage} visualization`}
                    className="w-full h-auto rounded-lg"
                  />
                </div>
              </div>
            </>
          ) : (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-yellow-700">
                    ML Analysis is not available for this region. This could be due to:
                  </p>
                  <ul className="mt-2 text-sm text-yellow-700 list-disc list-inside">
                    <li>Insufficient data quality for ML processing</li>
                    <li>Region too large or too small for accurate ML analysis</li>
                    <li>Technical limitations with the selected data source</li>
                  </ul>
                  <p className="mt-2 text-sm text-yellow-700">
                    Try adjusting your area selection or using a different data source.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Update the tab navigation */}
      <div className="mb-8">
        <div className="sm:hidden">
          <select
            id="tabs"
            name="tabs"
            className="block w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500"
            value={activeTab}
            onChange={(e) => setActiveTab(e.target.value as 'parameters' | 'ndwi' | 'ml')}
          >
            <option value="parameters">Parameters</option>
            <option value="ndwi">NDWI Analysis</option>
            {results?.mlAnalysisAvailable && <option value="ml">ML Analysis</option>}
          </select>
        </div>
        <div className="hidden sm:block">
          <nav className="flex space-x-4" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('parameters')}
              className={`${
                activeTab === 'parameters'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-500 hover:text-gray-700'
              } px-3 py-2 font-medium text-sm rounded-md`}
            >
              Parameters
            </button>
            {results && (
              <button
                onClick={() => setActiveTab('ndwi')}
                className={`${
                  activeTab === 'ndwi'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700'
                } px-3 py-2 font-medium text-sm rounded-md`}
              >
                NDWI Analysis
              </button>
            )}
            {results?.mlAnalysisAvailable && (
              <button
                onClick={() => setActiveTab('ml')}
                className={`${
                  activeTab === 'ml'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700'
                } px-3 py-2 font-medium text-sm rounded-md`}
              >
                ML Analysis
              </button>
            )}
          </nav>
        </div>
      </div>
    </div>
  );
} 