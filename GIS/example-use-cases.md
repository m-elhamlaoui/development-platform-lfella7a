# Example Use Cases for Sentinel Hub Process API

This document demonstrates practical applications of the Sentinel Hub Process API through real-world examples.

## 1. Land Cover Classification

Land cover classification is a common application of satellite imagery, useful for environmental monitoring, urban planning, and agricultural management.

### Example: Basic Land Cover Classification Using NDVI Thresholds

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sentinelhub import (
    CRS, BBox, DataCollection, MimeType, SentinelHubRequest, bbox_to_dimensions, SHConfig
)

# Set up authentication
config = SHConfig()
config.sh_client_id = 'YOUR-CLIENT-ID'
config.sh_client_secret = 'YOUR-CLIENT-SECRET'

# Define area of interest (example: part of California's Central Valley)
bbox_coords = (-121.2, 36.8, -120.8, 37.2)
bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)
resolution = 30
size = bbox_to_dimensions(bbox, resolution=resolution)

# Evalscript to get bands needed for classification
evalscript = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08", "B11", "B12", "SCL"],
    output: {
      bands: 5,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  return [sample.B04, sample.B08, sample.B11, sample.B12, sample.SCL];
}
"""

# Create request
request = SentinelHubRequest(
    evalscript=evalscript,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=("2022-07-01", "2022-07-31")
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox,
    size=size,
    config=config,
)

# Get data
data = request.get_data()[0]

# Extract bands
red = data[:, :, 0]
nir = data[:, :, 1]
swir1 = data[:, :, 2]
swir2 = data[:, :, 3]
scl = data[:, :, 4]  # Scene Classification Layer

# Calculate indices
ndvi = (nir - red) / (nir + red)
ndwi = (nir - swir1) / (nir + swir1)

# Simple classification
land_cover = np.zeros_like(ndvi, dtype=np.uint8)
land_cover[(ndvi > 0.5)] = 1                    # Dense vegetation
land_cover[(ndvi > 0.2) & (ndvi <= 0.5)] = 2    # Sparse vegetation
land_cover[(ndvi <= 0.2) & (ndvi > 0)] = 3      # Soil/Urban
land_cover[(ndwi > 0.3)] = 4                    # Water
land_cover[(scl == 3) | (scl == 8) | (scl == 9)] = 5  # Cloud/Cloud shadow

# Visualization
colors = ['black', 'darkgreen', 'lightgreen', 'burlywood', 'blue', 'white']
cmap = ListedColormap(colors)

plt.figure(figsize=(12, 12))
plt.imshow(land_cover, cmap=cmap)
plt.colorbar(ticks=[0, 1, 2, 3, 4, 5], 
             label='Land Cover Classes')
plt.title('Simple Land Cover Classification')
plt.tight_layout()

# Create legend patches
from matplotlib.patches import Patch
legend_labels = {
    0: 'No Data', 
    1: 'Dense Vegetation', 
    2: 'Sparse Vegetation',
    3: 'Soil/Urban', 
    4: 'Water', 
    5: 'Cloud/Cloud Shadow'
}
patches = [Patch(color=colors[i], label=legend_labels[i]) for i in range(len(colors))]
plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left')

plt.savefig('land_cover_classification.png', dpi=300, bbox_inches='tight')
plt.show()
```

## 2. Change Detection

Detecting changes over time is crucial for monitoring deforestation, urban growth, disaster impacts, and more.

### Example: Forest Fire Scar Analysis

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from sentinelhub import (
    CRS, BBox, DataCollection, MimeType, SentinelHubRequest, bbox_to_dimensions, SHConfig
)

# Set up authentication
config = SHConfig()
config.sh_client_id = 'YOUR-CLIENT-ID'
config.sh_client_secret = 'YOUR-CLIENT-SECRET'

# Define area of interest (example: 2021 Caldor Fire area, California)
bbox_coords = (-120.5, 38.7, -120.0, 39.0)
bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)
resolution = 20
size = bbox_to_dimensions(bbox, resolution=resolution)

# Evalscript for NBR (Normalized Burn Ratio)
evalscript_nbr = """
//VERSION=3
function setup() {
  return {
    input: ["B8A", "B12"],
    output: {
      bands: 1,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  // Normalized Burn Ratio
  let nbr = (sample.B8A - sample.B12) / (sample.B8A + sample.B12);
  return [nbr];
}
"""

# Request for pre-fire (July 2021) and post-fire (September 2021) imagery
request_pre = SentinelHubRequest(
    evalscript=evalscript_nbr,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=("2021-07-01", "2021-07-15")
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox,
    size=size,
    config=config,
)

request_post = SentinelHubRequest(
    evalscript=evalscript_nbr,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=("2021-09-15", "2021-09-30")
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox,
    size=size,
    config=config,
)

# Get data
nbr_pre = request_pre.get_data()[0][:, :, 0]
nbr_post = request_post.get_data()[0][:, :, 0]

# Calculate dNBR (delta NBR)
dnbr = nbr_pre - nbr_post

# Request for RGB visualization
evalscript_rgb = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B03", "B02"],
    output: { bands: 3 }
  };
}

function evaluatePixel(sample) {
  return [2.5*sample.B04, 2.5*sample.B03, 2.5*sample.B02];
}
"""

request_rgb_post = SentinelHubRequest(
    evalscript=evalscript_rgb,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=("2021-09-15", "2021-09-30")
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
    bbox=bbox,
    size=size,
    config=config,
)

rgb_post = request_rgb_post.get_data()[0]

# Visualization
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Pre-fire NBR
axes[0].imshow(nbr_pre, cmap='YlGn', vmin=-0.5, vmax=0.9)
axes[0].set_title('Pre-fire NBR (July 2021)')
axes[0].axis('off')

# Post-fire RGB
axes[1].imshow(rgb_post / 255.0)  # Normalize to [0, 1]
axes[1].set_title('Post-fire RGB (September 2021)')
axes[1].axis('off')

# dNBR with custom colormap for burn severity
# Create a custom colormap for burn severity
colors = [(0.0, 'blue'),  # Negative values: regrowth
          (0.25, 'green'),
          (0.4, 'yellow'),
          (0.6, 'orange'),
          (0.8, 'red'),
          (1.0, 'darkred')]

cmap_name = 'burn_severity'
cm = LinearSegmentedColormap.from_list(cmap_name, colors)

# Display dNBR
im = axes[2].imshow(dnbr, cmap=cm, vmin=-0.5, vmax=1.0)
axes[2].set_title('dNBR (Burn Severity)')
axes[2].axis('off')

# Add colorbar
cbar = fig.colorbar(im, ax=axes[2], fraction=0.046, pad=0.04)
cbar.set_label('Burn Severity')
cbar.set_ticks([-0.5, 0.0, 0.1, 0.27, 0.44, 0.66, 1.0])
cbar.set_ticklabels(['Regrowth', 'Unburned', 'Low', 'Moderate-Low', 'Moderate-High', 'High', 'Extreme'])

plt.tight_layout()
plt.savefig('fire_analysis.png', dpi=300, bbox_inches='tight')
plt.show()
```

## 3. Agricultural Monitoring

Satellite imagery is widely used in precision agriculture for crop health monitoring, yield estimation, and irrigation management.

### Example: Multi-temporal NDVI Analysis for Crop Growth Monitoring

```python
import matplotlib.pyplot as plt
import numpy as np
import datetime
from matplotlib.dates import DateFormatter
from sentinelhub import (
    CRS, BBox, DataCollection, MimeType, SentinelHubRequest, 
    bbox_to_dimensions, MosaickingOrder, SHConfig
)

# Set up authentication
config = SHConfig()
config.sh_client_id = 'YOUR-CLIENT-ID'
config.sh_client_secret = 'YOUR-CLIENT-SECRET'

# Define area of interest (example: agricultural field)
bbox_coords = (-93.52, 41.85, -93.47, 41.90)  # Example coordinates for Iowa farmland
bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)
resolution = 10
size = bbox_to_dimensions(bbox, resolution=resolution)

# Evalscript to calculate NDVI
evalscript_ndvi = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08", "dataMask"],
    output: {
      bands: 2,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  return [ndvi, sample.dataMask];
}
"""

# Define time intervals for one growing season (April to October 2022)
start_date = datetime.datetime(2022, 4, 1)
end_date = datetime.datetime(2022, 10, 31)
dates = []
ndvi_means = []
ndvi_stds = []

# Request NDVI data for each month
current_date = start_date
while current_date < end_date:
    next_date = current_date + datetime.timedelta(days=30)
    
    time_interval = (current_date.strftime("%Y-%m-%d"), next_date.strftime("%Y-%m-%d"))
    dates.append(current_date + datetime.timedelta(days=15))  # Middle of interval for plotting
    
    request_ndvi = SentinelHubRequest(
        evalscript=evalscript_ndvi,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=time_interval,
                mosaicking_order=MosaickingOrder.LEAST_CC
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=bbox,
        size=size,
        config=config,
    )
    
    try:
        data = request_ndvi.get_data()[0]
        ndvi = data[:, :, 0]
        mask = data[:, :, 1]
        
        # Calculate statistics for valid pixels
        valid_pixels = ndvi[mask == 1]
        if len(valid_pixels) > 0:
            ndvi_means.append(np.mean(valid_pixels))
            ndvi_stds.append(np.std(valid_pixels))
        else:
            ndvi_means.append(np.nan)
            ndvi_stds.append(np.nan)
    except Exception as e:
        print(f"Error for time interval {time_interval}: {e}")
        ndvi_means.append(np.nan)
        ndvi_stds.append(np.nan)
    
    current_date = next_date

# Get a single RGB image for reference
evalscript_rgb = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B03", "B02"],
    output: { bands: 3 }
  };
}

function evaluatePixel(sample) {
  return [2.5*sample.B04, 2.5*sample.B03, 2.5*sample.B02];
}
"""

request_rgb = SentinelHubRequest(
    evalscript=evalscript_rgb,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=("2022-07-01", "2022-07-31"),
            mosaicking_order=MosaickingOrder.LEAST_CC
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
    bbox=bbox,
    size=size,
    config=config,
)

rgb = request_rgb.get_data()[0]

# Visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={'width_ratios': [2, 1]})

# Plot NDVI time series
ax1.errorbar(dates, ndvi_means, yerr=ndvi_stds, fmt='o-', capsize=5, linewidth=2)
ax1.set_ylabel('NDVI')
ax1.set_xlabel('Date')
ax1.set_ylim(0, 1)
ax1.set_title('Crop Growth Cycle (NDVI)')
ax1.grid(True, linestyle='--', alpha=0.7)
date_formatter = DateFormatter('%b %d')
ax1.xaxis.set_major_formatter(date_formatter)
fig.autofmt_xdate()

# Annotate growth stages
growth_stages = [
    (datetime.datetime(2022, 5, 15), 'Emergence'),
    (datetime.datetime(2022, 7, 15), 'Peak Growth'),
    (datetime.datetime(2022, 9, 15), 'Senescence')
]

for date, label in growth_stages:
    nearest_idx = np.argmin([abs((d - date).total_seconds()) for d in dates])
    ax1.annotate(label, 
                 xy=(dates[nearest_idx], ndvi_means[nearest_idx]),
                 xytext=(0, 20),
                 textcoords='offset points',
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=.2'),
                 ha='center')

# Plot RGB image
ax2.imshow(rgb / 255.0)  # Normalize to [0, 1]
ax2.set_title('RGB Image (July 2022)')
ax2.axis('off')

plt.tight_layout()
plt.savefig('crop_monitoring.png', dpi=300, bbox_inches='tight')
plt.show()
```

## 4. Water Quality Monitoring

Sentinel-2 data can be used to assess water quality parameters such as turbidity, chlorophyll content, and harmful algal blooms.

### Example: Detecting Algal Blooms in Lakes

```python
import numpy as np
import matplotlib.pyplot as plt
from sentinelhub import (
    CRS, BBox, DataCollection, MimeType, SentinelHubRequest, bbox_to_dimensions, SHConfig
)

# Set up authentication
config = SHConfig()
config.sh_client_id = 'YOUR-CLIENT-ID'
config.sh_client_secret = 'YOUR-CLIENT-SECRET'

# Define area of interest (example: Lake Erie with harmful algal bloom)
bbox_coords = (-83.5, 41.6, -82.7, 42.0)
bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)
resolution = 60
size = bbox_to_dimensions(bbox, resolution=resolution)

