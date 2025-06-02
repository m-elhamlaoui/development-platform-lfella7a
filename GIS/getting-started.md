# Getting Started with Sentinel Hub

This guide covers the essential first steps to start working with Sentinel Hub's services.

## Account Setup

1. **Create a Sentinel Hub account**:
   - Visit [Sentinel Hub](https://www.sentinel-hub.com/) and click "Sign Up"
   - A free trial is available for 30 days
   - Academic and research users may qualify for ESA-sponsored accounts

2. **Understand the subscription options**:
   - Different pricing tiers based on processing units needed
   - Processing units are consumed based on the area size, data collection, and complexity of processing

## Authentication

To use the Sentinel Hub APIs, you need to authenticate using OAuth 2.0:

1. **Create OAuth credentials**:
   - Log in to your Sentinel Hub Dashboard
   - Navigate to "User settings" → "OAuth clients"
   - Click "Create new OAuth client"
   - Name your client and save the generated Client ID and Client Secret

2. **Request an access token**:
   
   ```bash
   curl -X POST \
     https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=client_credentials&client_id=YOUR_CLIENT_ID" \
     --data-urlencode "client_secret=YOUR_CLIENT_SECRET"
   ```

   This returns a JSON object containing an `access_token` that's valid for one hour.

3. **Use the token in API requests**:

   ```bash
   curl -X POST \
     https://services.sentinel-hub.com/api/v1/process \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{...}'
   ```

## Available APIs

Sentinel Hub offers multiple APIs for different purposes:

1. **Process API** - The most commonly used API for requesting satellite imagery
2. **Catalog API** - For searching available satellite data
3. **Batch Processing API** - For processing large areas or long time periods
4. **Statistical API** - For calculating statistics from satellite data
5. **OGC API** - Standard OGC web services (WMS, WCS, WMTS, WFS)

## Main Concepts

### Data Collections

Sentinel Hub provides access to various satellite data collections:

- **Sentinel-2** - High-resolution optical imagery (10m resolution)
- **Sentinel-1** - Synthetic Aperture Radar (SAR) data
- **Landsat** - Long-term optical imagery from NASA/USGS
- **MODIS** - Moderate resolution daily imagery
- **DEM** - Digital Elevation Models

### Evalscript

Evalscript is a JavaScript-based domain-specific language used to define how to process satellite data:

```javascript
//VERSION=3
function setup() {
  return {
    input: ["B04", "B03", "B02"],
    output: { bands: 3 }
  };
}

function evaluatePixel(sample) {
  return [sample.B04, sample.B03, sample.B02];
}
```

This simple evalscript returns a true color image using the Red, Green, and Blue bands from a satellite image.

### Areas of Interest (AOI)

Define the geographical area you want to process using:
- Bounding box coordinates (most common)
- GeoJSON geometry
- Well-known text (WKT) geometry

### Time Range

Specify the time period for which you want to retrieve data:
- Single date
- Date range (e.g., for creating composite images)

## Tools for Working with Sentinel Hub

- **Requests Builder** - Web UI for constructing API requests without coding
- **EO Browser** - Web application for browsing and exploring satellite imagery
- **sentinelhub-py** - Python package for programmatic access
- **eo-learn** - Python package for machine learning with satellite data

In the next section, [Process API Basics](process-api-basics.md), we'll dive deeper into using the Process API to retrieve satellite imagery. 