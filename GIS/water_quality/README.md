# Water Quality Monitoring Tool

This tool provides satellite-based water quality analysis using Sentinel Hub services with advanced customized algorithms for water quality assessment.

## Features

- Detect water bodies using NDWI (Normalized Difference Water Index)
- Analyze water quality parameters using surface reflectance
- Advanced algal bloom detection using specialized multi-spectral indices
- Support for multiple satellite data sources:
  - Sentinel-2 L2A and L1C (10m resolution)
  - Landsat 8/9 L2 and L1 (30m resolution)
  - Landsat 7 ETM+ (30m resolution)
  - Landsat 4-5 TM (30m resolution)
  - Harmonized Landsat Sentinel (30m resolution)
  - MODIS (250m resolution)
- Detailed visualization with custom colormaps
- Water quality metrics including clear water percentage, moderate quality, and potential algal presence

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Or install individual components:
   ```bash
   pip install sentinelhub matplotlib numpy pillow scipy
   ```

3. Configure Sentinel Hub credentials:
   - Sign up for a free account at [Sentinel Hub](https://www.sentinel-hub.com/)
   - Create a new OAuth client
   - Update the script with your client ID and secret

## Usage

```bash
python water_quality_monitor.py --config config.json --output analysis.png --data results.json
```

Where `config.json` contains:
```json
{
    "bboxCoords": [-122.52, 37.70, -122.15, 37.90],
    "timeInterval": ["2023-06-01", "2023-06-30"],
    "dataSource": "sentinel2"
}
```

## Enhanced Algal Detection

This tool uses a customized, satellite-specific approach for detecting algal blooms and chlorophyll concentration:

### For Sentinel-2
Uses a multi-index approach combining:
- Normalized Difference Chlorophyll Index (NDCI): (B05 - B04) / (B05 + B04)
- Red-Edge Chlorophyll Index (RECI): (B07 / B05) - 1
- Modified Chlorophyll Absorption Ratio Index (MCARI): ((B05 - B04) - 0.2 * (B05 - B03)) * (B05 / B04)

These indices leverage Sentinel-2's unique red-edge bands which are specifically sensitive to chlorophyll variations in water.

### For Landsat
Uses a combination of spectral ratios optimized for Landsat's band configuration:
- NIR/Red ratio: Sensitive to chlorophyll concentration
- SWIR/NIR ratio: Helps distinguish organic matter
- Triband ratio (Green/Red)/Blue: Enhanced sensitivity to chlorophyll

### For MODIS
Implements a specialized approach for MODIS's coarser resolution:
- Enhanced NIR/Red ratio calibrated for larger pixels
- Multi-band approach using green band normalization

This implementation provides accurate detection of algal presence and avoids the common issue of misidentifying transition zones (shorelines, shallow water) as algal blooms.

## Recent Improvements

The tool has been significantly enhanced with:

1. **Improved Algal Detection**: Implemented a specialized multi-spectral approach that accurately distinguishes between true algal blooms and shoreline/transition zones.

2. **Multi-Satellite Support**: Added customized algorithms for each satellite platform that take advantage of each sensor's unique spectral capabilities.

3. **Clearer Visualization**: Enhanced visualization that properly identifies transition zones and shallow water areas, avoiding false positive algal bloom detection.

4. **Reliability**: Removed external dependencies in favor of a robust custom implementation that works consistently across different environments.

## Output

The tool generates:
1. An analysis image with true color, NDWI, and algal potential visualizations
2. A detailed NDWI visualization highlighting different water zones
3. A JSON file with water quality metrics
4. A raw RGB satellite image

## Demo

Run the demo mode to see the tool in action:
   ```bash
   python water_quality_monitor.py
   ```

## Technical Details

The implementation uses specialized evaluation scripts that run directly on the Sentinel Hub processing API, allowing for efficient calculation of complex indices before downloading the data. This approach provides:

1. Better performance (calculations happen on the server side)
2. Reduced bandwidth usage (only the results are downloaded)
3. Higher quality analysis using the full spectral information

## Credits

- Sentinel Hub for satellite data access and evalscript processing
- Matplotlib for visualization 