# Evalscript for chlorophyll and turbidity indices
evalscript = """
//VERSION=3
function setup() {
  return {
    input: ["B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B11", "B12", "dataMask"],
    output: {
      bands: 5,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  // Normalized Difference Chlorophyll Index (B5-B4)/(B5+B4)
  let ndci = (sample.B05 - sample.B04) / (sample.B05 + sample.B04);
  
  // Maximum Chlorophyll Index (B5/B4)
  let mci = sample.B05 / sample.B04 - 1;
  
  // Floating Algae Index (B8-B5)/(B8+B5)
  let fai = (sample.B08 - sample.B05) / (sample.B08 + sample.B05);
  
  // Simple RGB for visualization (scaled for visibility)
  let rgb = [sample.B04, sample.B03, sample.B02];
  
  return [ndci, mci, fai, ...rgb];
}
"""

# Request data during algal bloom season (August 2019)
request = SentinelHubRequest(
    evalscript=evalscript,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=("2019-08-01", "2019-08-15")
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox,
    size=size,
    config=config,
)

# Get data
data = request.get_data()[0]

# Extract indices and RGB
ndci = data[:, :, 0]
mci = data[:, :, 1]
fai = data[:, :, 2]
rgb = data[:, :, 3:6]

# Create land/water mask (simple threshold on red band)
water_mask = rgb[:, :, 0] < 0.1  # Low red reflectance typically indicates water

