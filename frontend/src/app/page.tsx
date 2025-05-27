import React from 'react';
import { Box, Container, Typography, Button } from '@mui/material';
import Link from 'next/link';
import ImageWithFallback from "@/components/ImageWithFallback";

export default function Home() {
  return (
    <Container maxWidth="lg" sx={{ py: 8 }}>
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography variant="h2" component="h1" gutterBottom>
          Welcome to WaterWatch
        </Typography>
        <Typography variant="h5" component="h2" color="text.secondary" gutterBottom>
          Water Quality Monitoring and Algal Bloom Detection Platform
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
        <Link href="/water-quality" passHref>
          <Button variant="contained" color="primary" size="large">
            Water Quality Analysis
          </Button>
        </Link>
        <Link href="/map-selector" passHref>
          <Button variant="outlined" color="primary" size="large">
            Map Selector
          </Button>
        </Link>
      </Box>

      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 text-white">
        <div className="absolute inset-0 z-0 opacity-20">
          <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="0.5" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>
        
        <div className="container relative z-10 mx-auto px-4 py-20 md:py-32">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
                Water Quality <span className="text-blue-300">Monitoring</span>
              </h1>
              <p className="text-xl text-blue-100 mb-8 max-w-lg">
                Assess water quality and detect Algal Bloom using advanced satellite imagery and AI-powered analysis.
              </p>
            </div>
            <div className="relative hidden md:block h-80">
              <div className="absolute inset-0 rounded-lg overflow-hidden shadow-2xl">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-blue-800/20 backdrop-blur-sm"></div>
                <ImageWithFallback
                  src="/water_quality_assessment.png"
                  alt="Satellite view of water bodies"
                  fill
                  className="object-cover"
                  priority
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Features Section */}
      <div className="container mx-auto px-4 py-16">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
          Advanced Water Quality Monitoring Tools
        </h2>
        
        <div className="grid md:grid-cols-3 gap-8">
          <div className="card border border-gray-100 hover:shadow-lg transition-shadow">
            <div className="h-12 w-12 bg-blue-100 text-blue-700 rounded-lg flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Multi-Satellite Analysis</h3>
            <p className="text-gray-600 dark:text-gray-400">
              Access comprehensive water quality data from Sentinel-2, Landsat 8/9, and other high-resolution satellites.
            </p>
          </div>
          
          <div className="card border border-gray-100 hover:shadow-lg transition-shadow">
            <div className="h-12 w-12 bg-green-100 text-green-700 rounded-lg flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Pattern Recognition</h3>
            <p className="text-gray-600 dark:text-gray-400">
              Identify water quality issues and algal blooms with advanced pattern analysis and machine learning.
            </p>
          </div>
          
          <div className="card border border-gray-100 hover:shadow-lg transition-shadow">
            <div className="h-12 w-12 bg-purple-100 text-purple-700 rounded-lg flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Environmental Monitoring</h3>
            <p className="text-gray-600 dark:text-gray-400">
              Analyze water bodies, vegetation patterns, and environmental factors to understand water quality trends.
            </p>
          </div>
        </div>
      </div>
      
      {/* Call to Action */}
      <div className="bg-blue-50 dark:bg-blue-900/30 py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-blue-800 dark:text-blue-300 mb-4">Ready to Monitor?</h2>
          <p className="text-lg text-blue-600 dark:text-blue-400 max-w-2xl mx-auto mb-8">
            Start monitoring water quality and detecting algal blooms with our advanced satellite analysis tools
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link 
              href="/login" 
              className="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
            >
              Login
            </Link>
            <Link 
              href="/register" 
              className="px-6 py-3 border border-blue-600 text-blue-600 dark:text-blue-400 dark:border-blue-400 font-medium rounded-md hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors"
            >
              Register
            </Link>
          </div>
        </div>
      </div>
    </Container>
  );
}
