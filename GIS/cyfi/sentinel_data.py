import os
from datetime import datetime
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
import numpy as np

# Configure Sentinel Hub credentials
config = SHConfig()
config.sh_client_id = '6fc4acf0-cd2e-4097-b61d-5582083e0ab4'
config.sh_client_secret = 'B1d0KSm6A4VdD7WdDFb6B88y2TGpkPVv'

class SentinelDataRetriever:
    def __init__(self, resolution=20):
        self.resolution = resolution
        self._validate_config()

    def _validate_config(self):
        """Validate Sentinel Hub configuration."""
        try:
            if not config.sh_client_id or not config.sh_client_secret:
                raise ValueError("Sentinel Hub credentials not configured")
            print("Sentinel Hub configuration validated successfully")
        except Exception as e:
            raise ValueError(f"Sentinel Hub configuration error: {str(e)}")

    def _create_bbox(self, west: float, south: float, east: float, north: float) -> BBox:
        """Create a BBox object from coordinates."""
        return BBox(bbox=(west, south, east, north), crs=CRS.WGS84)

    def _get_image_dimensions(self, bbox: BBox) -> tuple:
        """Calculate image dimensions based on bbox and resolution."""
        return bbox_to_dimensions(bbox, resolution=self.resolution)

    def _create_evalscript_ndwi(self) -> str:
        """Create evalscript for NDWI calculation."""
        return """
        //VERSION=3
        function setup() {
            return {
                input: ["B03", "B08", "B04", "B02"],
                output: {
                    bands: 4,
                    sampleType: "FLOAT32"
                }
            };
        }

        function evaluatePixel(sample) {
            // Calculate NDWI (GREEN - NIR) / (GREEN + NIR)
            let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08);
            
            // Return NDWI and RGB bands for visualization
            return [ndwi, sample.B04, sample.B03, sample.B02];
        }
        """

    async def fetch_data(self, bbox_coords: dict, time_range: dict) -> dict:
        """
        Fetch satellite data for the given coordinates and time range.
        
        Args:
            bbox_coords: Dict with west, south, east, north coordinates
            time_range: Dict with startDate and endDate strings (YYYY-MM-DD)
            
        Returns:
            Dict containing NDWI data and RGB visualization
        """
        try:
            # Create bbox and calculate dimensions
            bbox = self._create_bbox(
                bbox_coords['west'],
                bbox_coords['south'],
                bbox_coords['east'],
                bbox_coords['north']
            )
            size = self._get_image_dimensions(bbox)

            # Create request for NDWI and RGB data
            request = SentinelHubRequest(
                evalscript=self._create_evalscript_ndwi(),
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL2_L2A,
                        time_interval=(time_range['startDate'], time_range['endDate']),
                        mosaicking_order=MosaickingOrder.LEAST_CC
                    )
                ],
                responses=[
                    SentinelHubRequest.output_response("default", MimeType.TIFF)
                ],
                bbox=bbox,
                size=size,
                config=config
            )

            # Get data
            data = request.get_data()[0]
            
            # Extract bands
            ndwi = data[..., 0]  # First band is NDWI
            rgb = data[..., 1:]  # Last 3 bands are RGB

            # Calculate cloud coverage (simplified version)
            # In a real implementation, you'd use the Scene Classification Layer
            cloud_coverage = 0  # Placeholder

            return {
                'ndwi': ndwi.tolist(),
                'rgb': rgb.tolist(),
                'metadata': {
                    'resolution': self.resolution,
                    'size': size,
                    'cloudCoverage': cloud_coverage,
                    'bbox': bbox_coords,
                    'timeRange': time_range
                }
            }

        except Exception as e:
            raise Exception(f"Failed to fetch Sentinel data: {str(e)}")

    async def get_available_dates(self, bbox_coords: dict, start_date: str, end_date: str) -> list:
        """Get available dates with good quality data for the given area."""
        # TODO: Implement checking for available dates with low cloud coverage
        return []  # Placeholder 