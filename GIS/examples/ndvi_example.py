import matplotlib.pyplot as plt
import numpy as np
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

# Set up authentication with the provided credentials
config = SHConfig()
config.sh_client_id = '6fc4acf0-cd2e-4097-b61d-5582083e0ab4'
config.sh_client_secret = 'B1d0KSm6A4VdD7WdDFb6B88y2TGpkPVv'

# Define the same area of interest (Barcelona, Spain)
bbox_coords = (2.0, 41.3, 2.3, 41.5)
bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)

# Define resolution and image dimensions
resolution = 20  # in meters
size = bbox_to_dimensions(bbox, resolution=resolution)

print(f"Image dimensions: {size}")

# Option 1: Calculate NDVI directly in the evalscript (returns a color-coded NDVI image)
evalscript_ndvi_colored = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08"],
    output: { bands: 3 }
  };
}

function evaluatePixel(sample) {
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  
  // Color scheme: blue (water) -> red (soil/urban) -> green (vegetation)
  // Values typically range from -1 to 1 for NDVI
  
  if (ndvi < -0.2) return [0.0, 0.0, 0.5]; // Water - blue
  if (ndvi < 0.2) return [0.9, 0.1, 0.1];  // Urban/soil - red
  if (ndvi < 0.4) return [0.4, 0.9, 0.1];  // Light vegetation - light green
  return [0.0, 0.7, 0.0];                  // Dense vegetation - dark green
}
"""

# Option 2: Get raw NDVI values for more precise analysis
evalscript_ndvi_raw = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08"],
    output: {
      bands: 1,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  return [ndvi];
}
"""

# Create requests for both options
request_ndvi_colored = SentinelHubRequest(
    evalscript=evalscript_ndvi_colored,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=("2023-06-01", "2023-06-30"),
            mosaicking_order=MosaickingOrder.LEAST_CC
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
    bbox=bbox,
    size=size,
    config=config,
)

request_ndvi_raw = SentinelHubRequest(
    evalscript=evalscript_ndvi_raw,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=("2023-06-01", "2023-06-30"),
            mosaicking_order=MosaickingOrder.LEAST_CC
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox,
    size=size,
    config=config,
)

print("Sending requests to Sentinel Hub...")

try:
    # Get the data for both
    ndvi_colored = request_ndvi_colored.get_data()[0]
    ndvi_raw = request_ndvi_raw.get_data()[0]
    
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Display color-coded NDVI
    ax1.imshow(ndvi_colored)
    ax1.set_title('Color-coded NDVI Classification')
    ax1.axis('off')
    
    # Display raw NDVI with a color map
    im = ax2.imshow(ndvi_raw, cmap='RdYlGn', vmin=-0.2, vmax=0.8)
    ax2.set_title('NDVI Values')
    ax2.axis('off')
    
    # Add a colorbar
    cbar = fig.colorbar(im, ax=ax2, orientation='vertical', fraction=0.046, pad=0.04)
    cbar.set_label('NDVI Value')
    
    # Add a legend for the color-coded image
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    
    legend_elements = [
        Patch(facecolor=(0.0, 0.0, 0.5), label='Water (NDVI < -0.2)'),
        Patch(facecolor=(0.9, 0.1, 0.1), label='Urban/Soil (NDVI < 0.2)'),
        Patch(facecolor=(0.4, 0.9, 0.1), label='Light Vegetation (NDVI < 0.4)'),
        Patch(facecolor=(0.0, 0.7, 0.0), label='Dense Vegetation (NDVI ≥ 0.4)')
    ]
    
    ax1.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.0, 0.0), 
               bbox_transform=fig.transFigure, ncol=4, frameon=False)
    
    plt.suptitle('NDVI Analysis of Barcelona (June 2023)', fontsize=16)
    plt.tight_layout()
    plt.savefig('barcelona_ndvi.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("NDVI analysis completed and saved as 'barcelona_ndvi.png'")
    
except Exception as e:
    print(f"Error retrieving data: {e}") 