"""
Sen2Coral API - FastAPI application for coral reef analysis
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import uvicorn
import logging
from datetime import datetime

from models import Sen2CoralRequest, Sen2CoralResponse
from analysis_service import Sen2CoralAnalysisService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sen2Coral API",
    description="Advanced coral reef mapping and water quality assessment using Sen2Coral algorithms",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend development
        "http://localhost:3001",  # Alternative frontend port
        "https://localhost:3000", # HTTPS frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analysis service
analysis_service = Sen2CoralAnalysisService()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Sen2Coral API",
        "version": "1.0.0",
        "description": "Advanced coral reef mapping and water quality assessment",
        "endpoints": {
            "analyze": "/api/sen2coral/analyze",
            "capabilities": "/api/sen2coral/capabilities",
            "status": "/api/sen2coral/status/{job_id}",
            "docs": "/docs"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "sen2coral-api"
    }

@app.post("/api/sen2coral/analyze")
async def analyze_sen2coral(request: Sen2CoralRequest):
    """
    Perform Sen2Coral analysis on the specified area and time range
    
    Args:
        request: Sen2CoralRequest containing coordinates, time range, and analysis parameters
        
    Returns:
        Sen2CoralResponse with analysis results
    """
    try:
        logger.info(f"Starting Sen2Coral analysis for coordinates: {request.coordinates}")
        
        # Validate request
        if not request.coordinates:
            raise HTTPException(status_code=400, detail="Coordinates are required")
        
        if not request.timeRange:
            raise HTTPException(status_code=400, detail="Time range is required")
        
        # Perform analysis
        result = await analysis_service.analyze(request)
        
        logger.info("Sen2Coral analysis completed successfully")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/sen2coral/capabilities")
async def get_capabilities():
    """
    Get Sen2Coral system capabilities and supported features
    
    Returns:
        Dictionary containing system capabilities
    """
    return {
        "analysisTypes": [
            "water_quality",
            "habitat", 
            "bathymetry",
            "change_detection"
        ],
        "waterQualityIndices": [
            "ndwi",
            "clarity", 
            "turbidity",
            "chlorophyll",
            "dissolvedOrganics"
        ],
        "habitatClasses": [
            "coral",
            "seagrass", 
            "sand",
            "rock",
            "deep_water"
        ],
        "maxArea": 100.0,  # km²
        "supportedSatellites": [
            "sentinel2",
            "landsat8"
        ],
        "processingLimits": {
            "maxCloudCover": 30,      # percentage
            "maxTimeRange": 365,      # days
            "maxResolution": 10,      # meters
            "minResolution": 60       # meters
        },
        "algorithms": {
            "sambuca": {
                "version": "2.1.0",
                "description": "Semi-analytical model for bathymetry, un-mixing, and concentration assessment"
            },
            "habitat_mapping": {
                "version": "1.5.0", 
                "description": "Machine learning-based coral reef habitat classification"
            },
            "water_quality": {
                "version": "1.8.0",
                "description": "Advanced water quality parameter estimation"
            }
        }
    }

@app.get("/api/sen2coral/status/{job_id}")
async def get_analysis_status(job_id: str):
    """
    Get the status of a Sen2Coral analysis job
    
    Args:
        job_id: Unique identifier for the analysis job
        
    Returns:
        Job status information
    """
    try:
        status = await analysis_service.get_job_status(job_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check job status")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return HTTPException(
        status_code=500,
        detail="Internal server error occurred"
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 