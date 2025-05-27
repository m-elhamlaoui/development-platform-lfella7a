# Sentinel Hub Python Examples

This folder contains Python scripts demonstrating how to interact with the Sentinel Hub Process API using the `sentinelhub-py` package. These examples show how to retrieve and analyze satellite imagery for various applications.

## Prerequisites

To run these examples, you need:

1. Python 3.6 or higher
2. The following Python packages:
   - sentinelhub
   - matplotlib
   - numpy

Install them using pip:
```bash
pip install sentinelhub matplotlib numpy
```

3. Sentinel Hub credentials (Client ID and Client Secret)

## Examples

### 1. True Color Image Retrieval (sentinel_example.py)

This script demonstrates how to:
- Authenticate with Sentinel Hub
- Define an area of interest
- Create a request for a true color image
- Retrieve and display the image

The script creates a true color image of Barcelona using RGB bands (B04, B03, B02) from Sentinel-2 imagery.

### 2. Vegetation Analysis (ndvi_example.py)

This script demonstrates the calculation of NDVI (Normalized Difference Vegetation Index), which is used to assess vegetation health and density. It shows:
- How to create an evalscript for NDVI calculation
- Different approaches for visualizing NDVI (color-coded classification and continuous color mapping)
- Creating multi-panel visualizations with matplotlib

### 3. Water Detection (water_detection.py)

This script demonstrates water body detection using NDWI (Normalized Difference Water Index). It shows:
- How to calculate NDWI using Green (B03) and NIR (B08) bands
- Applying thresholds to create a water mask
- Calculating statistics (water coverage percentage)
- Creating a three-panel visualization showing true color image, NDWI values, and water detection

## Output Images

Each script generates a high-resolution PNG image with its visualization results:

- `barcelona_true_color.png` - Sentinel-2 true color image of Barcelona
- `barcelona_ndvi.png` - NDVI analysis showing vegetation density
- `barcelona_water_detection.png` - Water detection using NDWI

## Adapting for Your Area of Interest

To adapt these scripts for your own area:

1. Replace the bbox_coords with your area's coordinates: (min_x, min_y, max_x, max_y) in WGS84
2. Adjust the time_interval in the request to get imagery from your desired date range
3. Modify the resolution parameter to change the output resolution (in meters)
4. Customize the evalscripts as needed for your specific analysis 