# Apply water mask to indices
ndci_masked = np.where(water_mask, ndci, np.nan)
mci_masked = np.where(water_mask, mci, np.nan)
fai_masked = np.where(water_mask, fai, np.nan)

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# RGB
axes[0, 0].imshow(np.clip(rgb * 3.5, 0, 1))  # Enhance brightness
axes[0, 0].set_title('RGB Image')
axes[0, 0].axis('off')

# NDCI
im1 = axes[0, 1].imshow(ndci_masked, cmap='RdYlGn', vmin=-0.1, vmax=0.3)
axes[0, 1].set_title('NDCI (Chlorophyll)')
axes[0, 1].axis('off')
fig.colorbar(im1, ax=axes[0, 1], fraction=0.046, pad=0.04)

# MCI
im2 = axes[1, 0].imshow(mci_masked, cmap='RdYlGn', vmin=0, vmax=0.5)
axes[1, 0].set_title('MCI (Maximum Chlorophyll Index)')
axes[1, 0].axis('off')
fig.colorbar(im2, ax=axes[1, 0], fraction=0.046, pad=0.04)

# FAI
im3 = axes[1, 1].imshow(fai_masked, cmap='RdYlGn_r', vmin=-0.1, vmax=0.1)
axes[1, 1].set_title('FAI (Floating Algae Index)')
axes[1, 1].axis('off')
fig.colorbar(im3, ax=axes[1, 1], fraction=0.046, pad=0.04)

