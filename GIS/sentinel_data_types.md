# Available Data Types in Sentinel Hub

This document outlines the various types of satellite data available through Sentinel Hub's Process API and how they can be used for different applications.

## Data Collections

Sentinel Hub provides access to multiple satellite data collections, including freely available public collections, commercial data, and the option to bring your own data.

### Sentinel Missions

#### Sentinel-2

The Sentinel-2 mission consists of twin satellites (Sentinel-2A and Sentinel-2B) providing high-resolution optical imagery. It's the most commonly used data source for vegetation monitoring, land use classification, and other optical remote sensing applications.

**Key Properties:**
- **Resolution:** 10m, 20m, and 60m (depending on the band)
- **Revisit time:** 5 days (with both satellites)
- **Data availability:** Since 2015
- **Processing levels:**
  - **L1C:** Top-of-atmosphere reflectance
  - **L2A:** Bottom-of-atmosphere (surface) reflectance (atmospherically corrected)

**Bands:**
| Band | Central Wavelength (nm) | Resolution (m) | Description |
|------|------------------------|----------------|-------------|
| B01 | 443 | 60 | Coastal aerosol |
| B02 | 490 | 10 | Blue |
| B03 | 560 | 10 | Green |
| B04 | 665 | 10 | Red |
| B05 | 705 | 20 | Vegetation Red Edge |
| B06 | 740 | 20 | Vegetation Red Edge |
| B07 | 783 | 20 | Vegetation Red Edge |
| B08 | 842 | 10 | NIR (Near Infrared) |
| B8A | 865 | 20 | Narrow NIR |
| B09 | 940 | 60 | Water vapor |
| B10 | 1375 | 60 | SWIR - Cirrus |
| B11 | 1610 | 20 | SWIR (Short Wave Infrared) |
| B12 | 2190 | 20 | SWIR |

#### Sentinel-1

Sentinel-1 provides all-weather, day-and-night radar imagery using Synthetic Aperture Radar (SAR) technology.

**Key Properties:**
- **Resolution:** 5m x 20m (IW mode)
- **Revisit time:** 6 days (with both satellites)
- **Data availability:** Since 2014
- **Polarizations:** VV, VH, HH, HV (depending on acquisition mode)
- **Acquisition modes:**
  - **IW (Interferometric Wide)**: Main acquisition mode over land
  - **EW (Extra Wide)**: Used primarily for maritime, polar areas and sea-ice monitoring
  - **SM (Stripmap)**: For small islands and specific campaigns
  - **WV (Wave)**: For determining ocean wave direction and wavelength

**Applications:**
- Flood mapping
- Sea ice monitoring
- Oil spill detection
- Ship detection
- Land-cover change detection
- Ground deformation monitoring

#### Sentinel-3

Sentinel-3 provides ocean and land monitoring data with its multiple instruments.

**Available Instruments:**
- **OLCI (Ocean and Land Color Instrument)**: Medium-resolution optical imaging for ocean and land color data
- **SLSTR (Sea and Land Surface Temperature Radiometer)**: Thermal infrared imaging for sea/land surface temperature

**Key Properties:**
- **Resolution:** 300m (OLCI), 500m-1km (SLSTR)
- **Revisit time:** ~2 days
- **Bands:** 21 bands (OLCI), 9 bands (SLSTR)

#### Sentinel-5P

Sentinel-5 Precursor carries the TROPOMI instrument for atmospheric monitoring.

**Key Properties:**
- **Resolution:** 7km x 3.5km
- **Data type:** Atmospheric gases and particles concentrations
- **Available products:** NO₂, O₃, SO₂, CH₄, CO, aerosol, cloud, etc.

### Landsat Collections

Landsat is NASA's longest-running Earth observation program, providing consistent imagery since 1972.

**Available Collections:**
- **Landsat 8-9 OLI/TIRS L1/L2:** The most recent Landsat satellites (2013-present)
- **Landsat 7 ETM+ L1/L2:** Operating since 1999 (with SLC-off data since 2003)
- **Landsat 4-5 TM L1/L2:** Historical data (1982-2013)
- **Landsat 1-5 MSS L1:** Oldest Landsat data (1972-1992)

**Key Properties (Landsat 8-9):**
- **Resolution:** 30m (15m for panchromatic, 100m for thermal)
- **Revisit time:** 16 days per satellite
- **Processing levels:**
  - **L1:** Top-of-atmosphere reflectance
  - **L2:** Surface reflectance (atmospherically corrected)

### Other Public Collections

#### MODIS

MODIS (Moderate Resolution Imaging Spectroradiometer) provides daily global coverage at moderate resolution.

**Key Properties:**
- **Resolution:** 250m, 500m, and 1000m (depending on band)
- **Revisit time:** Daily
- **Data availability:** Since 2000
- **Platforms:** Terra and Aqua satellites
- **Available products:** MCD43A4 (NBAR - Nadir BRDF-Adjusted Reflectance) 

#### Digital Elevation Models (DEM)

Sentinel Hub provides access to several global Digital Elevation Models:

- **Copernicus DEM:** Available at 30m and 90m resolution globally
- **Mapzen DEM:** Composite dataset from multiple sources

**Applications:**
- Terrain analysis
- Hydrological modeling
- Visibility analysis
- Orthorectification of satellite images

#### ENVISAT

Historical data from the European Space Agency's ENVISAT mission (2002-2012):

- **MERIS:** Medium Resolution Imaging Spectrometer, focused on ocean color and land cover

### Commercial Data Collections

#### Planet

