# Using Sentinel Hub with Python

This guide shows how to work with Sentinel Hub services using Python, with a primary focus on the official `sentinelhub-py` package.

## Getting Started with sentinelhub-py

### Installation

The `sentinelhub-py` package can be installed using pip:

```bash
pip install sentinelhub
```

It's recommended to use a virtual environment (venv, conda, etc.) to avoid dependency conflicts.

### Setting Up Authentication

Create a configuration file with your Sentinel Hub credentials:

```python
from sentinelhub import SHConfig

config = SHConfig()

# Set your OAuth client credentials
config.sh_client_id = 'YOUR-CLIENT-ID'
config.sh_client_secret = 'YOUR-CLIENT-SECRET'

# Save the configuration for future use (optional)
config.save()
```

Once saved, this configuration can be loaded in future sessions:

```python
from sentinelhub import SHConfig

config = SHConfig()
# If you've previously saved the configuration, it will be loaded automatically
```

## Using the Process API

### Basic Example: Fetching a True Color Image

```python
import matplotlib.pyplot as plt
from sentinelhub import (
    CRS,
    BBox,
    DataCollection,
    MimeType,
    MosaickingOrder,
    SentinelHubRequest,
    bbox_to_dimensions,
)

# Define the area of interest (Luxembourg)
bbox_coords = (5.65, 49.55, 6.35, 50.05)
bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)

# Define resolution and image dimensions
resolution = 20  # in meters
size = bbox_to_dimensions(bbox, resolution=resolution)

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
            time_interval=("2020-06-01", "2020-06-30"),
            mosaicking_order=MosaickingOrder.LEAST_CC
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
    bbox=bbox,
    size=size,
    config=config,
)

# Get the data
image = request.get_data()[0]  # Returns a list, with a single image in this case

# Display the image
plt.figure(figsize=(10, 10))
plt.axis('off')
plt.imshow(image)
plt.show()
```

### Working with Multiple Bands and Raw Data

For scientific analysis, you often need the raw band values rather than a visual representation:

```python
# Define evalscript for multiple bands in raw format
evalscript_raw = """
//VERSION=3
function setup() {
  return {
    input: ["B02", "B03", "B04", "B08"],
    output: {
      bands: 4,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  return [sample.B02, sample.B03, sample.B04, sample.B08];
}
"""

# Create the request with TIFF output format for raw data
request_raw = SentinelHubRequest(
    evalscript=evalscript_raw,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=("2020-06-01", "2020-06-30"),
            mosaicking_order=MosaickingOrder.LEAST_CC
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox,
    size=size,
    config=config,
)

# Get the raw data
bands = request_raw.get_data()[0]

# Now you can work with individual bands:
blue_band = bands[:, :, 0]    # B02
green_band = bands[:, :, 1]   # B03
red_band = bands[:, :, 2]     # B04
nir_band = bands[:, :, 3]     # B08

# Calculate NDVI
ndvi = (nir_band - red_band) / (nir_band + red_band)

# Display NDVI
plt.figure(figsize=(10, 10))
plt.axis('off')
plt.imshow(ndvi, cmap='RdYlGn', vmin=-1, vmax=1)
plt.colorbar(label='NDVI')
plt.title('NDVI Map')
plt.show()
```

### Downloading Data for Multiple Timestamps

```python
import datetime
import numpy as np

# Define time range and create time intervals
start_date = datetime.datetime(2020, 5, 1)
end_date = datetime.datetime(2020, 8, 1)
n_intervals = 4  # Monthly intervals

delta = (end_date - start_date) / n_intervals
time_intervals = []

for i in range(n_intervals):
    interval_start = start_date + i * delta
    interval_end = start_date + (i + 1) * delta
    time_intervals.append((interval_start.strftime("%Y-%m-%d"), interval_end.strftime("%Y-%m-%d")))

# Create a request for each interval
requests = []
for interval in time_intervals:
    request = SentinelHubRequest(
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=interval,
                mosaicking_order=MosaickingOrder.LEAST_CC
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
        bbox=bbox,
        size=size,
        config=config,
    )
    requests.append(request)

# Download all images
images = []
for request in requests:
    images.append(request.get_data()[0])

# Display all images in a grid
fig, axes = plt.subplots(2, 2, figsize=(16, 16))
for idx, (ax, image, interval) in enumerate(zip(axes.flatten(), images, time_intervals)):
    ax.imshow(image)
    ax.set_title(f"{interval[0]} to {interval[1]}")
    ax.axis('off')
plt.tight_layout()
plt.show()
```

## Using the Catalog API

The Catalog API allows you to search for available satellite imagery before making Process API requests:

