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

# Define an area of interest (example: Barcelona, Spain)
bbox_coords = (2.0, 41.3, 2.3, 41.5)
bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)

# Define resolution and image dimensions
resolution = 20  # in meters
size = bbox_to_dimensions(bbox, resolution=resolution)

print(f"Image dimensions: {size}")

# Create an evalscript for true color imagery
evalscript = """
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

# Create the request
request = SentinelHubRequest(
    evalscript=evalscript,
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

print("Sending request to Sentinel Hub...")

try:
    # Get the data
    image = request.get_data()[0]  # Returns a list, with a single image in this case
    
    # Display the image
    plt.figure(figsize=(10, 10))
    plt.axis('off')
    plt.title('Sentinel-2 True Color Image (Barcelona, June 2023)')
    plt.imshow(image)
    plt.savefig('barcelona_true_color.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Image successfully retrieved and saved as 'barcelona_true_color.png'")
    
except Exception as e:
    print(f"Error retrieving data: {e}") 