plt.suptitle('Lake Erie Algal Bloom Analysis - August 2019', fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('algal_bloom_analysis.png', dpi=300, bbox_inches='tight')
plt.show()
```

## 5. Urban Monitoring and Development

Satellite imagery can track urban expansion, monitor construction activities, and assess heat island effects.

### Example: Urban Heat Island Effect Analysis

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from sentinelhub import (
    CRS, BBox, DataCollection, MimeType, SentinelHubRequest, bbox_to_dimensions, SHConfig
)

# Set up authentication
config = SHConfig()
config.sh_client_id = 'YOUR-CLIENT-ID'
config.sh_client_secret = 'YOUR-CLIENT-SECRET'

# Define area of interest (example: Phoenix, AZ metro area)
bbox_coords = (-112.1, 33.4, -111.9, 33.6)
bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)
resolution = 60
size = bbox_to_dimensions(bbox, resolution=resolution)

# Evalscript for Landsat 8 Land Surface Temperature and NDVI
evalscript = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B05", "B10", "dataMask"],
    output: {
      bands: 4,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  // Calculate NDVI
  let ndvi = (sample.B05 - sample.B04) / (sample.B05 + sample.B04);
  
  // Convert Landsat thermal band to brightness temperature in Celsius
  // This is a simplified conversion
  let bt = sample.B10 * 0.1 - 273.15;
  
  // Create a simple RGB for visualization
  let r = sample.B04 * 3.5;
  let g = sample.B05 * 3.5;
  let b = 0.5 * (r + g);
  
  return [bt, ndvi, sample.dataMask, r];
}
"""

# Request data for summer (high heat)
request = SentinelHubRequest(
    evalscript=evalscript,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.LANDSAT_OT_L2,
            time_interval=("2022-07-01", "2022-07-31")
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox,
    size=size,
    config=config,
)

# Get data
data = request.get_data()[0]

# Extract bands
temperature = data[:, :, 0]
ndvi = data[:, :, 1]
data_mask = data[:, :, 2]
red_band = data[:, :, 3]

# Create urban vs vegetation mask based on NDVI
urban_mask = (ndvi < 0.2) & (data_mask > 0)
veg_mask = (ndvi > 0.4) & (data_mask > 0)

# Calculate statistics
urban_temp = temperature[urban_mask]
veg_temp = temperature[veg_mask]

urban_mean = np.mean(urban_temp)
veg_mean = np.mean(veg_temp)
temp_diff = urban_mean - veg_mean

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Temperature map
divnorm = TwoSlopeNorm(vmin=np.nanmin(temperature), vcenter=(veg_mean + urban_mean)/2, vmax=np.nanmax(temperature))
im1 = axes[0, 0].imshow(temperature, cmap='RdYlBu_r', norm=divnorm)
axes[0, 0].set_title('Land Surface Temperature (°C)')
axes[0, 0].axis('off')
cbar1 = fig.colorbar(im1, ax=axes[0, 0], fraction=0.046, pad=0.04)
cbar1.set_label('Temperature (°C)')

# NDVI map
im2 = axes[0, 1].imshow(ndvi, cmap='YlGn', vmin=-0.2, vmax=0.8)
axes[0, 1].set_title('NDVI (Vegetation Index)')
axes[0, 1].axis('off')
cbar2 = fig.colorbar(im2, ax=axes[0, 1], fraction=0.046, pad=0.04)
cbar2.set_label('NDVI')

# Urban vs Vegetation mask
mask_vis = np.zeros_like(ndvi)
mask_vis[urban_mask] = 1
mask_vis[veg_mask] = 2
im3 = axes[1, 0].imshow(mask_vis, cmap='viridis', vmin=0, vmax=2)
axes[1, 0].set_title('Land Cover Classification')
axes[1, 0].axis('off')
cbar3 = fig.colorbar(im3, ax=axes[1, 0], fraction=0.046, pad=0.04, ticks=[0.33, 1, 1.67])
cbar3.set_ticklabels(['Other', 'Urban', 'Vegetation'])

# Temperature histogram
axes[1, 1].hist(urban_temp, bins=30, alpha=0.7, label=f'Urban (mean={urban_mean:.2f}°C)')
axes[1, 1].hist(veg_temp, bins=30, alpha=0.7, label=f'Vegetation (mean={veg_mean:.2f}°C)')
axes[1, 1].set_title(f'Temperature Distribution\nUrban Heat Island Effect: +{temp_diff:.2f}°C')
axes[1, 1].set_xlabel('Temperature (°C)')
axes[1, 1].set_ylabel('Pixel Count')
axes[1, 1].legend()
axes[1, 1].grid(True, linestyle='--', alpha=0.7)

plt.suptitle('Urban Heat Island Analysis - Phoenix, AZ - July 2022', fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('urban_heat_island.png', dpi=300, bbox_inches='tight')
plt.show()
```

## 6. Disaster Response and Management

Satellite imagery provides crucial information for disaster response, including flood mapping, fire detection, and damage assessment.

### Example: Flood Mapping with Sentinel-1 SAR Data

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sentinelhub import (
    CRS, BBox, DataCollection, MimeType, SentinelHubRequest, bbox_to_dimensions, SHConfig
)

# Set up authentication
config = SHConfig()
config.sh_client_id = 'YOUR-CLIENT-ID'
config.sh_client_secret = 'YOUR-CLIENT-SECRET'

# Define area of interest (example: Mississippi River flooding)
bbox_coords = (-91.2, 32.3, -90.8, 32.7)
bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)
resolution = 40
size = bbox_to_dimensions(bbox, resolution=resolution)

