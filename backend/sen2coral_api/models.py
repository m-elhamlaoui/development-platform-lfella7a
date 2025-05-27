"""
Pydantic models for Sen2Coral API
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime

class DataSource(str, Enum):
    """Supported data sources for analysis"""
    sentinel2 = "sentinel2"
    sambuca = "sambuca"
    combined = "combined"

class AnalysisType(str, Enum):
    """Types of analysis supported by Sen2Coral"""
    water_quality = "water_quality"
    habitat = "habitat"
    bathymetry = "bathymetry"
    change_detection = "change_detection"

class BBox(BaseModel):
    """Bounding box coordinates"""
    west: float = Field(..., ge=-180, le=180, description="Western longitude")
    south: float = Field(..., ge=-90, le=90, description="Southern latitude")
    east: float = Field(..., ge=-180, le=180, description="Eastern longitude")
    north: float = Field(..., ge=-90, le=90, description="Northern latitude")
    
    @validator('east')
    def east_must_be_greater_than_west(cls, v, values):
        if 'west' in values and v <= values['west']:
            raise ValueError('East longitude must be greater than west longitude')
        return v
    
    @validator('north')
    def north_must_be_greater_than_south(cls, v, values):
        if 'south' in values and v <= values['south']:
            raise ValueError('North latitude must be greater than south latitude')
        return v

class TimeRange(BaseModel):
    """Time range for analysis"""
    startDate: str = Field(..., description="Start date in ISO format (YYYY-MM-DD)")
    endDate: str = Field(..., description="End date in ISO format (YYYY-MM-DD)")
    
    @validator('endDate')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'startDate' in values:
            try:
                start = datetime.fromisoformat(values['startDate'])
                end = datetime.fromisoformat(v)
                if end <= start:
                    raise ValueError('End date must be after start date')
            except ValueError as e:
                raise ValueError(f'Invalid date format: {str(e)}')
        return v

class AnalysisOptions(BaseModel):
    """Optional parameters for analysis"""
    cloudMaskThreshold: Optional[int] = Field(20, ge=0, le=100, description="Cloud mask threshold percentage")
    waterQualityIndices: Optional[List[str]] = Field(
        default=["ndwi", "clarity", "turbidity"],
        description="Water quality indices to calculate"
    )
    habitatClasses: Optional[List[str]] = Field(
        default=["coral", "seagrass", "sand"],
        description="Habitat classes to identify"
    )
    depthRange: Optional[Dict[str, float]] = Field(
        default={"min": 0.0, "max": 30.0},
        description="Depth range for bathymetry analysis"
    )

class Sen2CoralRequest(BaseModel):
    """Request model for Sen2Coral analysis"""
    coordinates: BBox = Field(..., description="Bounding box coordinates")
    timeRange: TimeRange = Field(..., description="Time range for analysis")
    dataSource: DataSource = Field(DataSource.sentinel2, description="Data source for analysis")
    analysisType: AnalysisType = Field(AnalysisType.water_quality, description="Type of analysis to perform")
    options: Optional[AnalysisOptions] = Field(None, description="Optional analysis parameters")

class WaterQualityMetrics(BaseModel):
    """Water quality analysis results"""
    ndwi: float = Field(..., ge=-1, le=1, description="Normalized Difference Water Index")
    clarity: float = Field(..., ge=0, le=1, description="Water clarity index")
    turbidity: float = Field(..., ge=0, le=1, description="Turbidity level")
    chlorophyll: float = Field(..., ge=0, description="Chlorophyll concentration")
    dissolvedOrganics: float = Field(..., ge=0, le=1, description="Dissolved organic matter")

class HabitatMetrics(BaseModel):
    """Habitat mapping analysis results"""
    coralCover: float = Field(..., ge=0, le=100, description="Coral cover percentage")
    seagrassCover: float = Field(..., ge=0, le=100, description="Seagrass cover percentage")
    sandCover: float = Field(..., ge=0, le=100, description="Sand cover percentage")
    rockCover: float = Field(..., ge=0, le=100, description="Rock cover percentage")
    classification: Dict[str, float] = Field(..., description="Detailed habitat classification")

class BathymetryMetrics(BaseModel):
    """Bathymetry analysis results"""
    meanDepth: float = Field(..., ge=0, description="Mean depth in meters")
    minDepth: float = Field(..., ge=0, description="Minimum depth in meters")
    maxDepth: float = Field(..., ge=0, description="Maximum depth in meters")
    depthConfidence: float = Field(..., ge=0, le=1, description="Depth estimation confidence")

class ChangeDetectionMetrics(BaseModel):
    """Change detection analysis results"""
    waterQualityChange: float = Field(..., ge=-100, le=100, description="Water quality change percentage")
    habitatChange: float = Field(..., ge=-100, le=100, description="Habitat change percentage")
    depthChange: float = Field(..., description="Depth change in meters")
    changeConfidence: float = Field(..., ge=0, le=1, description="Change detection confidence")

class GeoJSONFeature(BaseModel):
    """GeoJSON feature structure"""
    type: str = Field("Feature", description="Feature type")
    geometry: Dict[str, Any] = Field(..., description="Geometry object")
    properties: Dict[str, Any] = Field(..., description="Feature properties")

class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON feature collection"""
    type: str = Field("FeatureCollection", description="Collection type")
    features: List[GeoJSONFeature] = Field(..., description="List of features")

