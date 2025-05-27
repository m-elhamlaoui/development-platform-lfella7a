"""
Sen2Coral Analysis Service
"""
import asyncio
import uuid
import time
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

from models import (
    Sen2CoralRequest, Sen2CoralResponse, JobStatus,
    WaterQualityMetrics, HabitatMetrics, BathymetryMetrics,
    ChangeDetectionMetrics, GeoJSONFeatureCollection, 
    AnalysisMetadata, GeoJSONFeature
)
from data_processor import SentinelDataProcessor
from sen2coral_bridge import Sen2CoralBridge

logger = logging.getLogger(__name__)

class Sen2CoralAnalysisService:
    """Service for performing Sen2Coral analysis"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.jobs: Dict[str, JobStatus] = {}
        
        # Initialize components
        try:
            self.data_processor = SentinelDataProcessor()
            self.sen2coral_bridge = Sen2CoralBridge()
            self.mock_mode = self.sen2coral_bridge.mock_mode
            logger.info(f"Sen2Coral Analysis Service initialized (mock_mode: {self.mock_mode})")
        except Exception as e:
            logger.warning(f"Failed to initialize Sen2Coral components: {str(e)}")
            self.data_processor = None
            self.sen2coral_bridge = None
            self.mock_mode = True
        
    async def analyze(self, request: Sen2CoralRequest) -> Sen2CoralResponse:
        """
        Perform Sen2Coral analysis
        
        Args:
            request: Analysis request parameters
            
        Returns:
            Analysis results
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting {request.analysisType} analysis for area: {request.coordinates}")
            
            if self.mock_mode:
                # Use enhanced mock with real satellite data for better results
                result = await self._enhanced_mock_with_real_data(request)
            else:
                # Real Sen2Coral implementation
                result = await self._real_analysis(request)
            
            processing_time = time.time() - start_time
            logger.info(f"Analysis completed in {processing_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise
    
    async def _mock_analysis(self, request: Sen2CoralRequest) -> Sen2CoralResponse:
        """
        Mock analysis implementation for testing
        """
        # Simulate processing time
        await asyncio.sleep(2)
        
        # Calculate area for realistic mock data
        area_deg = (request.coordinates.east - request.coordinates.west) * \
                  (request.coordinates.north - request.coordinates.south)
        
        # Generate mock results based on analysis type
        water_quality = None
        habitat = None
        bathymetry = None
        change_detection = None
        
        if request.analysisType in ["water_quality", "change_detection"]:
            water_quality = WaterQualityMetrics(
                ndwi=0.75 + (area_deg * 0.1),
                clarity=0.82 - (area_deg * 0.05),
                turbidity=0.15 + (area_deg * 0.02),
                chlorophyll=0.25 + (area_deg * 0.03),
                dissolvedOrganics=0.18 + (area_deg * 0.01)
            )
        
        if request.analysisType in ["habitat", "change_detection"]:
            habitat = HabitatMetrics(
                coralCover=45.2 - (area_deg * 2),
                seagrassCover=23.8 + (area_deg * 1),
                sandCover=31.0 + (area_deg * 0.5),
                rockCover=0.0,
                classification={
                    "healthy_coral": 35.2 - (area_deg * 1.5),
                    "stressed_coral": 10.0 - (area_deg * 0.5),
                    "dense_seagrass": 15.8 + (area_deg * 0.8),
                    "sparse_seagrass": 8.0 + (area_deg * 0.2),
                    "sand": 31.0 + (area_deg * 0.5)
                }
            )
        
        if request.analysisType in ["bathymetry", "change_detection"]:
            bathymetry = BathymetryMetrics(
                meanDepth=12.5 + (area_deg * 2),
                minDepth=2.1,
                maxDepth=25.8 + (area_deg * 5),
                depthConfidence=0.87 - (area_deg * 0.1)
            )
        
        if request.analysisType == "change_detection":
            change_detection = ChangeDetectionMetrics(
                waterQualityChange=-5.2,
                habitatChange=-8.1,
                depthChange=0.3,
                changeConfidence=0.78
            )
        
        # Generate mock GeoJSON
        geojson = self._generate_mock_geojson(request.coordinates, request.analysisType)
        
        # Create metadata
        metadata = AnalysisMetadata(
            processingTime=2.0,
            cloudCover=12.5,
            dataQuality=0.92,
            algorithmVersion="2.1.0-mock",
            timestamp=datetime.utcnow().isoformat(),
            inputParameters={
                "dataSource": request.dataSource.value,
                "analysisType": request.analysisType.value,
                "cloudThreshold": request.options.cloudMaskThreshold if request.options else 20
            }
        )
        
        return Sen2CoralResponse(
            bbox=request.coordinates,
            timestamp=datetime.utcnow().isoformat(),
            waterQuality=water_quality,
            habitat=habitat,
            bathymetry=bathymetry,
            changeDetection=change_detection,
            geojson=geojson,
            metadata=metadata
        )
    
    async def _enhanced_mock_with_real_data(self, request: Sen2CoralRequest) -> Sen2CoralResponse:
        """
        Enhanced mock analysis that always fetches real satellite data for realistic results
        
        Args:
            request: Analysis request
            
        Returns:
            Enhanced analysis results based on real satellite data
        """
        try:
            logger.info("Starting enhanced mock analysis with real satellite data")
            
            # Always fetch real satellite data
            time_range = {
                'startDate': request.timeRange.startDate,
                'endDate': request.timeRange.endDate
            }
            
            if self.data_processor:
                logger.info("Fetching real satellite data...")
                satellite_result = self.data_processor.fetch_sentinel_data(
                    bbox=request.coordinates,
                    time_range=time_range,
                    data_source=request.dataSource.value,
                    resolution=60
                )
                
                if satellite_result["success"]:
                    logger.info("Successfully fetched real satellite data, generating enhanced results")
                    return await self._enhanced_mock_analysis(request, satellite_result)
                else:
                    logger.warning(f"Failed to fetch satellite data: {satellite_result.get('error', 'Unknown error')}")
            
            # Fall back to basic mock if satellite data fetch fails
            logger.info("Falling back to basic mock analysis")
            return await self._mock_analysis(request)
            
        except Exception as e:
            logger.error(f"Enhanced mock analysis failed: {str(e)}")
            # Final fallback to basic mock
            return await self._mock_analysis(request)
    
    async def _real_analysis(self, request: Sen2CoralRequest) -> Sen2CoralResponse:
        """
        Real Sen2Coral analysis implementation using satellite data and Sen2Coral algorithms
        """
        try:
            logger.info("Starting real Sen2Coral analysis")
            
            # Step 1: Fetch satellite data
            logger.info("Fetching satellite data...")
            time_range = {
                'startDate': request.timeRange.startDate,
                'endDate': request.timeRange.endDate
            }
            
            satellite_result = self.data_processor.fetch_sentinel_data(
                bbox=request.coordinates,
                time_range=time_range,
                data_source=request.dataSource.value,
                resolution=60  # Default resolution for Sen2Coral
            )
            
            if not satellite_result["success"]:
                raise ValueError(f"Failed to fetch satellite data: {satellite_result['error']}")
            
            # Step 2: Prepare data for Sen2Coral
            logger.info("Preparing data for Sen2Coral analysis...")
            satellite_data = satellite_result["data"]
            metadata = satellite_result["metadata"]
            
            # Save data in Sen2Coral compatible format
            data_path = self.data_processor.save_data_for_sen2coral(satellite_data, metadata)
            
            # Step 3: Run Sen2Coral analysis
            logger.info("Running Sen2Coral algorithms...")
            sen2coral_params = self._convert_request_to_sen2coral(request, data_path, metadata)
            sen2coral_result = self.sen2coral_bridge.run_analysis(sen2coral_params)
            
            # Step 4: Convert results to API format
            logger.info("Converting results to API format...")
            api_result = self._convert_sen2coral_result(sen2coral_result, request, metadata)
            
            # Cleanup temporary files
            try:
                if os.path.exists(data_path):
                    os.unlink(data_path)
                metadata_path = data_path.replace('.npy', '_metadata.json')
                if os.path.exists(metadata_path):
                    os.unlink(metadata_path)
            except Exception as cleanup_err:
                logger.warning(f"Failed to cleanup temporary files: {str(cleanup_err)}")
            
            logger.info("Real Sen2Coral analysis completed successfully")
            return api_result
            
        except Exception as e:
            logger.error(f"Real Sen2Coral analysis failed: {str(e)}")
            # Fall back to enhanced mock analysis with satellite data if available
            if 'satellite_result' in locals() and satellite_result.get("success"):
                logger.info("Falling back to enhanced mock analysis with real satellite data")
                return await self._enhanced_mock_analysis(request, satellite_result)
            else:
                # Fall back to basic mock analysis
                logger.info("Falling back to basic mock analysis")
                return await self._mock_analysis(request)
    
    def _convert_request_to_sen2coral(self, request: Sen2CoralRequest, data_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert API request to Sen2Coral input format
        
        Args:
            request: API request
            data_path: Path to satellite data file
            metadata: Satellite data metadata
            
        Returns:
            Sen2Coral input parameters
        """
        return {
            "dataPath": data_path,
            "bbox": [
                request.coordinates.west,
                request.coordinates.south,
                request.coordinates.east,
                request.coordinates.north
            ],
            "timeRange": {
                "start": request.timeRange.startDate,
                "end": request.timeRange.endDate
            },
            "dataSource": request.dataSource.value,
            "analysisType": request.analysisType.value,
            "options": request.options.dict() if request.options else {},
            "metadata": metadata
        }
    
    def _convert_sen2coral_result(self, sen2coral_result: Dict[str, Any], request: Sen2CoralRequest, metadata: Dict[str, Any]) -> Sen2CoralResponse:
        """
        Convert Sen2Coral output to API response format
        
        Args:
            sen2coral_result: Sen2Coral analysis results
            request: Original API request
            metadata: Satellite data metadata
            
        Returns:
            API response
        """
        # Extract results based on analysis type
        water_quality = None
        habitat = None
        bathymetry = None
        change_detection = None
        
        if "waterQuality" in sen2coral_result:
            wq = sen2coral_result["waterQuality"]
            water_quality = WaterQualityMetrics(
                ndwi=wq.get("ndwi", 0.0),
                clarity=wq.get("clarity", 0.0),
                turbidity=wq.get("turbidity", 0.0),
                chlorophyll=wq.get("chlorophyll", 0.0),
                dissolvedOrganics=wq.get("dissolvedOrganics", 0.0)
            )
        
        if "habitat" in sen2coral_result:
            hab = sen2coral_result["habitat"]
            habitat = HabitatMetrics(
                coralCover=hab.get("coralCover", 0.0),
                seagrassCover=hab.get("seagrassCover", 0.0),
                sandCover=hab.get("sandCover", 0.0),
                rockCover=hab.get("rockCover", 0.0),
                classification=hab.get("classification", {})
            )
        
        if "bathymetry" in sen2coral_result:
            bath = sen2coral_result["bathymetry"]
            bathymetry = BathymetryMetrics(
                meanDepth=bath.get("meanDepth", 0.0),
                minDepth=bath.get("minDepth", 0.0),
                maxDepth=bath.get("maxDepth", 0.0),
                depthConfidence=bath.get("depthConfidence", 0.0)
            )
        
        if "changeDetection" in sen2coral_result:
            cd = sen2coral_result["changeDetection"]
            change_detection = ChangeDetectionMetrics(
                waterQualityChange=cd.get("waterQualityChange", 0.0),
                habitatChange=cd.get("habitatChange", 0.0),
                depthChange=cd.get("depthChange", 0.0),
                changeConfidence=cd.get("changeConfidence", 0.0)
            )
        
        # Convert GeoJSON
        geojson_data = sen2coral_result.get("geojson", {"type": "FeatureCollection", "features": []})
        geojson = GeoJSONFeatureCollection(
            type=geojson_data["type"],
            features=[
                GeoJSONFeature(
                    type=feature["type"],
                    geometry=feature["geometry"],
                    properties=feature["properties"]
                ) for feature in geojson_data.get("features", [])
            ]
        )
        
        # Create metadata
        sen2coral_metadata = sen2coral_result.get("metadata", {})
        api_metadata = AnalysisMetadata(
            processingTime=sen2coral_metadata.get("processingTime", 0.0),
            cloudCover=metadata.get("cloud_cover", 0.0),
            dataQuality=metadata.get("data_quality", 0.0),
            algorithmVersion=sen2coral_metadata.get("algorithmVersion", "unknown"),
            timestamp=sen2coral_metadata.get("timestamp", datetime.utcnow().isoformat()),
            inputParameters={
                "dataSource": request.dataSource.value,
                "analysisType": request.analysisType.value,
                "coordinates": request.coordinates.dict(),
                "timeRange": request.timeRange.dict(),
                "options": request.options.dict() if request.options else {}
            }
        )
        
        return Sen2CoralResponse(
            bbox=request.coordinates,
            timestamp=datetime.utcnow().isoformat(),
            waterQuality=water_quality,
            habitat=habitat,
            bathymetry=bathymetry,
            changeDetection=change_detection,
            geojson=geojson,
            metadata=api_metadata
        )
    
    async def _enhanced_mock_analysis(self, request: Sen2CoralRequest, satellite_result: Dict[str, Any]) -> Sen2CoralResponse:
        """
        Enhanced mock analysis using real satellite data
        
        Args:
            request: Analysis request
            satellite_result: Real satellite data
            
        Returns:
            Enhanced mock analysis results
        """
        logger.info("Running enhanced mock analysis with real satellite data")
        
        # Simulate processing time
        await asyncio.sleep(2)
        
        # Use real satellite metrics as base for enhanced mock data
        water_metrics = satellite_result.get("water_metrics", {})
        metadata = satellite_result.get("metadata", {})
        
        # Generate enhanced results based on real data
        water_quality = None
        habitat = None
        bathymetry = None
        change_detection = None
        
        if request.analysisType in ["water_quality", "change_detection"]:
            # Use real NDWI data to enhance mock results
            base_ndwi = water_metrics.get("mean_ndwi", 0.0)
            water_quality = WaterQualityMetrics(
                ndwi=max(-1, min(1, base_ndwi)),
                clarity=max(0, min(1, 0.8 + base_ndwi * 0.2)),
                turbidity=max(0, min(1, 0.2 - base_ndwi * 0.1)),
                chlorophyll=max(0, water_metrics.get("poor_quality", 0) / 100 * 0.5),
                dissolvedOrganics=max(0, min(1, 0.15 + abs(base_ndwi) * 0.1))
            )
        
        if request.analysisType in ["habitat", "change_detection"]:
            # Estimate habitat based on water coverage and quality
            water_coverage = water_metrics.get("water_coverage", 0)
            clear_water = water_metrics.get("clear_water", 0)
            
            habitat = HabitatMetrics(
                coralCover=max(0, min(100, clear_water * 0.6)),
                seagrassCover=max(0, min(100, water_coverage * 0.3)),
                sandCover=max(0, min(100, 100 - water_coverage * 0.8)),
                rockCover=0.0,
                classification={
                    "healthy_coral": max(0, clear_water * 0.5),
                    "stressed_coral": max(0, clear_water * 0.1),
                    "dense_seagrass": max(0, water_coverage * 0.2),
                    "sparse_seagrass": max(0, water_coverage * 0.1),
                    "sand": max(0, 100 - water_coverage * 0.8)
                }
            )
        
        if request.analysisType in ["bathymetry", "change_detection"]:
            # Estimate bathymetry based on water clarity
            clarity_factor = water_metrics.get("clear_water", 50) / 100
            bathymetry = BathymetryMetrics(
                meanDepth=5.0 + clarity_factor * 15.0,
                minDepth=1.0,
                maxDepth=10.0 + clarity_factor * 25.0,
                depthConfidence=max(0.5, clarity_factor)
            )
        
        if request.analysisType == "change_detection":
            change_detection = ChangeDetectionMetrics(
                waterQualityChange=-2.5,
                habitatChange=-5.0,
                depthChange=0.2,
                changeConfidence=0.75
            )
        
        # Generate enhanced GeoJSON with real coordinate bounds
        geojson = self._generate_enhanced_geojson(request.coordinates, request.analysisType, water_metrics)
        
        # Create enhanced metadata
        enhanced_metadata = AnalysisMetadata(
            processingTime=2.0,
            cloudCover=metadata.get("cloud_cover", 10.0),
            dataQuality=metadata.get("data_quality", 0.9),
            algorithmVersion="2.1.0-enhanced-mock",
            timestamp=datetime.utcnow().isoformat(),
            inputParameters={
                "dataSource": request.dataSource.value,
                "analysisType": request.analysisType.value,
                "realSatelliteData": True,
                "enhancedMock": True
            }
        )
        
        return Sen2CoralResponse(
            bbox=request.coordinates,
            timestamp=datetime.utcnow().isoformat(),
            waterQuality=water_quality,
            habitat=habitat,
            bathymetry=bathymetry,
            changeDetection=change_detection,
            geojson=geojson,
            metadata=enhanced_metadata
        )
    
    def _generate_enhanced_geojson(self, bbox, analysis_type: str, water_metrics: Dict[str, float]) -> GeoJSONFeatureCollection:
        """Generate enhanced GeoJSON based on real satellite data"""
        
        # Create polygon covering the bbox
        polygon_coords = [[
            [bbox.west, bbox.south],
            [bbox.east, bbox.south],
            [bbox.east, bbox.north],
            [bbox.west, bbox.north],
            [bbox.west, bbox.south]
        ]]
        
        features = []
        water_coverage = water_metrics.get("water_coverage", 0)
        
        if analysis_type == "water_quality":
            features.append(GeoJSONFeature(
                type="Feature",
                geometry={
                    "type": "Polygon",
                    "coordinates": polygon_coords
                },
                properties={
                    "analysisType": "water_quality",
                    "metrics": {
                        "ndwi": water_metrics.get("mean_ndwi", 0.0),
                        "clarity": water_metrics.get("clear_water", 0) / 100,
                        "turbidity": water_metrics.get("poor_quality", 0) / 100,
                        "waterCoverage": water_coverage
                    },
                    "confidence": water_metrics.get("data_quality", 0.9),
                    "realData": True
                }
            ))
        
        elif analysis_type == "habitat" and water_coverage > 10:
            # Only create habitat zones if there's significant water coverage
            mid_lon = (bbox.west + bbox.east) / 2
            mid_lat = (bbox.south + bbox.north) / 2
            
            # Coral zone (where water is clearest)
            if water_metrics.get("clear_water", 0) > 20:
                features.append(GeoJSONFeature(
                    type="Feature",
                    geometry={
                        "type": "Polygon",
                        "coordinates": [[
                            [bbox.west, bbox.south],
                            [mid_lon, bbox.south],
                            [mid_lon, mid_lat],
                            [bbox.west, mid_lat],
                            [bbox.west, bbox.south]
                        ]]
                    },
                    properties={
                        "analysisType": "habitat",
                        "habitatType": "coral",
                        "metrics": {"coralCover": water_metrics.get("clear_water", 0) * 0.6},
                        "confidence": 0.85,
                        "realData": True
                    }
                ))
        
        elif analysis_type == "bathymetry" and water_coverage > 5:
            features.append(GeoJSONFeature(
                type="Feature",
                geometry={
                    "type": "Polygon",
                    "coordinates": polygon_coords
                },
                properties={
                    "analysisType": "bathymetry",
                    "metrics": {
                        "estimatedDepth": 5.0 + water_metrics.get("clear_water", 0) / 100 * 15.0,
                        "waterCoverage": water_coverage
                    },
                    "confidence": max(0.5, water_metrics.get("clear_water", 0) / 100),
                    "realData": True
                }
            ))
        
        return GeoJSONFeatureCollection(
            type="FeatureCollection",
            features=features
        )
    
    def _generate_mock_geojson(self, bbox, analysis_type: str) -> GeoJSONFeatureCollection:
        """Generate mock GeoJSON data for testing"""
        
        # Create a simple polygon covering the bbox
        polygon_coords = [[
            [bbox.west, bbox.south],
            [bbox.east, bbox.south],
            [bbox.east, bbox.north],
            [bbox.west, bbox.north],
            [bbox.west, bbox.south]
        ]]
        
        # Generate different features based on analysis type
        features = []
        
        if analysis_type == "water_quality":
            features.append(GeoJSONFeature(
                type="Feature",
                geometry={
                    "type": "Polygon",
                    "coordinates": polygon_coords
                },
                properties={
                    "analysisType": "water_quality",
                    "metrics": {
                        "ndwi": 0.75,
                        "clarity": 0.82,
                        "turbidity": 0.15
                    },
                    "confidence": 0.92
                }
            ))
        
        elif analysis_type == "habitat":
            # Create multiple habitat zones
            mid_lon = (bbox.west + bbox.east) / 2
            mid_lat = (bbox.south + bbox.north) / 2
            
            # Coral zone
            features.append(GeoJSONFeature(
                type="Feature",
                geometry={
                    "type": "Polygon",
                    "coordinates": [[
                        [bbox.west, bbox.south],
                        [mid_lon, bbox.south],
                        [mid_lon, mid_lat],
                        [bbox.west, mid_lat],
                        [bbox.west, bbox.south]
                    ]]
                },
                properties={
                    "analysisType": "habitat",
                    "habitatType": "coral",
                    "metrics": {"coralCover": 65.2},
                    "confidence": 0.88
                }
            ))
            
            # Seagrass zone
            features.append(GeoJSONFeature(
                type="Feature",
                geometry={
                    "type": "Polygon",
                    "coordinates": [[
                        [mid_lon, bbox.south],
                        [bbox.east, bbox.south],
                        [bbox.east, mid_lat],
                        [mid_lon, mid_lat],
                        [mid_lon, bbox.south]
                    ]]
                },
                properties={
                    "analysisType": "habitat",
                    "habitatType": "seagrass",
                    "metrics": {"seagrassCover": 78.5},
                    "confidence": 0.85
                }
            ))
        
        elif analysis_type == "bathymetry":
            features.append(GeoJSONFeature(
                type="Feature",
                geometry={
                    "type": "Polygon",
                    "coordinates": polygon_coords
                },
                properties={
                    "analysisType": "bathymetry",
                    "metrics": {
                        "meanDepth": 12.5,
                        "minDepth": 2.1,
                        "maxDepth": 25.8
                    },
                    "confidence": 0.87
                }
            ))
        
        return GeoJSONFeatureCollection(
            type="FeatureCollection",
            features=features
        )
    
    async def get_job_status(self, job_id: str) -> JobStatus:
        """
        Get the status of an analysis job
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Job status information
        """
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        return self.jobs[job_id]
    
    def create_job(self, request: Sen2CoralRequest) -> str:
        """
        Create a new analysis job
        
        Args:
            request: Analysis request
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        self.jobs[job_id] = JobStatus(
            jobId=job_id,
            status="pending",
            progress=0,
            message="Job created",
            createdAt=datetime.utcnow().isoformat(),
            updatedAt=datetime.utcnow().isoformat()
        )
        
        return job_id
    
    def update_job_status(self, job_id: str, status: str, progress: int, 
                         message: Optional[str] = None, 
                         result: Optional[Sen2CoralResponse] = None,
                         error: Optional[str] = None):
        """Update job status"""
        if job_id in self.jobs:
            self.jobs[job_id].status = status
            self.jobs[job_id].progress = progress
            self.jobs[job_id].updatedAt = datetime.utcnow().isoformat()
            
            if message:
                self.jobs[job_id].message = message
            if result:
                self.jobs[job_id].result = result
            if error:
                self.jobs[job_id].error = error 