# Evalscript for Sentinel-1 water detection
evalscript_s1 = """
//VERSION=3
function setup() {
  return {
    input: ["VV", "VH"],
    output: {
      bands: 3,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  // Water detection using VV band threshold
  let waterMask = sample.VV < -15 ? 1 : 0;
  
  // Return VV, VH, and water mask
  return [sample.VV, sample.VH, waterMask];
}
"""

# Define pre-flood and during-flood time ranges
pre_flood_range = ("2022-01-01", "2022-01-15")  # Example period before flooding
during_flood_range = ("2022-03-01", "2022-03-15")  # Example period during flooding

# Request pre-flood data
request_pre = SentinelHubRequest(
    evalscript=evalscript_s1,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL1_IW,
            time_interval=pre_flood_range
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox,
    size=size,
    config=config,
)

# Request during-flood data
request_during = SentinelHubRequest(
    evalscript=evalscript_s1,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL1_IW,
            time_interval=during_flood_range
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox,
    size=size,
    config=config,
)

# Get data
data_pre = request_pre.get_data()[0]
data_during = request_during.get_data()[0]

# Extract bands
vv_pre = data_pre[:, :, 0]
water_pre = data_pre[:, :, 2]

vv_during = data_during[:, :, 0]
water_during = data_during[:, :, 2]

