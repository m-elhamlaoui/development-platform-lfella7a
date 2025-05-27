'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function Documentation() {
  const [activeSection, setActiveSection] = useState('overview');

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">WaterWatch Documentation</h1>
          <p className="text-xl text-gray-600">
            A comprehensive guide to using our water quality monitoring platform
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <nav className="space-y-1 sticky top-4">
              {[
                { id: 'overview', name: 'Overview' },
                { id: 'features', name: 'Features' },
                { id: 'how-it-works', name: 'How It Works' },
                { id: 'analysis', name: 'Analysis Pipeline' },
                { id: 'technical', name: 'Technical Stack' },
                { id: 'getting-started', name: 'Getting Started' }
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveSection(item.id)}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
                    activeSection === item.id
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  {item.name}
                </button>
              ))}
            </nav>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-12">
            {/* Overview Section */}
            <section id="overview" className={activeSection === 'overview' ? '' : 'hidden'}>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Project Overview</h2>
              <p className="text-gray-600 mb-6">
                WaterWatch is a satellite-driven platform for assessing water quality and detecting algal blooms using AI models 
                and Sentinel Hub satellite imagery.
              </p>
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Purpose</h3>
                <ul className="list-disc list-inside space-y-2 text-gray-600">
                  <li>Select an area of interest (AOI) via an interactive map</li>
                  <li>Fetch satellite imagery from the Sentinel Hub API</li>
                  <li>Analyze water quality and detect algal blooms using multiple AI techniques</li>
                  <li>View results in a clean, tabbed interface</li>
                  <li>Access personalized dashboards with secure authentication</li>
                </ul>
              </div>
            </section>

            {/* Features Section */}
            <section id="features" className={activeSection === 'features' ? '' : 'hidden'}>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Platform Features</h2>
              <div className="bg-white shadow rounded-lg p-6">
                <ul className="space-y-4">
                  <li className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="h-6 w-6 text-blue-600">•</div>
                    </div>
                    <div>
                      <h4 className="font-semibold">Jakarta EE Backend</h4>
                      <p className="text-gray-600">Robust backend for user authentication and data processing</p>
                    </div>
                  </li>
                  <li className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="h-6 w-6 text-blue-600">•</div>
                    </div>
                    <div>
                      <h4 className="font-semibold">Next.js Frontend</h4>
                      <p className="text-gray-600">TypeScript-based frontend with interactive mapping and multi-tab results display</p>
                    </div>
                  </li>
                  <li className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="h-6 w-6 text-blue-600">•</div>
                    </div>
                    <div>
                      <h4 className="font-semibold">Data Integration</h4>
                      <p className="text-gray-600">PostgreSQL integration and automated pipelines for data retrieval</p>
                    </div>
                  </li>
                </ul>
              </div>
            </section>

            {/* How It Works Section */}
            <section id="how-it-works" className={activeSection === 'how-it-works' ? '' : 'hidden'}>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">How It Works</h2>
              <div className="space-y-6">
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">1. AOI Selection</h3>
                  <p className="text-gray-600">
                    Users choose an area on a simple interactive map. The platform records the coordinates and passes them to a 
                    processing pipeline.
                  </p>
                </div>
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">2. Data Retrieval</h3>
                  <p className="text-gray-600">
                    Once an AOI is confirmed, the system calls the Sentinel Hub API to fetch satellite data (e.g., True Color 
                    imagery, NDWI index). The satellite data is then passed to various scripts for analysis.
                  </p>
                </div>
              </div>
            </section>

            {/* Analysis Pipeline Section */}
            <section id="analysis" className={activeSection === 'analysis' ? '' : 'hidden'}>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Analysis Pipeline</h2>
              <div className="space-y-6">
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">NDWI-based Detection</h3>
                  <ul className="list-disc list-inside space-y-2 text-gray-600">
                    <li>Enhances water visibility using the Normalized Difference Water Index</li>
                    <li>Detects irregularities indicative of algal bloom zones</li>
                  </ul>
                </div>
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">ML-Based Analysis</h3>
                  <ul className="list-disc list-inside space-y-2 text-gray-600">
                    <li>Uses machine learning models trained on algal bloom patterns</li>
                    <li>Provides a predictive layer using deep learning on spectral bands</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Technical Stack Section */}
            <section id="technical" className={activeSection === 'technical' ? '' : 'hidden'}>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Technical Stack</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Backend</h3>
                  <ul className="list-disc list-inside space-y-2 text-gray-600">
                    <li>RESTful API with JWT-based authentication</li>
                    <li>PostgreSQL for user data</li>
                    <li>Integration with Sentinel Hub API</li>
                    <li>Model pipelines for analysis</li>
                  </ul>
                </div>
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Frontend</h3>
                  <ul className="list-disc list-inside space-y-2 text-gray-600">
                    <li>Next.js with TypeScript</li>
                    <li>Interactive map for AOI selection</li>
                    <li>Multi-tab results view</li>
                    <li>Authentication and user dashboard</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Getting Started Section */}
            <section id="getting-started" className={activeSection === 'getting-started' ? '' : 'hidden'}>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Getting Started</h2>
              <div className="space-y-6">
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Prerequisites</h3>
                  <ul className="list-disc list-inside space-y-2 text-gray-600">
                    <li>Java 17+</li>
                    <li>Node.js 18+</li>
                    <li>PostgreSQL</li>
                    <li>Maven</li>
                    <li>WildFly 26+</li>
                  </ul>
                </div>
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Access Points</h3>
                  <ul className="list-disc list-inside space-y-2 text-gray-600">
                    <li>Frontend UI: <code className="bg-gray-100 px-2 py-1 rounded">http://localhost:3000</code></li>
                    <li>Backend API: <code className="bg-gray-100 px-2 py-1 rounded">http://localhost:28081/auth-backend</code></li>
                    <li>WildFly Admin: <code className="bg-gray-100 px-2 py-1 rounded">http://localhost:29990</code></li>
                  </ul>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
} 