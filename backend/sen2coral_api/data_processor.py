"""
Sentinel-2 Data Processor for Sen2Coral Analysis
Based on the proven water_quality_monitor.py implementation
"""
import numpy as np
import logging
from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime
import tempfile
import os

try:
    from sentinelhub import (
        SHConfig,
        CRS,
        BBox,
        DataCollection,
        MimeType,
        SentinelHubRequest,
        bbox_to_dimensions,
        MosaickingOrder
    )
    SENTINELHUB_AVAILABLE = True
except ImportError:
    SENTINELHUB_AVAILABLE = False
    print("Warning: SentinelHub not available. Install with: pip install sentinelhub")

from models import BBox as Sen2CoralBBox

logger = logging.getLogger(__name__)

class SentinelDataProcessor:
    """
    Processes Sentinel-2 data for Sen2Coral analysis
    """
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialize the Sentinel data processor
        
        Args:
            client_id: SentinelHub client ID
            client_secret: SentinelHub client secret
        """
        if not SENTINELHUB_AVAILABLE:
            raise ImportError("SentinelHub package is required for satellite data processing")
        
        self.config = SHConfig()
        
        # Use provided credentials or default ones
        self.config.sh_client_id = client_id or '6fc4acf0-cd2e-4097-b61d-5582083e0ab4'
        self.config.sh_client_secret = client_secret or 'B1d0KSm6A4VdD7WdDFb6B88y2TGpkPVv'
        
        # Validate credentials
        if not self.config.sh_client_id or not self.config.sh_client_secret:
            raise ValueError("SentinelHub credentials are required")
        
        logger.info("SentinelHub data processor initialized")
    
    def get_data_source_config(self, data_source: str) -> Dict[str, Any]:
        """
        Get configuration for the specified data source
        
        Args:
            data_source: Name of the data source (e.g., 'sentinel2', 'landsat8')
            
        Returns:
            Configuration dictionary for the data source
        """
        data_sources = {
            "sentinel2": {
                "collection": DataCollection.SENTINEL2_L2A,
                "bands": {
                    "red": "B04", "green": "B03", "blue": "B02",
                    "nir": "B08", "red_edge1": "B05", "red_edge2": "B06",
                    "red_edge3": "B07", "nir_narrow": "B8A",
                    "swir1": "B11", "swir2": "B12"
                },
                "resolution": 10,
                "mosaicking_order": MosaickingOrder.LEAST_CC,
            },
            "landsat8": {
                "collection": DataCollection.LANDSAT_OT_L2,
                "bands": {
                    "red": "B04", "green": "B03", "blue": "B02",
                    "nir": "B05", "swir1": "B06", "swir2": "B07"
                },
                "resolution": 30,
                "mosaicking_order": MosaickingOrder.MOST_RECENT,
            }
        }
        
        return data_sources.get(data_source.lower(), data_sources["sentinel2"])
    
    def get_sen2coral_evalscript(self, data_source: str = "sentinel2") -> str:
        """
        Get evaluation script optimized for Sen2Coral analysis
        
        Args:
            data_source: Satellite data source
            
        Returns:
            Evaluation script for Sen2Coral band extraction
        """
        if data_source.startswith('sentinel2'):
            return """
            //VERSION=3
            function setup() {
                return {
                    input: ["B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B11", "B12"],
                    output: { 
                        bands: 10,
                        sampleType: "FLOAT32"
                    }
                };
            }
            
            function evaluatePixel(sample) {
                // Return all bands needed for Sen2Coral analysis
                return [
                    sample.B02,  // Blue
                    sample.B03,  // Green  
                    sample.B04,  // Red
                    sample.B05,  // Red Edge 1
                    sample.B06,  // Red Edge 2
                    sample.B07,  // Red Edge 3
                    sample.B08,  // NIR
                    sample.B8A,  // NIR Narrow
                    sample.B11,  // SWIR 1
                    sample.B12   // SWIR 2
                ];
            }
            """
        elif data_source.startswith('landsat'):
            return """
            //VERSION=3
            function setup() {
                return {
                    input: ["B02", "B03", "B04", "B05", "B06", "B07"],
                    output: { 
                        bands: 6,
                        sampleType: "FLOAT32"
                    }
                };
            }
            
            function evaluatePixel(sample) {
                // Return Landsat bands for Sen2Coral analysis
                return [
                    sample.B02,  // Blue
                    sample.B03,  // Green
                    sample.B04,  // Red
                    sample.B05,  // NIR
                    sample.B06,  // SWIR 1
                    sample.B07   // SWIR 2
                ];
            }
            """
        else:
            # Default to Sentinel-2
            return self.get_sen2coral_evalscript("sentinel2")
    
    def fetch_sentinel_data(self, 
                          bbox: Sen2CoralBBox, 
                          time_range: Dict[str, str], 
                          data_source: str = "sentinel2",
                          resolution: int = 60) -> Dict[str, Any]:
        """
        Fetch Sentinel-2 data for Sen2Coral processing
        
        Args:
            bbox: Bounding box coordinates
            time_range: Time range with startDate and endDate
            data_source: Satellite data source
            resolution: Spatial resolution in meters
            
        Returns:
            Dictionary containing satellite data and metadata
        """
        try:
            logger.info(f"Fetching {data_source} data for Sen2Coral analysis")
            
            # Get data source configuration
            source_config = self.get_data_source_config(data_source)
            data_collection = source_config["collection"]
            source_resolution = source_config.get("resolution", 10)
            mosaicking_order = source_config.get("mosaicking_order", MosaickingOrder.MOST_RECENT)
            
            # Adjust resolution if needed
            if resolution < source_resolution:
                logger.warning(f"Requested resolution ({resolution}m) is higher than {data_source} native resolution. Using {source_resolution}m instead.")
                resolution = source_resolution
            
            # Validate coordinates
            self._validate_coordinates(bbox)
            
            # Convert to SentinelHub BBox
            sh_bbox = BBox(
                bbox=[bbox.west, bbox.south, bbox.east, bbox.north], 
                crs=CRS.WGS84
            )
            
            # Calculate image dimensions
            size = bbox_to_dimensions(sh_bbox, resolution=resolution)
            
            # Check if the resulting image would be too large
            if size[0] > 2500 or size[1] > 2500:
                width_deg = abs(bbox.east - bbox.west)
                height_deg = abs(bbox.north - bbox.south)
                adjusted_resolution = max(resolution, max(width_deg, height_deg) * 111000 / 2500)
                size = bbox_to_dimensions(sh_bbox, resolution=adjusted_resolution)
                logger.info(f"Adjusted resolution to {adjusted_resolution}m to handle large area")
            
            logger.info(f"Image dimensions: {size[0]}x{size[1]} pixels")
            
            # Create time interval
            time_interval = (time_range['startDate'], time_range['endDate'])
            
            # Get evaluation script for Sen2Coral
            evalscript = self.get_sen2coral_evalscript(data_source)
            
            # Create request for Sen2Coral bands
            request = SentinelHubRequest(
                evalscript=evalscript,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=data_collection,
                        time_interval=time_interval,
                        mosaicking_order=mosaicking_order
                    )
                ],
                responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                bbox=sh_bbox,
                size=size,
                config=self.config,
            )
            
            logger.info("Sending request to SentinelHub...")
            
            # Get the data
            data = request.get_data()[0]
            
            if data is None or data.size == 0:
                raise ValueError("No data returned from SentinelHub API")
            
            # Count valid pixels
            valid_pixels = np.sum(~np.isnan(data).all(axis=2))
            total_pixels = data.shape[0] * data.shape[1]
            
            if valid_pixels == 0:
                raise ValueError("No valid data for the selected area and time interval")
            
            logger.info(f"Valid pixels: {valid_pixels} out of {total_pixels} ({valid_pixels/total_pixels*100:.1f}%)")
            
            # Calculate basic water quality metrics for validation
            water_metrics = self._calculate_basic_metrics(data, data_source)
            
            return {
                "success": True,
                "data": data,
                "metadata": {
                    "bbox": {
                        "west": bbox.west,
                        "south": bbox.south, 
                        "east": bbox.east,
                        "north": bbox.north
                    },
                    "time_range": time_range,
                    "data_source": data_source,
                    "resolution": resolution,
                    "size": size,
                    "valid_pixels": int(valid_pixels),
                    "total_pixels": int(total_pixels),
                    "data_quality": float(valid_pixels / total_pixels),
                    "bands": source_config["bands"],
                    "collection": str(data_collection)
                },
                "water_metrics": water_metrics
            }
            
        except Exception as e:
            logger.error(f"Error fetching satellite data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_coordinates(self, bbox: Sen2CoralBBox) -> None:
        """Validate bounding box coordinates"""
        if not (-180 <= bbox.west <= 180 and -90 <= bbox.south <= 90 and 
                -180 <= bbox.east <= 180 and -90 <= bbox.north <= 90):
            raise ValueError(f"Invalid coordinates: {bbox}. Must be within valid lat/long ranges.")
        
        width_deg = abs(bbox.east - bbox.west)
        height_deg = abs(bbox.north - bbox.south)
        
        if width_deg > 10 or height_deg > 10:
            raise ValueError(f"Bounding box too large: {width_deg}° x {height_deg}°. Please select a smaller area (max: 10° x 10°).")
        
        if width_deg < 0.001 or height_deg < 0.001:
            raise ValueError(f"Bounding box too small: {width_deg}° x {height_deg}°. Please select a larger area (min: 0.001° x 0.001°).")
    
    def _calculate_basic_metrics(self, data: np.ndarray, data_source: str) -> Dict[str, float]:
        """
        Calculate basic water quality metrics for validation
        
        Args:
            data: Satellite imagery data
            data_source: Data source name
            
        Returns:
            Dictionary of basic water quality metrics
        """
        try:
            if data_source.startswith('sentinel2'):
                # For Sentinel-2: B03 (Green), B08 (NIR)
                green = data[:, :, 1]  # B03
                nir = data[:, :, 6]    # B08
            elif data_source.startswith('landsat'):
                # For Landsat: B03 (Green), B05 (NIR)
                green = data[:, :, 1]  # B03
                nir = data[:, :, 3]    # B05
            else:
                # Default to first available bands
                green = data[:, :, 1]
                nir = data[:, :, 3] if data.shape[2] > 3 else data[:, :, 1]
            
            # Calculate NDWI
            ndwi = np.divide(green - nir, green + nir, 
                           out=np.zeros_like(green), 
                           where=(green + nir) != 0)
            
            # Basic water detection
            water_mask = ndwi > 0.03
            water_coverage = np.sum(water_mask) / (data.shape[0] * data.shape[1]) * 100
            
            # Water quality assessment
            if np.sum(water_mask) > 0:
                water_ndwi = ndwi[water_mask]
                clear_water = np.sum(water_ndwi > 0.12) / len(water_ndwi) * 100
                moderate_quality = np.sum((water_ndwi >= 0.06) & (water_ndwi <= 0.12)) / len(water_ndwi) * 100
                poor_quality = np.sum(water_ndwi < 0.06) / len(water_ndwi) * 100
            else:
                clear_water = moderate_quality = poor_quality = 0
            
            return {
                "water_coverage": float(water_coverage),
                "clear_water": float(clear_water),
                "moderate_quality": float(moderate_quality),
                "poor_quality": float(poor_quality),
                "mean_ndwi": float(np.nanmean(ndwi)),
                "std_ndwi": float(np.nanstd(ndwi))
            }
            
        except Exception as e:
            logger.warning(f"Error calculating basic metrics: {str(e)}")
            return {
                "water_coverage": 0.0,
                "clear_water": 0.0,
                "moderate_quality": 0.0,
                "poor_quality": 0.0,
                "mean_ndwi": 0.0,
                "std_ndwi": 0.0
            }
    
    def save_data_for_sen2coral(self, data: np.ndarray, metadata: Dict[str, Any]) -> str:
        """
        Save satellite data in a format suitable for Sen2Coral processing
        
        Args:
            data: Satellite imagery data
            metadata: Data metadata
            
        Returns:
            Path to saved data file
        """
        try:
            # Create temporary file for Sen2Coral input
            temp_file = tempfile.NamedTemporaryFile(suffix='.tiff', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # Save as GeoTIFF (Sen2Coral compatible format)
            # Note: This is a simplified version. In production, you'd use rasterio
            # to properly save with geospatial metadata
            
            # For now, save as numpy array that can be loaded by Sen2Coral bridge
            np.save(temp_path.replace('.tiff', '.npy'), data)
            
            # Save metadata
            import json
            with open(temp_path.replace('.tiff', '_metadata.json'), 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Saved Sen2Coral input data to {temp_path}")
            return temp_path.replace('.tiff', '.npy')
            
        except Exception as e:
            logger.error(f"Error saving data for Sen2Coral: {str(e)}")
            raise 