```python
from sentinelhub import SentinelHubCatalog, MimeType, CRS, BBox

catalog = SentinelHubCatalog(config=config)

# Search for available Sentinel-2 L2A data
bbox_coords = (5.65, 49.55, 6.35, 50.05)  # Luxembourg
bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)

search_iterator = catalog.search(
    collection=DataCollection.SENTINEL2_L2A,
    bbox=bbox,
    time=("2020-06-01", "2020-06-30"),
    fields={
        "include": [
            "id",
            "properties.datetime",
            "properties.eo:cloud_cover"
        ]
    },
    query={
        "eo:cloud_cover": {
            "lt": 20  # Less than 20% cloud coverage
        }
    }
)

# Print the results
results = list(search_iterator)
print(f"Found {len(results)} scenes:")

for item in results:
    print(f"ID: {item['id']}")
    print(f"Date: {item['properties']['datetime']}")
    print(f"Cloud cover: {item['properties']['eo:cloud_cover']}%")
    print("-" * 50)
```

## Working with Large Areas (eo-learn)

For processing large areas or time series, the `eo-learn` package built on top of `sentinelhub-py` is recommended:

```bash
pip install eo-learn
```

Basic example of using eo-learn:

```python
from eolearn.core import EOPatch, FeatureType
from eolearn.io import SentinelHubInputTask
from sentinelhub import CRS, BBox, DataCollection

# Define the area and time range
bbox = BBox((5.65, 49.55, 6.35, 50.05), crs=CRS.WGS84)
time_interval = ("2020-06-01", "2020-06-30")

# Define the input task
input_task = SentinelHubInputTask(
    data_collection=DataCollection.SENTINEL2_L2A,
    bands=['B02', 'B03', 'B04', 'B08'],
    bands_feature=(FeatureType.DATA, 'BANDS'),
    resolution=20,
    maxcc=0.8,
    time_difference=datetime.timedelta(hours=2),
    config=config,
    max_threads=5
)

# Execute the task
eop = input_task.execute(bbox=bbox, time_interval=time_interval)

# Now you can work with the EOPatch
print(f"EOPatch contains {len(eop.timestamp)} timestamps")
print(f"Band data shape: {eop.data['BANDS'].shape}")  # (time, height, width, bands)

# Extract single time frame
rgb_data = eop.data['BANDS'][0, :, :, [2, 1, 0]]  # RGB for the first timestamp

# Visualize
plt.figure(figsize=(10, 10))
plt.imshow(np.clip(rgb_data * 3.5, 0, 1))  # Scale for better visualization
plt.axis('off')
plt.show()
```

## Error Handling

It's important to implement proper error handling when working with API requests:

```python
from sentinelhub.exceptions import SentinelHubException
import time

def get_image_with_retry(request, max_retries=3, delay=5):
    """Attempt to get data with retries for common errors"""
    for attempt in range(max_retries):
        try:
            return request.get_data()
        except SentinelHubException as e:
            if "401" in str(e) and attempt < max_retries - 1:
                print(f"Authentication error, refreshing token and retrying... (attempt {attempt+1})")
                # You might need to refresh your token here
                time.sleep(delay)
            elif "429" in str(e) and attempt < max_retries - 1:
                print(f"Rate limit exceeded, waiting and retrying... (attempt {attempt+1})")
                time.sleep(delay * (attempt + 1))  # Exponential backoff
            elif "500" in str(e) and attempt < max_retries - 1:
                print(f"Server error, retrying... (attempt {attempt+1})")
                time.sleep(delay)
            else:
                raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    
    raise Exception(f"Failed after {max_retries} attempts")
```

## Best Practices for Python Integration

1. **Manage Authentication Properly**
   - Store credentials securely, never hardcode them
   - Handle token refreshing when needed

2. **Optimize Data Requests**
   - Only request the bands you need
   - Use appropriate spatial and temporal resolution
   - Consider using Statistical API for large-scale analysis

3. **Parallelize Processing**
   - Use the `max_threads` parameter in SentinelHubDownloadClient for multiple requests
   - Consider using batch processing for large areas

4. **Cache Results**
   - Use the `data_folder` parameter to cache results locally
   - Implement your own caching for derived products

5. **Handle Errors Gracefully**
   - Implement retries with exponential backoff
   - Check data availability before making large requests

## Advanced Use Cases

For more advanced use cases and examples, check out:

- [eo-learn documentation](https://eo-learn.readthedocs.io/)
- [Sentinel Hub GitHub examples](https://github.com/sentinel-hub/sentinelhub-py/tree/master/examples)
- [Custom scripts repository](https://github.com/sentinel-hub/custom-scripts)

## Next Steps

Check out our [Example Use Cases](example-use-cases.md) for more real-world applications of the Sentinel Hub Process API with Python. 