- **PlanetScope:** 3-5m resolution daily imagery
- **SkySat:** 50-72cm high-resolution imagery
- **Planet Basemaps:** Mosaicked imagery at various frequencies
- **Analysis-Ready PlanetScope:** Harmonized, consistent time series

#### Maxar/DigitalGlobe

- **WorldView & GeoEye:** Very high resolution (31-50cm) commercial imagery

#### Planetary Variables

- **Crop Biomass:** Daily relative measurement of agricultural biomass
- **Soil Water Content:** Soil moisture measurements
- **Land Surface Temperature:** Skin temperature measurements

### Derived and Value-Added Products

- **Sentinel-2 L2A 120m Mosaic:** Cloud-free 10-daily composites
- **ESA WorldCover:** Global land cover map at 10m resolution
- **CNES Land Cover Map:** Land classification for France
- **10m Annual Land Use Land Cover:** 9-class global land cover
- **Road and Building Detection:** Infrastructure mapping from Planet imagery
- **Forest Carbon Products:** Canopy height, cover, and carbon metrics

### BYOD (Bring Your Own Data)

Users can also bring their own geospatial data to Sentinel Hub for processing, as long as the data is in Cloud Optimized GeoTIFF (COG) format.

## Common Indices and Analysis Types

The following indices and analysis types can be computed using Sentinel Hub data:

### Vegetation Indices

- **NDVI (Normalized Difference Vegetation Index):**
  ```
  (NIR - Red) / (NIR + Red)
  ```
  Primary index for vegetation monitoring, ranging from -1 to 1, with higher values indicating healthier vegetation.

- **EVI (Enhanced Vegetation Index):**
  ```
  2.5 * ((NIR - Red) / (NIR + 6 * Red - 7.5 * Blue + 1))
  ```
  Less sensitive to atmospheric effects and canopy background signals than NDVI.

- **SAVI (Soil Adjusted Vegetation Index):**
  ```
  ((NIR - Red) / (NIR + Red + L)) * (1 + L)
  ```
  Where L is a soil brightness correction factor.

- **LAI (Leaf Area Index):**
  Estimates the leaf area per unit ground area.

### Water Indices

- **NDWI (Normalized Difference Water Index):**
  ```
  (Green - NIR) / (Green + NIR)
  ```
  Used for water body detection and water content in vegetation.

- **MNDWI (Modified NDWI):**
  ```
  (Green - SWIR) / (Green + SWIR)
  ```
  Better differentiation between water and built-up areas.

### Built-Up/Urban Indices

- **NDBI (Normalized Difference Built-up Index):**
  ```
  (SWIR - NIR) / (SWIR + NIR)
  ```
  Highlights urban areas.

- **UI (Urban Index):**
  ```
  (SWIR2 - NIR) / (SWIR2 + NIR)
  ```
  Alternative for urban area detection.

### Other Specialized Indices

- **NBR (Normalized Burn Ratio):**
  ```
  (NIR - SWIR) / (NIR + SWIR)
  ```
  Used for burn scar mapping and fire severity assessment.

- **NDSI (Normalized Difference Snow Index):**
  ```
  (Green - SWIR) / (Green + SWIR)
  ```
  For snow cover detection.

## Data Processing Capabilities

Sentinel Hub allows for various types of processing through its evalscript functionality:

### Basic Operations

- **Band combinations:** Creating true color, false color, and other composite images
- **Band math:** Performing mathematical operations on band values
- **Thresholding:** Classifying pixels based on value thresholds
- **Scaling and normalization:** Adjusting data ranges for visualization

### Advanced Processing

- **Time-series analysis:** Processing data over multiple dates
- **Statistical operations:** Calculating min, max, mean, median, etc. over time
- **Custom algorithms:** Implementing specialized processing algorithms
- **Machine learning integration:** Preparing data for ML models
- **Data fusion:** Combining data from multiple sources (e.g., optical + radar)

## Data Output Formats

Sentinel Hub can provide data in various formats:

- **Raster image formats:**
  - PNG (8-bit visualization)
  - JPEG (8-bit visualization)
  - TIFF (8-bit or 32-bit for analysis)

- **Data types:**
  - UINT8: 8-bit unsigned integer (0-255)
  - UINT16: 16-bit unsigned integer (0-65535)
  - FLOAT32: 32-bit floating point (for scientific analysis)

## Example Applications

Here are some examples of what you can do with each data type:

### With Sentinel-2 Optical Data

1. **Agriculture:**
   - Crop health monitoring using NDVI
   - Irrigation management
   - Yield prediction
   - Field boundary detection

2. **Forestry:**
   - Deforestation detection
   - Species classification
   - Biomass estimation
   - Fire damage assessment

3. **Urban studies:**
   - Urban growth monitoring
   - Green space mapping
   - Land use classification

### With Sentinel-1 SAR Data

1. **Disaster response:**
   - Flood mapping (works through clouds)
   - Earthquake damage assessment
   - Oil spill detection

2. **Cryosphere:**
   - Sea ice monitoring
   - Glacier movement tracking
   - Snow cover mapping

3. **Agriculture:**
   - Soil moisture estimation
   - Crop type mapping
   - Field operations monitoring (plowing, harvesting)

### Multi-source Data Fusion

Combining different data sources can provide enhanced insights:

- **Sentinel-1 + Sentinel-2:** Complementary information (radar + optical)
- **Sentinel-2 + Landsat:** Extended time series
- **Satellite + DEM:** Topographic analysis and correction

## Conclusion

Sentinel Hub provides access to a rich variety of Earth observation data that can be used for countless applications across domains such as environmental monitoring, agriculture, urban planning, disaster management, and more. The flexible processing capabilities allow users to transform raw satellite data into actionable insights through custom algorithms and analysis workflows. 