class AnalysisMetadata(BaseModel):
    """Metadata for analysis results"""
    processingTime: float = Field(..., ge=0, description="Processing time in seconds")
    cloudCover: float = Field(..., ge=0, le=100, description="Cloud cover percentage")
    dataQuality: float = Field(..., ge=0, le=1, description="Data quality score")
    algorithmVersion: str = Field(..., description="Algorithm version used")
    timestamp: str = Field(..., description="Analysis timestamp")
    inputParameters: Dict[str, Any] = Field(..., description="Input parameters used")

class Sen2CoralResponse(BaseModel):
    """Response model for Sen2Coral analysis"""
    bbox: BBox = Field(..., description="Analysis bounding box")
    timestamp: str = Field(..., description="Analysis timestamp")
    waterQuality: Optional[WaterQualityMetrics] = Field(None, description="Water quality results")
    habitat: Optional[HabitatMetrics] = Field(None, description="Habitat mapping results")
    bathymetry: Optional[BathymetryMetrics] = Field(None, description="Bathymetry results")
    changeDetection: Optional[ChangeDetectionMetrics] = Field(None, description="Change detection results")
    geojson: GeoJSONFeatureCollection = Field(..., description="Spatial results as GeoJSON")
    metadata: AnalysisMetadata = Field(..., description="Analysis metadata")

class JobStatus(BaseModel):
    """Job status response"""
    jobId: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status: pending, processing, completed, failed")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    message: Optional[str] = Field(None, description="Status message")
    result: Optional[Sen2CoralResponse] = Field(None, description="Analysis result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    createdAt: str = Field(..., description="Job creation timestamp")
    updatedAt: str = Field(..., description="Last update timestamp")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp")

class CapabilitiesResponse(BaseModel):
    """System capabilities response"""
    analysisTypes: List[str] = Field(..., description="Supported analysis types")
    waterQualityIndices: List[str] = Field(..., description="Available water quality indices")
    habitatClasses: List[str] = Field(..., description="Supported habitat classes")
    maxArea: float = Field(..., description="Maximum analysis area in km²")
    supportedSatellites: List[str] = Field(..., description="Supported satellite data sources")
    processingLimits: Dict[str, Union[int, float]] = Field(..., description="Processing limitations")
    algorithms: Dict[str, Dict[str, str]] = Field(..., description="Available algorithms and versions") 