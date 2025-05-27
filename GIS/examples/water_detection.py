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

# Define an area of interest (Barcelona with more of the coastline)
bbox_coords = (2.0, 41.25, 2.35, 41.5)
bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)

# Define resolution and image dimensions
resolution = 20  # in meters
size = bbox_to_dimensions(bbox, resolution=resolution)

print(f"Image dimensions: {size}")

# True color image for reference
evalscript_true_color = """
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
"""

# NDWI calculation (using GREEN and NIR bands)
evalscript_ndwi = """
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
"""

# Water detection with visualization
evalscript_water_detection = """
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
  
  // Create a water mask (NDWI > 0.2 typically indicates water)
  if (ndwi > 0.2) {
    // Blue for water
    return [0.0, 0.0, 0.8];
  } else {
    // Use a semi-transparent true color for land
    return [0.7*sample.B04, 0.7*sample.B03, 0.7*sample.B02];
  }
}
"""

# Create requests
request_true_color = SentinelHubRequest(
    evalscript=evalscript_true_color,
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

request_ndwi = SentinelHubRequest(
    evalscript=evalscript_ndwi,
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

request_water_detection = SentinelHubRequest(
    evalscript=evalscript_water_detection,
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

print("Sending requests to Sentinel Hub...")

try:
    # Get the data
    true_color = request_true_color.get_data()[0]
    ndwi = request_ndwi.get_data()[0]
    water_detection = request_water_detection.get_data()[0]
    
    # Create a figure with three subplots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
    
    # Display true color image
    ax1.imshow(true_color)
    ax1.set_title('True Color Image')
    ax1.axis('off')
    
    # Display NDWI
    im2 = ax2.imshow(ndwi, cmap='RdYlBu', vmin=-0.5, vmax=0.5)
    ax2.set_title('NDWI (Normalized Difference Water Index)')
    ax2.axis('off')
    cbar = fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
    cbar.set_label('NDWI Value')
    
    # Display water detection
    ax3.imshow(water_detection)
    ax3.set_title('Water Detection (NDWI > 0.2)')
    ax3.axis('off')
    
    # Calculate some statistics
    water_pixels = np.sum(ndwi > 0.2)
    total_pixels = ndwi.size
    water_percentage = (water_pixels / total_pixels) * 100
    
    # Add water percentage text
    plt.figtext(0.5, 0.01, f"Water coverage: {water_percentage:.2f}% of the area", 
                ha='center', fontsize=12, 
                bbox={'facecolor': 'white', 'alpha': 0.7, 'pad': 5})
    
    plt.suptitle('Water Detection in Barcelona Using NDWI (June 2023)', fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('barcelona_water_detection.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Water detection analysis completed and saved as 'barcelona_water_detection.png'")
    print(f"Water coverage: {water_percentage:.2f}% of the area")
    
except Exception as e:
    print(f"Error retrieving data: {e}") 