# Calculate flood extent (water during flood - permanent water)
flood_extent = water_during - water_pre
flood_extent[flood_extent < 0] = 0  # Ensure we don't have negative values

# Request optical data for reference (using Sentinel-2)
evalscript_s2 = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B03", "B02"],
    output: { bands: 3 }
  };
}

function evaluatePixel(sample) {
  return [2.5*sample.B04, 2.5*sample.B03, 2.5*sample.B02];
}
"""

request_rgb = SentinelHubRequest(
    evalscript=evalscript_s2,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=pre_flood_range
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
    bbox=bbox,
    size=size,
    config=config,
)

rgb = request_rgb.get_data()[0]

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# RGB reference image
axes[0, 0].imshow(rgb / 255.0)
axes[0, 0].set_title('Reference RGB Image (Pre-flood)')
axes[0, 0].axis('off')

# SAR VV backscatter
vv_min, vv_max = -25, 0
axes[0, 1].imshow(vv_during, cmap='gray', vmin=vv_min, vmax=vv_max)
axes[0, 1].set_title('Sentinel-1 VV Backscatter (During Flood)')
axes[0, 1].axis('off')

# Water during flood
water_cmap = ListedColormap(['none', 'blue'])
axes[1, 0].imshow(rgb / 255.0)  # Background RGB
axes[1, 0].imshow(water_during, cmap=water_cmap, alpha=0.7)
axes[1, 0].set_title('Water Extent (During Flood)')
axes[1, 0].axis('off')

# Flood-specific areas
flood_cmap = ListedColormap(['none', 'red'])
axes[1, 1].imshow(rgb / 255.0)  # Background RGB
axes[1, 1].imshow(flood_extent, cmap=flood_cmap, alpha=0.7)
axes[1, 1].set_title('Flood-Specific Areas')
axes[1, 1].axis('off')

# Calculate and display statistics
permanent_water_area = np.sum(water_pre) * resolution * resolution / 1e6  # km²
flood_water_area = np.sum(water_during) * resolution * resolution / 1e6  # km²
flood_specific_area = np.sum(flood_extent) * resolution * resolution / 1e6  # km²

stats_text = (
    f"Permanent Water: {permanent_water_area:.2f} km²\n"
    f"Total Water During Flood: {flood_water_area:.2f} km²\n"
    f"Flooded Area: {flood_specific_area:.2f} km²\n"
    f"Increase: {(flood_water_area / permanent_water_area - 1) * 100:.1f}%"
)

plt.figtext(0.5, 0.02, stats_text, ha='center', fontsize=12, 
           bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 5})

plt.suptitle('Flood Mapping using Sentinel-1 SAR Data', fontsize=16)
plt.tight_layout(rect=[0, 0.05, 1, 0.96])
plt.savefig('flood_mapping.png', dpi=300, bbox_inches='tight')
plt.show()
```

## Resources for Further Exploration

These examples demonstrate just a few of the many applications of the Sentinel Hub Process API. For more advanced use cases, consider exploring:

1. **Machine Learning Integration**: 
   - Use [eo-learn](https://eo-learn.readthedocs.io/) to create ML-ready features from satellite data
   - Apply pre-trained models for land cover classification, object detection, etc.

2. **Time Series Analysis**:
   - Monitor long-term changes using statistical metrics
   - Detect anomalies and trends

3. **Custom Indices and Algorithms**:
   - Develop custom spectral indices for specific applications
   - Implement scientific algorithms in evalscripts

4. **Multi-sensor Fusion**:
   - Combine optical, radar, and other data sources
   - Integrate with ground data or other remote sensing platforms

5. **Advanced Visualization**:
   - Create interactive maps with tools like Folium or Bokeh
   - Build dashboards for monitoring applications

For more examples and resources, visit the [Sentinel Hub GitHub repository](https://github.com/sentinel-hub) and the [Sentinel Hub custom scripts repository](https://github.com/sentinel-hub/custom-scripts). 