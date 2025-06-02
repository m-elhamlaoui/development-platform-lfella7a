#!/usr/bin/env python
import argparse
import json
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.image import imread
import datetime
import traceback
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

# Using custom implementation without eo-learn dependency
print("Using enhanced custom water quality implementation")

from PIL import Image
from io import BytesIO

# Update the import to use absolute import
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from GIS.ml_water_detection import MLWaterDetector, enhance_water_detection

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Water Quality Analysis')
    parser.add_argument('--config', required=True, help='Path to config JSON file')
    parser.add_argument('--output', required=True, help='Path to output image file')
    parser.add_argument('--data', required=True, help='Path to output data JSON file')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with extra logging')
    return parser.parse_args()

def get_data_source_config(data_source_name):
    """
    Get the configuration for the specified data source.
    
    Args:
        data_source_name: Name of the data source (e.g., 'sentinel2', 'landsat8', 'modis')
        
    Returns:
        dict: Configuration details for the data source
    """
    data_sources = {
        # Sentinel-2 L2A configuration (atmospherically corrected)
        "sentinel2": {
            "collection": DataCollection.SENTINEL2_L2A,
            "bands": {
                "red": "B04",
                "green": "B03", 
                "blue": "B02",
                "nir": "B08",
                "swir1": "B11",
                "swir2": "B12"
            },
            "resolution": 10,
            "mosaicking_order": MosaickingOrder.LEAST_CC,  # Supports least cloud cover
            "ndwi_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B03", "B08"],
                output: {
                  bands: 1,
                  sampleType: "FLOAT32"
                }
              };
            }

            function evaluatePixel(sample) {
              // NDWI = (Green - NIR) / (Green + NIR)
              let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08);
              return [ndwi];
            }
            """,
            "true_color_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B04", "B03", "B02"],
                output: { bands: 3 }
              };
            }

            function evaluatePixel(sample) {
              return [3.5*sample.B04, 3.5*sample.B03, 3.5*sample.B02];
            }
            """,
            "water_detection_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B03", "B08", "B04"],
                output: { bands: 3 }
              };
            }

            function evaluatePixel(sample) {
              // Calculate NDWI
              let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08);
              
              // Create a water mask (NDWI > 0.03 for ocean/coastal water)
              if (ndwi > 0.03) {
                // Blue for water
                return [0.0, 0.0, 0.8];
              } else {
                // Use a semi-transparent true color for land
                return [0.7*sample.B04, 0.7*sample.B03, 0.7*sample.B02];
              }
            }
            """
        },
        
        # Sentinel-2 L1C configuration (non-atmospherically corrected)
        "sentinel2_l1c": {
            "collection": DataCollection.SENTINEL2_L1C,
            "bands": {
                "red": "B04",
                "green": "B03", 
                "blue": "B02",
                "nir": "B08",
                "swir1": "B11",
                "swir2": "B12"
            },
            "resolution": 10,
            "mosaicking_order": MosaickingOrder.LEAST_CC,
            "ndwi_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B03", "B08"],
                output: {
                  bands: 1,
                  sampleType: "FLOAT32"
                }
              };
            }

            function evaluatePixel(sample) {
              // NDWI = (Green - NIR) / (Green + NIR)
              let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08);
              return [ndwi];
            }
            """,
            "true_color_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B04", "B03", "B02"],
                output: { bands: 3 }
              };
            }

            function evaluatePixel(sample) {
              return [3.5*sample.B04, 3.5*sample.B03, 3.5*sample.B02];
            }
            """,
            "water_detection_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B03", "B08", "B04"],
                output: { bands: 3 }
              };
            }

            function evaluatePixel(sample) {
              // Calculate NDWI
              let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08);
              
              // Create a water mask (NDWI > 0.03 for ocean/coastal water)
              if (ndwi > 0.03) {
                // Blue for water
                return [0.0, 0.0, 0.8];
              } else {
                // Use a semi-transparent true color for land
                return [0.7*sample.B04, 0.7*sample.B03, 0.7*sample.B02];
              }
            }
            """
        },
        
        # Landsat-8/9 L2 configuration (atmospherically corrected)
        "landsat8": {
            "collection": DataCollection.LANDSAT_OT_L2,
            "bands": {
                "red": "B04", 
                "green": "B03", 
                "blue": "B02",
                "nir": "B05",
                "swir1": "B06",
                "swir2": "B07"
            },
            "resolution": 30,
            "mosaicking_order": MosaickingOrder.MOST_RECENT,  # Use most recent for Landsat
            "ndwi_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B03", "B05"],
                output: {
                  bands: 1,
                  sampleType: "FLOAT32"
                }
              };
            }

            function evaluatePixel(sample) {
              // NDWI = (Green - NIR) / (Green + NIR)
              let ndwi = (sample.B03 - sample.B05) / (sample.B03 + sample.B05);
              return [ndwi];
            }
            """,
            "true_color_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B04", "B03", "B02"],
                output: { bands: 3 }
              };
            }

            function evaluatePixel(sample) {
              return [3.5*sample.B04, 3.5*sample.B03, 3.5*sample.B02];
            }
            """,
            "water_detection_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B03", "B05", "B04"],
                output: { bands: 3 }
              };
            }

            function evaluatePixel(sample) {
              // Calculate NDWI
              let ndwi = (sample.B03 - sample.B05) / (sample.B03 + sample.B05);
              
              // Create a water mask (NDWI > 0.03 for ocean/coastal water)
              if (ndwi > 0.03) {
                // Blue for water
                return [0.0, 0.0, 0.8];
              } else {
                // Use a semi-transparent true color for land
                return [0.7*sample.B04, 0.7*sample.B03, 0.7*sample.B02];
              }
            }
            """
        },
        
        # Landsat-8/9 L1 configuration (non-atmospherically corrected)
        "landsat8_l1": {
            "collection": DataCollection.LANDSAT_OT_L1,
            "bands": {
                "red": "B04", 
                "green": "B03", 
                "blue": "B02",
                "nir": "B05",
                "swir1": "B06",
                "swir2": "B07"
            },
            "resolution": 30,
            "mosaicking_order": MosaickingOrder.MOST_RECENT,
            "ndwi_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B03", "B05"],
                output: {
                  bands: 1,
                  sampleType: "FLOAT32"
                }
              };
            }

            function evaluatePixel(sample) {
              // NDWI = (Green - NIR) / (Green + NIR)
              let ndwi = (sample.B03 - sample.B05) / (sample.B03 + sample.B05);
              return [ndwi];
            }
            """,
            "true_color_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B04", "B03", "B02"],
                output: { bands: 3 }
              };
            }

            function evaluatePixel(sample) {
              return [3.5*sample.B04, 3.5*sample.B03, 3.5*sample.B02];
            }
            """,
            "water_detection_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B03", "B05", "B04"],
                output: { bands: 3 }
              };
            }

            function evaluatePixel(sample) {
              // Calculate NDWI
              let ndwi = (sample.B03 - sample.B05) / (sample.B03 + sample.B05);
              
              // Create a water mask (NDWI > 0.03 for ocean/coastal water)
              if (ndwi > 0.03) {
                // Blue for water
                return [0.0, 0.0, 0.8];
              } else {
                // Use a semi-transparent true color for land
                return [0.7*sample.B04, 0.7*sample.B03, 0.7*sample.B02];
              }
            }
            """
        },
        
        # Landsat 7 ETM+ L2 configuration (atmospherically corrected)
        "landsat7": {
            "collection": DataCollection.LANDSAT_ETM_L2,
            "bands": {
                "red": "B03", 
                "green": "B02", 
                "blue": "B01",
                "nir": "B04",
                "swir1": "B05",
                "swir2": "B07"
            },
            "resolution": 30,
            "mosaicking_order": MosaickingOrder.MOST_RECENT,
            "ndwi_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B02", "B04"],
                output: {
                  bands: 1,
                  sampleType: "FLOAT32"
                }
              };
            }

            function evaluatePixel(sample) {
              // NDWI = (Green - NIR) / (Green + NIR)
              let ndwi = (sample.B02 - sample.B04) / (sample.B02 + sample.B04);
              return [ndwi];
            }
            """,
            "true_color_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B03", "B02", "B01"],
                output: { bands: 3 }
              };
            }

            function evaluatePixel(sample) {
              return [3.5*sample.B03, 3.5*sample.B02, 3.5*sample.B01];
            }
            """,
            "water_detection_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B02", "B04", "B03"],
                output: { bands: 3 }
              };
            }

            function evaluatePixel(sample) {
              // Calculate NDWI
              let ndwi = (sample.B02 - sample.B04) / (sample.B02 + sample.B04);
              
              // Create a water mask (NDWI > 0.03 for ocean/coastal water)
              if (ndwi > 0.03) {
                // Blue for water
                return [0.0, 0.0, 0.8];
              } else {
                // Use a semi-transparent true color for land
                return [0.7*sample.B03, 0.7*sample.B02, 0.7*sample.B01];
              }
            }
            """
        },
        
        # Landsat 4-5 TM L2 configuration (atmospherically corrected)
        "landsat5": {
            "collection": DataCollection.LANDSAT_TM_L2,
            "bands": {
                "red": "B03", 
                "green": "B02", 
                "blue": "B01",
                "nir": "B04",
                "swir1": "B05",
                "swir2": "B07"
            },
            "resolution": 30,
            "mosaicking_order": MosaickingOrder.MOST_RECENT,
            "ndwi_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B02", "B04"],
                output: {
                  bands: 1,
                  sampleType: "FLOAT32"
                }
              };
            }

            function evaluatePixel(sample) {
              // NDWI = (Green - NIR) / (Green + NIR)
              let ndwi = (sample.B02 - sample.B04) / (sample.B02 + sample.B04);
              return [ndwi];
            }
            """,
            "true_color_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B03", "B02", "B01"],
                output: { bands: 3 }
              };
            }

            function evaluatePixel(sample) {
              return [3.5*sample.B03, 3.5*sample.B02, 3.5*sample.B01];
            }
            """,
            "water_detection_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B02", "B04", "B03"],
                output: { bands: 3 }
              };
            }

            function evaluatePixel(sample) {
              // Calculate NDWI
              let ndwi = (sample.B02 - sample.B04) / (sample.B02 + sample.B04);
              
              // Create a water mask (NDWI > 0.03 for ocean/coastal water)
              if (ndwi > 0.03) {
                // Blue for water
                return [0.0, 0.0, 0.8];
              } else {
                // Use a semi-transparent true color for land
                return [0.7*sample.B03, 0.7*sample.B02, 0.7*sample.B01];
              }
            }
            """
        },

        # Harmonized Landsat Sentinel (HLS) configuration
        "hls": {
            "collection": DataCollection.LANDSAT_OT_L2,  # Using Landsat 8 as base since HLS isn't directly available
            "bands": {
                "red": "B04", 
                "green": "B03", 
                "blue": "B02",
                "nir": "B05",
                "swir1": "B06",
                "swir2": "B07"
            },
            "resolution": 30,
            "mosaicking_order": MosaickingOrder.MOST_RECENT,
            "ndwi_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B03", "B05"],
                output: {
                  bands: 1,
                  sampleType: "FLOAT32"
                }
              };
            }

            function evaluatePixel(sample) {
              // NDWI = (Green - NIR) / (Green + NIR)
              let ndwi = (sample.B03 - sample.B05) / (sample.B03 + sample.B05);
              return [ndwi];
            }
            """,
            "true_color_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B04", "B03", "B02"],
                output: { bands: 3 }
              };
            }

            function evaluatePixel(sample) {
              return [3.5*sample.B04, 3.5*sample.B03, 3.5*sample.B02];
            }
            """,
            "water_detection_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B03", "B05", "B04"],
                output: { bands: 3 }
              };
            }

            function evaluatePixel(sample) {
              // Calculate NDWI
              let ndwi = (sample.B03 - sample.B05) / (sample.B03 + sample.B05);
              
              // Create a water mask (NDWI > 0.03 for ocean/coastal water)
              if (ndwi > 0.03) {
                // Blue for water
                return [0.0, 0.0, 0.8];
              } else {
                // Use a semi-transparent true color for land
                return [0.7*sample.B04, 0.7*sample.B03, 0.7*sample.B02];
              }
            }
            """
        },
        
        # MODIS configuration
        "modis": {
            "collection": DataCollection.MODIS,
            "bands": {
                "red": "B01", 
                "green": "B04", 
                "blue": "B03",
                "nir": "B02",
                "swir1": "B06",
                "swir2": "B07"
            },
            "resolution": 250,
            "mosaicking_order": MosaickingOrder.MOST_RECENT,  # Use most recent for MODIS
            "ndwi_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B04", "B02"],
                output: {
                  bands: 1,
                  sampleType: "FLOAT32"
                }
              };
            }

            function evaluatePixel(sample) {
              // NDWI = (Green - NIR) / (Green + NIR)
              let ndwi = (sample.B04 - sample.B02) / (sample.B04 + sample.B02);
              return [ndwi];
            }
            """,
            "true_color_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B01", "B04", "B03"],
                output: { bands: 3 }
              };
            }

            function evaluatePixel(sample) {
              return [3.5*sample.B01, 3.5*sample.B04, 3.5*sample.B03];
            }
            """,
            "water_detection_script": """
            //VERSION=3
            function setup() {
              return {
                input: ["B04", "B02", "B01"],
                output: { bands: 3 }
              };
            }

            function evaluatePixel(sample) {
              // Calculate NDWI
              let ndwi = (sample.B04 - sample.B02) / (sample.B04 + sample.B02);
              
              // Create a water mask (NDWI > 0.03 for ocean/coastal water)
              if (ndwi > 0.03) {
                // Blue for water
                return [0.0, 0.0, 0.8];
              } else {
                // Use a semi-transparent true color for land
                return [0.7*sample.B01, 0.7*sample.B04, 0.7*sample.B03];
              }
            }
            """
        }
    }
    
    # Return the default (Sentinel-2) if the source is not found
    return data_sources.get(data_source_name.lower(), data_sources["sentinel2"])

def get_sentinel_data(bbox_coords, time_interval, resolution=60, data_source="sentinel2", debug=False):
    """
    Retrieve satellite data for water quality analysis
    
    Args:
        bbox_coords: Tuple of (west, south, east, north) coordinates
        time_interval: Tuple of (start_date, end_date) for the time range
        resolution: Spatial resolution in meters (default: 60m)
        data_source: Satellite data source to use (default: "sentinel2")
        debug: Enable debug mode with extra logging
        
    Returns:
        Dictionary with the results and analysis
    """
    try:
        # Get data source configuration
        source_config = get_data_source_config(data_source)
        data_collection = source_config["collection"]
        source_resolution = source_config.get("resolution", 10)
        mosaicking_order = source_config.get("mosaicking_order", MosaickingOrder.MOST_RECENT)
        
        # Adjust resolution if needed based on data source
        if resolution < source_resolution:
            print(f"Warning: Requested resolution ({resolution}m) is higher than {data_source} native resolution. Using {source_resolution}m instead.")
            resolution = source_resolution
        
        # Log key info
        print(f"Processing area: {bbox_coords}")
        print(f"Time interval: {time_interval}")
        print(f"Resolution: {resolution}m")
        print(f"Data source: {data_source}")
        print(f"Mosaicking order: {mosaicking_order}")
        
        # Set up authentication
        config = SHConfig()
        
        # Configure Sentinel Hub credentials
        config.sh_client_id = '6fc4acf0-cd2e-4097-b61d-5582083e0ab4'
        config.sh_client_secret = 'B1d0KSm6A4VdD7WdDFb6B88y2TGpkPVv'
        
        # Check if authentication is properly set
        if not config.sh_client_id or not config.sh_client_secret:
            raise ValueError("Missing Sentinel Hub credentials")
        
        # Validate coordinates
        west, south, east, north = bbox_coords
        
        # Check if coordinates are valid
        if not (-180 <= west <= 180 and -90 <= south <= 90 and -180 <= east <= 180 and -90 <= north <= 90):
            raise ValueError(f"Invalid coordinates: {bbox_coords}. Must be within valid lat/long ranges.")
        
        # Check if bounding box is too large
        width_deg = abs(east - west)
        height_deg = abs(north - south)
        
        if width_deg > 10 or height_deg > 10:
            raise ValueError(f"Bounding box too large: {width_deg}° x {height_deg}°. Please select a smaller area (max: 10° x 10°).")
        
        # Check if bounding box is too small
        if width_deg < 0.001 or height_deg < 0.001:
            raise ValueError(f"Bounding box too small: {width_deg}° x {height_deg}°. Please select a larger area (min: 0.001° x 0.001°).")
        
        # Convert bbox to Sentinel Hub format
        bbox = BBox(bbox=[west, south, east, north], crs=CRS.WGS84)
        
        # Calculate image dimensions
        size = bbox_to_dimensions(bbox, resolution=resolution)
        
        # Check if the resulting image would be too large
        if size[0] > 2500 or size[1] > 2500:
            # Recalculate with a lower resolution if the area is too large
            adjusted_resolution = max(resolution, max(width_deg, height_deg) * 111000 / 2500)  # 111km per degree
            size = bbox_to_dimensions(bbox, resolution=adjusted_resolution)
            print(f"Adjusted resolution to {adjusted_resolution}m to handle large area")
        
        print(f"Image dimensions: {size[0]}x{size[1]} pixels")
        
        # Use the evaluation scripts from the data source config
        evalscript_ndwi = source_config["ndwi_script"]
        evalscript_true_color = source_config["true_color_script"]
        evalscript_water_detection = source_config["water_detection_script"]
        
        # Create request for NDWI calculation
        request_ndwi = SentinelHubRequest(
            evalscript=evalscript_ndwi,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=data_collection,
                    time_interval=time_interval,
                    mosaicking_order=mosaicking_order
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            size=size,
            config=config,
        )
        
        # Create request for true color image
        request_true_color = SentinelHubRequest(
            evalscript=evalscript_true_color,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=data_collection,
                    time_interval=time_interval,
                    mosaicking_order=mosaicking_order
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
            bbox=bbox,
            size=size,
            config=config,
        )
        
        # Create an enhanced algal detection script that depends on the data source
        if data_source.startswith('sentinel2'):
            # For Sentinel-2, use NDCI (Normalized Difference Chlorophyll Index) and Red Edge bands
            evalscript_algal_detection = """
        //VERSION=3
        function setup() {
          return {
        input: ["B03", "B04", "B05", "B06", "B07", "B8A", "B11", "B12"],
            output: {
              bands: 1,
              sampleType: "FLOAT32"
            }
          };
        }

        function evaluatePixel(sample) {
      // NDWI for water masking
      var ndwi = (sample.B03 - sample.B8A) / (sample.B03 + sample.B8A);
      
      // Only calculate indices for water pixels (NDWI > 0.03)
      if (ndwi > 0.03) {
        // Normalized Difference Chlorophyll Index (NDCI) = (B05 - B04) / (B05 + B04)
        // Good for detecting chlorophyll-a in water
        var ndci = (sample.B05 - sample.B04) / (sample.B05 + sample.B04);
        
        // Red-Edge Chlorophyll Index = B07 / B05 - 1
        // Sensitive to chlorophyll concentrations
        var reci = (sample.B07 / sample.B05) - 1;
        
        // Modified Chlorophyll Absorption Ratio Index (MCARI)
        // Better sensitivity to chlorophyll variations
        var mcari = ((sample.B05 - sample.B04) - 0.2 * (sample.B05 - sample.B03)) * (sample.B05 / sample.B04);
        
        // Combined algal index with weighted components
        // Higher values indicate higher chlorophyll/algae presence
        var algalIndex = (ndci * 0.5) + (reci * 0.3) + (mcari * 0.2);
        
        return [algalIndex];
      } else {
        // Not water
        return [-9999];
      }
    }
    """
        elif data_source.startswith('landsat'):
            # For Landsat, adapt using available bands
            evalscript_algal_detection = """
        //VERSION=3
        function setup() {
          return {
        input: ["B02", "B03", "B04", "B05", "B06", "B07"],
        output: {
          bands: 1,
          sampleType: "FLOAT32"
        }
          };
        }

        function evaluatePixel(sample) {
      // NDWI for water masking (using Green and NIR)
      var ndwi = (sample.B03 - sample.B05) / (sample.B03 + sample.B05);
      
      // Only calculate for water pixels
      if (ndwi > 0.03) {
        // NIR/Red ratio - higher in algae-laden water
        var nirRedRatio = sample.B05 / sample.B04;
        
        // SWIR/NIR ratio - helps distinguish organic matter
        var swirNirRatio = sample.B06 / sample.B05;
        
        // Simple 3-band ratio (Green/Red)/Blue - sensitive to chlorophyll
        var triband = (sample.B03 / sample.B04) / sample.B02;
        
        // Combined algal index - higher values indicate more algal presence
        var algalIndex = (nirRedRatio * 0.6) + (triband * 0.3) - (swirNirRatio * 0.1);
        
        return [algalIndex];
      } else {
        // Not water
        return [-9999];
      }
    }
    """
        else:
            # For MODIS and other sensors with limited bands
            evalscript_algal_detection = """
        //VERSION=3
        function setup() {
          return {
        input: ["B01", "B02", "B03", "B04", "B05", "B06", "B07"],
        output: {
          bands: 1,
          sampleType: "FLOAT32"
        }
          };
        }

        function evaluatePixel(sample) {
      // NDWI for water masking
      var ndwi = (sample.B04 - sample.B02) / (sample.B04 + sample.B02);
          
      // Only calculate for water pixels
      if (ndwi > 0.03) {
        // NIR/Red ratio - higher in algae-laden water
        var nirRedRatio = sample.B02 / sample.B01;
        
        // Enhanced algae detection using multi-band approach
        var algalIndex = nirRedRatio * (sample.B04 / sample.B03);
        
        return [algalIndex];
          } else {
        // Not water
        return [-9999];
          }
        }
        """
        
        # Create request for algal detection
        request_algal_detection = SentinelHubRequest(
            evalscript=evalscript_algal_detection,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=data_collection,
                    time_interval=time_interval,
                    mosaicking_order=mosaicking_order
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            size=size,
            config=config,
        )
        
        # Create request for water detection visualization
        request_water_detection = SentinelHubRequest(
            evalscript=evalscript_water_detection,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=data_collection,
                    time_interval=time_interval,
                    mosaicking_order=mosaicking_order
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
            bbox=bbox,
            size=size,
            config=config,
        )
        
        print("Sending requests to Sentinel Hub...")
        
        # Process NDWI data
        ndwi_data = request_ndwi.get_data()[0]
        
        # Check if we got valid data
        if ndwi_data is None or ndwi_data.size == 0:
            raise ValueError("No data returned from Sentinel Hub API")
        
        # Get algal detection data
        print("Getting algal detection data...")
        try:
            algal_data = request_algal_detection.get_data()[0]
            algal_data_available = True
            print("Successfully received algal detection data")
        except Exception as e:
            print(f"Warning: Could not retrieve algal detection data: {str(e)}")
            algal_data = None
            algal_data_available = False
        
        # Get true color image
        print("Getting true color image...")
        try:
            true_color_data = request_true_color.get_data()[0]
            true_color_available = True
            print("Successfully received true color image")
        except Exception as e:
            print(f"Warning: Could not retrieve true color image: {str(e)}")
            true_color_data = None
            true_color_available = False
        
        # Get water detection visualization
        print("Getting water detection visualization...")
        try:
            water_detection_data = request_water_detection.get_data()[0]
            water_detection_available = True
            print("Successfully received water detection visualization")
        except Exception as e:
            print(f"Warning: Could not retrieve water detection visualization: {str(e)}")
            water_detection_data = None
            water_detection_available = False
        
        # Count valid pixels
        valid_pixels = np.sum(~np.isnan(ndwi_data))
        if valid_pixels == 0:
            raise ValueError("No valid data for the selected area and time interval. Try a different area or date range.")
        
        print(f"Valid pixels: {valid_pixels} out of {ndwi_data.size} ({valid_pixels/ndwi_data.size*100:.1f}%)")
        
        # Traditional NDWI Analysis
        ndwi_water_mask = ndwi_data > 0.03
        ndwi_water_pixels = np.sum(ndwi_water_mask)
        ndwi_water_coverage = (ndwi_water_pixels / valid_pixels) * 100

        # Calculate NDWI-based water quality metrics
        ndwi_metrics = calculate_water_metrics(ndwi_data, ndwi_water_mask, algal_data, algal_data_available)
        
        # ML-Enhanced Analysis
        try:
            print("Performing ML-enhanced water detection...")
            # Define model path
            model_dir = os.path.join(os.path.dirname(__file__), 'models')
            os.makedirs(model_dir, exist_ok=True)
            model_path = os.path.join(model_dir, f'water_detector_{data_source}.joblib')
            
            # Use ML-enhanced water detection
            ml_water_mask = enhance_water_detection(ndwi_data, true_color_data, model_path)
            ml_water_pixels = np.sum(ml_water_mask)
            ml_water_coverage = (ml_water_pixels / valid_pixels) * 100
            
            # Calculate ML-based water quality metrics
            ml_metrics = calculate_water_metrics(ndwi_data, ml_water_mask, algal_data, algal_data_available)
            ml_analysis_available = True
            print("ML-Enhanced water detection complete")
        except Exception as ml_err:
            print(f"ML enhancement failed: {str(ml_err)}")
            ml_metrics = None
            ml_analysis_available = False
        
        return {
            "success": True,
            "data": {
                "ndwi_analysis": {
                    "waterCoverage": round(ndwi_water_coverage, 1),
                    "clearWater": round(ndwi_metrics['clear_water_percent'], 1),
                    "moderateQuality": round(ndwi_metrics['moderate_quality_percent'], 1),
                    "algalPresence": round(ndwi_metrics['algal_presence_percent'], 1),
                },
                "ml_analysis": ml_metrics and {
                    "waterCoverage": round(ml_water_coverage, 1),
                    "clearWater": round(ml_metrics['clear_water_percent'], 1),
                    "moderateQuality": round(ml_metrics['moderate_quality_percent'], 1),
                    "algalPresence": round(ml_metrics['algal_presence_percent'], 1),
                },
                "trueColorAvailable": true_color_available,
                "waterDetectionAvailable": water_detection_available,
                "dataSource": data_source,
                "mlAnalysisAvailable": ml_analysis_available
            },
            "visualization": {
                "ndwi": ndwi_data,
                "true_color": true_color_data,
                "water_detection": water_detection_data,
                "ndwi_mask": ndwi_water_mask,
                "ml_mask": ml_water_mask if ml_analysis_available else None,
                "algal_detection": algal_data if algal_data_available else None
            }
        }
    
    except Exception as e:
        # Handle errors
        error_message = str(e)
        print(f"Error retrieving data from Sentinel Hub: {error_message}")
        traceback.print_exc()
        return {
            "success": False,
            "error": f"Error analyzing water quality: {error_message}"
        }

def calculate_water_metrics(ndwi_data, water_mask, algal_data, algal_data_available):
    """Calculate water quality metrics using the provided water mask"""
    water_pixels = np.sum(water_mask)
    if water_pixels > 0:
        # Get NDWI values only for water pixels
        water_ndwi = ndwi_data[water_mask]
        
        # 1. Clear water (NDWI > 0.12)
        clear_mask = water_ndwi > 0.12
        clear_pixels = np.sum(clear_mask)
        clear_water_percent = (clear_pixels / water_pixels) * 100
        
        # 2. Moderate quality (0.06 <= NDWI <= 0.12)
        moderate_mask = (water_ndwi >= 0.06) & (water_ndwi <= 0.12)
        moderate_pixels = np.sum(moderate_mask)
        moderate_quality_percent = (moderate_pixels / water_pixels) * 100
        
        # 3. Process algal detection
        algal_presence_percent = calculate_algal_presence(
            water_mask, algal_data, algal_data_available, water_ndwi, water_pixels
        )
        
        return {
            'clear_water_percent': clear_water_percent,
            'moderate_quality_percent': moderate_quality_percent,
            'algal_presence_percent': algal_presence_percent
        }
    else:
        return {
            'clear_water_percent': 0,
            'moderate_quality_percent': 0,
            'algal_presence_percent': 0
        }

def calculate_algal_presence(water_mask, algal_data, algal_data_available, water_ndwi, water_pixels):
    """Calculate algal presence percentage"""
    if algal_data_available and algal_data is not None:
        valid_algal_mask = (algal_data > -9990) & water_mask
        if np.sum(valid_algal_mask) > 0:
            algal_index = algal_data[valid_algal_mask]
            algal_threshold = 0.15
            algal_mask = algal_index > algal_threshold
            algal_pixels = np.sum(algal_mask)
            return (algal_pixels / water_pixels) * 100
    
    # Fallback using NDWI
    algal_pixels = np.sum(water_ndwi < 0.08)
    return (algal_pixels / water_pixels) * 15

def explain_ndwi_values():
    """
    Returns an explanation of what different NDWI values represent.
    
    This function provides information about how to interpret the NDWI visualization,
    particularly explaining what different colored zones represent.
    
    Returns:
        dict: A dictionary containing explanations for different NDWI value ranges
    """
    return {
        "explanation": "The NDWI (Normalized Difference Water Index) visualization shows different values representing various surface types:",
        "ranges": [
            {
                "range": "NDWI > 0.3",
                "color": "Deep blue",
                "meaning": "Clear, deep water bodies with minimal suspended particles"
            },
            {
                "range": "0.05 < NDWI < 0.3",
                "color": "Light blue",
                "meaning": "Water bodies with some turbidity or shallow water"
            },
            {
                "range": "0 < NDWI < 0.05",
                "color": "White/yellow",
                "meaning": "Transition zones like shorelines, very shallow water, or water with high sediment"
            },
            {
                "range": "-0.2 < NDWI < 0",
                "color": "Light red",
                "meaning": "Moist soil, wetlands, or areas with high moisture content but not covered by water"
            },
            {
                "range": "NDWI < -0.2",
                "color": "Deep red",
                "meaning": "Dry land, built-up areas, vegetation, and other non-water surfaces"
            }
        ],
        "note": "White/yellow zones in the NDWI visualization often represent transition areas between water and land, such as shorelines, wetlands, very shallow water, or water with high sediment content. These areas have NDWI values close to zero, making them appear as transition zones in the colormap. These should not be confused with algal blooms, which require specialized spectral indices for accurate detection."
    }

def create_visualization(data, output_path, bbox_coords, data_source="sentinel2"):
    """Create a water quality visualization image"""
    try:
        # Extract data
        ndwi = data["visualization"]["ndwi"]
        true_color = data["visualization"].get("true_color")
        water_detection = data["visualization"].get("water_detection")
        algal_data = data["visualization"].get("algal_detection")
        
        # Get quality metrics from NDWI analysis
        ndwi_metrics = data["data"]["ndwi_analysis"]
        water_coverage = ndwi_metrics["waterCoverage"]
        clear_water = ndwi_metrics["clearWater"]
        moderate_quality = ndwi_metrics["moderateQuality"]
        algal_presence = ndwi_metrics["algalPresence"]
        
        # Get data source information
        source_config = get_data_source_config(data_source)
        source_name = {
            "sentinel2": "Sentinel-2",
            "landsat8": "Landsat 8/9",
            "modis": "MODIS"
        }.get(data_source.lower(), "Sentinel-2")
        
        # Prepare output paths
        rgb_output_path = output_path.replace('.png', '_rgb.png')
        
        # Create a figure with three subplots
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # Display true color image
        if true_color is not None:
            axes[0].imshow(true_color)
            axes[0].set_title('True Color Image')
            axes[0].axis('off')
            # Save true color image separately
            plt.imsave(rgb_output_path, true_color)
            print(f"Saved true color image to {rgb_output_path}")
        else:
            axes[0].text(0.5, 0.5, 'True color image not available', 
                      ha='center', va='center')
            axes[0].axis('off')
        
        # Display NDWI
        im1 = axes[1].imshow(ndwi, cmap='RdYlBu', vmin=-0.5, vmax=0.5)
        axes[1].set_title('NDWI (Normalized Difference Water Index)')
        axes[1].axis('off')
        cbar = fig.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)
        cbar.set_label('NDWI Value')
        
        # Add annotation for white/yellow zones
        axes[1].text(0.5, 0.95, 'White/yellow areas: Transition zones or shallow water (NDWI near 0)',
                  transform=axes[1].transAxes, ha='center', fontsize=8,
                  bbox=dict(facecolor='white', alpha=0.7, boxstyle='round'))
        
        # Display water detection or algal bloom visualization if available
        if algal_data is not None and data_source in ['sentinel2', 'sentinel2_l1c', 'landsat8', 'landsat8_l1', 'landsat7', 'landsat5', 'hls']:
            # Create a custom colormap for algal visualization
            algal_cmap = plt.cm.YlOrRd  # Yellow-Orange-Red colormap
            
            # Apply the water mask to the algal data
            masked_algal = np.copy(algal_data)
            masked_algal[ndwi <= 0.03] = np.nan  # Mask out non-water areas
            
            # Display only in water areas
            im2 = axes[2].imshow(masked_algal, cmap=algal_cmap, vmin=0, vmax=2)
            axes[2].set_title('Algal Bloom Potential')
            axes[2].axis('off')
            cbar2 = fig.colorbar(im2, ax=axes[2], fraction=0.046, pad=0.04)
            cbar2.set_label('Algal Index')
            
            # Add legend for algal visualization
            axes[2].text(0.5, 0.05, 'Higher values indicate increased likelihood of algal presence',
                      transform=axes[2].transAxes, ha='center', fontsize=8,
                      bbox=dict(facecolor='white', alpha=0.7, boxstyle='round'))
        elif water_detection is not None:
            # Use the regular water detection visualization
            axes[2].imshow(water_detection)
            axes[2].set_title('Water Detection (NDWI > 0.03)')
            axes[2].axis('off')
        else:
            # If no visualization is available, create one based on NDWI
            water_rgb = np.zeros((ndwi.shape[0], ndwi.shape[1], 3))
            water_rgb[:, :, 2] = np.where(ndwi > 0.03, 0.8, 0.2)  # Blue channel for water
            water_rgb[:, :, 1] = np.where(ndwi > 0.03, 0.0, 0.6)  # Green channel for land
            water_rgb[:, :, 0] = np.where(ndwi > 0.03, 0.0, 0.7)  # Red channel for land
            axes[2].imshow(water_rgb)
            axes[2].set_title('Water Detection (NDWI > 0.03)')
            axes[2].axis('off')
        
        # Add water percentage text
        plt.figtext(0.5, 0.01, 
                   f"Water coverage: {water_coverage:.1f}% of area | "
                   f"Clear water: {clear_water:.1f}% | "
                   f"Moderate quality: {moderate_quality:.1f}% | "
                   f"Potential issues: {algal_presence:.1f}%", 
                   ha='center', fontsize=12, 
                   bbox={'facecolor': 'white', 'alpha': 0.7, 'pad': 5})
        
        # Add region coordinates and data source
        west, south, east, north = bbox_coords
        plt.suptitle(f'Water Quality Analysis - {source_name}\nRegion: [{west:.4f}, {south:.4f}, {east:.4f}, {north:.4f}]', 
                    fontsize=16)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)  # Close the figure to free memory
        
        return True, rgb_output_path if true_color is not None else None
        
    except Exception as e:
        print(f"Error creating visualization: {str(e)}")
        traceback.print_exc()
        
        # Create a simple error image
        fig = plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, f"Error creating visualization:\n{str(e)}", 
                 ha='center', va='center', fontsize=12,
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        plt.axis('off')
        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        return False, None

def generate_detailed_ndwi_visualization(ndwi_data, output_path, bbox_coords, data_source="sentinel2"):
    """
    Generate a more detailed NDWI visualization with clearer labeling for transition zones.
    
    Args:
        ndwi_data: The NDWI data array
        output_path: Path to save the visualization
        bbox_coords: Bounding box coordinates for the region
        data_source: Satellite data source used (default: "sentinel2")
        
    Returns:
        bool: Success indicator
    """
    try:
        # Get data source information
        source_name = {
            "sentinel2": "Sentinel-2",
            "landsat8": "Landsat 8/9",
            "modis": "MODIS"
        }.get(data_source.lower(), "Sentinel-2")
        
        # Create a custom colormap that highlights transition zones
        # This creates a colormap with clear distinctions between different NDWI value ranges
        colors = [(0.7, 0, 0),      # Deep red (< -0.2)
                 (0.9, 0.4, 0.4),  # Light red (-0.2 to 0)
                 (1, 1, 0.8),      # Pale yellow (0 to 0.05)
                 (0.6, 0.8, 1),    # Light blue (0.05 to 0.3)
                 (0, 0, 0.8)]      # Deep blue (> 0.3)
        
        positions = [0, 0.3, 0.5, 0.55, 1]
        custom_cmap = LinearSegmentedColormap.from_list('custom_ndwi', list(zip(positions, colors)))
        
        # Create the visualization
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Display NDWI with custom colormap
        im = ax.imshow(ndwi_data, cmap=custom_cmap, vmin=-0.5, vmax=0.5)
        ax.set_title('Detailed NDWI Visualization', fontsize=16)
        ax.axis('off')
        
        # Add colorbar with labeled sections
        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('NDWI Value', fontsize=12)
        
        # Add tick marks and labels for different zones
        cbar.set_ticks([-0.4, -0.2, 0, 0.05, 0.3, 0.5])
        cbar.set_ticklabels(['< -0.4', '-0.2', '0', '0.05', '0.3', '> 0.5'])
        
        # Add explanatory text boxes for different zones
        explanations = [
            {'pos': (0.05, 0.20), 'text': 'Deep Red: Dry land, vegetation\n(NDWI < -0.2)', 'color': 'red'},
            {'pos': (0.05, 0.15), 'text': 'Light Red: Moist soil, wetlands\n(-0.2 < NDWI < 0)', 'color': 'lightcoral'},
            {'pos': (0.05, 0.10), 'text': 'Yellow/White: Transition zones\n(0 < NDWI < 0.05)', 'color': 'yellow'},
            {'pos': (0.05, 0.05), 'text': 'Light Blue: Shallow/turbid water\n(0.05 < NDWI < 0.3)', 'color': 'lightblue'},
            {'pos': (0.95, 0.05), 'text': 'Deep Blue: Clear water\n(NDWI > 0.3)', 'color': 'blue', 'ha': 'right'}
        ]
        
        for exp in explanations:
            ha = exp.get('ha', 'left')
            ax.text(exp['pos'][0], exp['pos'][1], exp['text'], 
                    transform=ax.transAxes, ha=ha, fontsize=10,
                    bbox=dict(facecolor='white', alpha=0.7, boxstyle='round', 
                              edgecolor=exp['color'], linewidth=2))
        
        # Add region coordinates and data source
        west, south, east, north = bbox_coords
        plt.suptitle(f'NDWI Analysis with Transition Zone Details - {source_name}\nRegion: [{west:.4f}, {south:.4f}, {east:.4f}, {north:.4f}]', 
                    fontsize=16)
        
        # Add a note about white/yellow transition zones
        transition_note = ("The white/yellow zones represent transition areas between water and land,\n"
                          "such as shorelines, wetlands, very shallow water, or water with high sediment content.\n"
                          "These areas have NDWI values close to zero and should NOT be confused with algal blooms.")
        plt.figtext(0.5, 0.01, transition_note, ha='center', fontsize=12, 
                    bbox={'facecolor': 'white', 'alpha': 0.7, 'pad': 5})
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        print(f"Saved detailed NDWI visualization to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error creating detailed NDWI visualization: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Main function to process water quality analysis"""
    args = parse_arguments()
    
    try:
        # Read config file
        with open(args.config, 'r') as f:
            config = json.load(f)
        
        # Extract parameters
        bbox_coords = config['bboxCoords']
        time_interval = config.get('timeInterval', ["2023-01-01", "2023-12-31"])
        data_source = config.get('dataSource', "sentinel2")
        
        print(f"Processing water quality analysis for bbox: {bbox_coords}")
        print(f"Time interval: {time_interval}")
        print(f"Data source: {data_source}")
        
        # Call Sentinel Hub to get water quality data
        results = get_sentinel_data(bbox_coords, time_interval, data_source=data_source, debug=args.debug)
        
        if results["success"]:
            # Create visualization
            viz_success, rgb_path = create_visualization(results, args.output, bbox_coords, data_source)
            
            # Create detailed NDWI visualization
            detailed_ndwi_path = args.output.replace('.png', '_detailed_ndwi.png')
            generate_detailed_ndwi_visualization(
                results["visualization"]["ndwi"], 
                detailed_ndwi_path, 
                bbox_coords,
                data_source
            )
            
            # Add the detailed visualization path to the results
            results["data"]["detailedNdwiPath"] = os.path.basename(detailed_ndwi_path)
            
            # Get the raw RGB image path
            if viz_success and rgb_path:
                rgb_filename = os.path.basename(rgb_path)
                results["data"]["rgbImagePath"] = rgb_filename
            
            # Save data to output file
            with open(args.data, 'w') as f:
                json.dump(results["data"], f)
            
            print("Water quality analysis completed successfully.")
            print(f"Results: {json.dumps(results['data'])}")
            sys.exit(0)
        else:
            print(f"Error in water quality analysis: {results['error']}", file=sys.stderr)
            
            # Fallback approach (if Sentinel Hub fails)
            # Create a meaningful error file for debugging
            fig = plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, f"Water Quality Analysis Error:\n\n{results['error']}", 
                     ha='center', va='center', fontsize=12,
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            plt.axis('off')
            plt.savefig(args.output, dpi=100, bbox_inches='tight')
            plt.close(fig)
            
            # Return minimal data
            fallback_data = {
                "waterCoverage": 0,
                "clearWater": 0,
                "moderateQuality": 0,
                "algalPresence": 0,
                "error": results["error"]
            }
            
            with open(args.data, 'w') as f:
                json.dump(fallback_data, f)
            
            sys.exit(1)
        
    except Exception as e:
        error_message = f"Error in water quality analysis: {str(e)}"
        print(error_message, file=sys.stderr)
        traceback.print_exc()
        
        # Create a meaningful error file
        fig = plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, f"Error processing water quality analysis:\n\n{str(e)}", 
                 ha='center', va='center', fontsize=12,
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        plt.axis('off')
        plt.savefig(args.output, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        # Return minimal data with error
        error_data = {
            "waterCoverage": 0,
            "clearWater": 0,
            "moderateQuality": 0,
            "algalPresence": 0,
            "error": str(e)
        }
        
        with open(args.data, 'w') as f:
            json.dump(error_data, f)
        
        sys.exit(1)

def run_demo():
    """Run a demo analysis with predefined parameters"""
    import tempfile
    import json
    from datetime import datetime
    import matplotlib.pyplot as plt
    from matplotlib.image import imread
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("\n" + "=" * 80)
    print(f"{'WATER QUALITY ANALYSIS DEMO':^80}")
    print("=" * 80)
    print(f"\nRun date: {now}")
    print("\nRunning demo analysis with predefined parameters...")
    
    # Demo parameters - San Francisco Bay
    demo_bbox = [-122.52, 37.70, -122.15, 37.90]
    demo_time_interval = ["2023-06-01", "2023-06-30"]
    demo_data_source = "sentinel2"  # Default to Sentinel-2
    
    # Check if a data source is specified as an argument
    if len(sys.argv) > 1 and sys.argv[1] in ["sentinel2", "landsat8", "modis"]:
        demo_data_source = sys.argv[1]
    
    print("\n" + "-" * 80)
    print(f"{'ANALYSIS PARAMETERS':^80}")
    print("-" * 80)
    print(f"{'Location':<20}: {'San Francisco Bay':<40}")
    print(f"{'Coordinates':<20}: {'West: ' + str(demo_bbox[0]):<20} {'East: ' + str(demo_bbox[2]):<20}")
    print(f"{'  ':<20}  {'South: ' + str(demo_bbox[1]):<20} {'North: ' + str(demo_bbox[3]):<20}")
    print(f"{'Time Interval':<20}: {'Start: ' + demo_time_interval[0]:<20} {'End: ' + demo_time_interval[1]:<20}")
    print(f"{'Data Source':<20}: {demo_data_source:<40}")
    
    # Create temp files for output
    demo_output_dir = os.path.join(os.getcwd(), "demo_output")
    os.makedirs(demo_output_dir, exist_ok=True)
    
    output_image = os.path.join(demo_output_dir, "demo_analysis.png")
    output_data = os.path.join(demo_output_dir, "demo_results.json")
    
    # Create a temp config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_file:
        json.dump({
            "bboxCoords": demo_bbox,
            "timeInterval": demo_time_interval,
            "dataSource": demo_data_source
        }, config_file)
        config_path = config_file.name
    
    try:
        print("\n" + "-" * 80)
        print(f"{'PROCESSING':^80}")
        print("-" * 80)
        print("\n[1/3] Initiating water quality analysis...")
        
        # Call Sentinel Hub to get water quality data
        print("[2/3] Retrieving and analyzing satellite data...")
        results = get_sentinel_data(demo_bbox, demo_time_interval, data_source=demo_data_source, debug=True)
        
        if results["success"]:
            # Create visualization
            print("[3/3] Creating visualizations...")
            viz_success, rgb_path = create_visualization(results, output_image, demo_bbox, demo_data_source)
            
            # Create detailed NDWI visualization
            detailed_ndwi_path = output_image.replace('.png', '_detailed_ndwi.png')
            generate_detailed_ndwi_visualization(
                results["visualization"]["ndwi"], 
                detailed_ndwi_path, 
                demo_bbox,
                demo_data_source
            )
            
            # Add the detailed visualization path to the results
            results["data"]["detailedNdwiPath"] = os.path.basename(detailed_ndwi_path)
            
            # Get the raw RGB image path
            if viz_success and rgb_path:
                rgb_filename = os.path.basename(rgb_path)
                results["data"]["rgbImagePath"] = rgb_filename
            
            # Save data to output file
            with open(output_data, 'w') as f:
                json.dump(results["data"], f, indent=2)
            
            print("\n" + "-" * 80)
            print(f"{'ANALYSIS RESULTS':^80}")
            print("-" * 80)
            
            # Water coverage section
            print(f"\n{'WATER COVERAGE':^80}")
            print(f"{'='*20:^80}")
            print(f"{'Water area':<30}: {results['data']['waterCoverage']:>6.1f}% of the region")
            print(f"{'Land area':<30}: {100 - results['data']['waterCoverage']:>6.1f}% of the region")
            
            # Water quality section
            if results['data']['waterCoverage'] > 0:
                print(f"\n{'WATER QUALITY METRICS':^80}")
                print(f"{'='*25:^80}")
                print(f"{'Clear water':<30}: {results['data']['clearWater']:>6.1f}% of water area")
                print(f"{'Moderate quality':<30}: {results['data']['moderateQuality']:>6.1f}% of water area")
                print(f"{'Potential algal presence':<30}: {results['data']['algalPresence']:>6.1f}% of water area")
                
                # Quality assessment
                print(f"\n{'WATER QUALITY ASSESSMENT':^80}")
                print(f"{'='*26:^80}")
                if results['data']['clearWater'] > 90:
                    quality_assessment = "Excellent - Very clear water dominates the region"
                elif results['data']['clearWater'] > 70:
                    quality_assessment = "Good - Mostly clear water with some moderate areas"
                elif results['data']['clearWater'] > 50:
                    quality_assessment = "Fair - Mix of clear and moderate quality water"
                elif results['data']['algalPresence'] > 20:
                    quality_assessment = "Poor - Significant algal presence detected"
                else:
                    quality_assessment = "Moderate - Water quality shows mixed signals"
                
                print(f"{'Overall assessment':<30}: {quality_assessment}")
            
            # Output files
            print("\n" + "-" * 80)
            print(f"{'OUTPUT FILES':^80}")
            print("-" * 80)
            print(f"{'Analysis visualization':<30}: {output_image}")
            if rgb_path:
                print(f"{'RGB satellite image':<30}: {rgb_path}")
            if 'detailedNdwiPath' in results['data']:
                print(f"{'Detailed NDWI visualization':<30}: {detailed_ndwi_path}")
            print(f"{'Results data (JSON)':<30}: {output_data}")
            
            # Add NDWI explanation section
            print("\n" + "-" * 80)
            print(f"{'NDWI VISUALIZATION EXPLANATION':^80}")
            print("-" * 80)
            print(f"Data source: {demo_data_source}")
            print("\nThe NDWI (Normalized Difference Water Index) visualization uses colors to represent different surfaces:")
            print(f"{'Deep blue':<20}: Clear, deep water (NDWI > 0.3)")
            print(f"{'Light blue':<20}: Water with some turbidity or shallow water (0.05 < NDWI < 0.3)")
            print(f"{'White/yellow':<20}: Transition zones, shorelines, very shallow water (0 < NDWI < 0.05)")
            print(f"{'Light red':<20}: Moist soil, wetlands, areas with high moisture (-0.2 < NDWI < 0)")
            print(f"{'Deep red':<20}: Dry land, built-up areas, vegetation (NDWI < -0.2)")
            
            print("\nThe white/yellow zones in your image represent transition areas such as:")
            print("- Shorelines or coastal boundaries")
            print("- Very shallow water areas")
            print("- Water with high sediment content")
            print("- Wetlands or partially submerged vegetation")
            print("- Mixed pixels containing both water and land")
            print("\nThese areas have NDWI values close to zero, making them appear as transition zones in the visualization.")
            print("For more accurate classification, refer to the detailed NDWI visualization.")
            
            # Create a combined display image
            combined_path = os.path.join(demo_output_dir, "demo_combined_view.png")
            try:
                # Create a figure for combined view - using 3 panels horizontally like the example
                fig, axes = plt.subplots(1, 3, figsize=(20, 6.5))
                
                # First show RGB image
                if rgb_path and os.path.exists(rgb_path):
                    try:
                        rgb_img = imread(rgb_path)
                        axes[0].imshow(rgb_img)
                        axes[0].set_title('True Color Image', fontsize=14)
                        axes[0].axis('off')
                    except Exception as rgb_err:
                        print(f"Warning: Error loading RGB image: {str(rgb_err)}")
                        axes[0].text(0.5, 0.5, "RGB image failed to load", 
                                   ha='center', va='center', transform=axes[0].transAxes)
                        axes[0].axis('off')
                
                # Show NDWI image in middle
                try:
                    if os.path.exists(output_image):
                        analysis_img = imread(output_image)
                        
                        # Extract the NDWI image from the analysis by cropping
                        # This assumes the standard 2-panel layout with NDWI on top
                        height, width, _ = analysis_img.shape
                        ndwi_img = analysis_img[:height//2, :, :]
                        
                        axes[1].imshow(ndwi_img)
                        axes[1].set_title('NDWI (Normalized Difference Water Index)', fontsize=14)
                        axes[1].axis('off')
                except Exception as ndwi_err:
                    print(f"Warning: Error extracting NDWI image: {str(ndwi_err)}")
                    axes[1].text(0.5, 0.5, "NDWI visualization failed to load", 
                               ha='center', va='center', transform=axes[1].transAxes)
                    axes[1].axis('off')
                
                # Show water classification in the third panel
                try:
                    if os.path.exists(output_image):
                        analysis_img = imread(output_image)
                        
                        # Extract the classification image from the analysis by cropping
                        # This assumes the standard 2-panel layout with classification on bottom
                        height, width, _ = analysis_img.shape
                        class_img = analysis_img[height//2:, :, :]
                        
                        axes[2].imshow(class_img)
                        axes[2].set_title('Water Quality Classification', fontsize=14)
                        axes[2].axis('off')
                except Exception as class_err:
                    print(f"Warning: Error extracting classification image: {str(class_err)}")
                    axes[2].text(0.5, 0.5, "Classification failed to load", 
                               ha='center', va='center', transform=axes[2].transAxes)
                    axes[2].axis('off')
                
                # Add overall title and statistics
                plt.suptitle(f'Water Quality Analysis for San Francisco Bay\nRegion: {demo_bbox}', fontsize=16)
                
                # Add water percentage text
                plt.figtext(0.5, 0.01, 
                          f"Water coverage: {results['data']['waterCoverage']:.1f}% of area | " +
                          f"Clear water: {results['data']['clearWater']:.1f}% | " +
                          f"Moderate quality: {results['data']['moderateQuality']:.1f}% | " +
                          f"Algal presence: {results['data']['algalPresence']:.1f}%", 
                          ha='center', fontsize=12, 
                          bbox={'facecolor': 'white', 'alpha': 0.7, 'pad': 5})
                
                plt.tight_layout(rect=[0, 0.05, 1, 0.95])
                plt.savefig(combined_path, dpi=150, bbox_inches='tight')
                plt.close(fig)
                print(f"{'Combined visualization':<30}: {combined_path}")
            except Exception as comb_err:
                print(f"Warning: Could not create combined visualization: {str(comb_err)}")
            
            # Display the images using matplotlib
            print("\n" + "-" * 80)
            print(f"{'DISPLAYING IMAGES':^80}")
            print("-" * 80)
            print("\nShowing analysis images. Close the image windows to continue...")
            
            # Check if we're in an interactive environment
            is_interactive = hasattr(plt, 'get_backend') and plt.get_backend().lower() != 'agg'
            
            if is_interactive:
                # First show the true color image if available
                if rgb_path and os.path.exists(rgb_path):
                    try:
                        rgb_img = imread(rgb_path)
                        plt.figure(figsize=(10, 8))
                        plt.imshow(rgb_img)
                        plt.title('True Color / Water Detection Visualization')
                        plt.axis('off')
                        plt.tight_layout()
                        plt.show(block=False)
                        print("Displayed true color image.")
                    except Exception as img_err:
                        print(f"Warning: Could not display true color image: {str(img_err)}")
                
                # Then show the analysis visualization
                if os.path.exists(output_image):
                    try:
                        analysis_img = imread(output_image)
                        plt.figure(figsize=(12, 10))
                        plt.imshow(analysis_img)
                        plt.title('Water Quality Analysis')
                        plt.axis('off')
                        plt.tight_layout()
                        plt.show()
                        print("Displayed analysis image.")
                    except Exception as img_err:
                        print(f"Warning: Could not display analysis image: {str(img_err)}")
            else:
                print("Not running in interactive mode. Images saved to files.")
                print(f"View the combined visualization at: {combined_path}")
            
        else:
            print("\n" + "-" * 80)
            print(f"{'ERROR':^80}")
            print("-" * 80)
            print(f"\n{results['error']}")
            sys.exit(1)
            
    except Exception as e:
        print("\n" + "-" * 80)
        print(f"{'ERROR':^80}")
        print("-" * 80)
        print(f"\n{str(e)}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up the temp config file
        if os.path.exists(config_path):
            os.unlink(config_path)
    
    print("\n" + "=" * 80)
    print(f"{'DEMO COMPLETED SUCCESSFULLY':^80}")
    print("=" * 80)

if __name__ == "__main__":
    import sys
    
    # Check if any arguments were provided
    if len(sys.argv) > 1:
        # Run with provided arguments
        main()
    else:
        # Run demo with predefined parameters
        run_demo()
