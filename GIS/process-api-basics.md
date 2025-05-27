# Sentinel Hub Process API Basics

The Process API is Sentinel Hub's core service for retrieving and processing satellite imagery. This guide covers the fundamental aspects of using the Process API.

## What is the Process API?

The Process API allows you to:

- Request satellite imagery for specific areas and time ranges
- Apply custom processing to raw satellite data
- Receive processed imagery in various formats (PNG, JPEG, TIFF)
- Obtain raw band values for scientific analysis

## API Endpoint

The Process API's main endpoint is:

```
https://services.sentinel-hub.com/api/v1/process
```

All requests are made via HTTP POST method.

## Request Structure

A typical Process API request is structured as follows:

```json
{
  "input": {
    "bounds": {
      "bbox": [13.822174072265625, 45.85080395917834, 14.55963134765625, 46.29191774991382],
      "properties": {
        "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
      }
    },
    "data": [
      {
        "type": "S2L2A",
        "dataFilter": {
          "timeRange": {
            "from": "2020-05-01T00:00:00Z",
            "to": "2020-06-01T23:59:59Z"
          },
          "mosaickingOrder": "leastCC"
        }
      }
    ]
  },
  "output": {
    "width": 512,
    "height": 512,
    "responses": [
      {
        "identifier": "default",
        "format": {
          "type": "image/png"
        }
      }
    ]
  },
  "evalscript": "//VERSION=3\nfunction setup() {\n  return {\n    input: [\"B04\", \"B03\", \"B02\"],\n    output: { bands: 3 }\n  };\n}\n\nfunction evaluatePixel(sample) {\n  return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];\n}"
}
```

Let's break down the main components:

### 1. Input Section

The `input` section defines what data you want to process:

#### Bounds

The `bounds` parameter specifies the geographical area (Area of Interest) you want to process:

```json
"bounds": {
  "bbox": [13.822174072265625, 45.85080395917834, 14.55963134765625, 46.29191774991382],
  "properties": {
    "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
  }
}
```

- `bbox`: An array of coordinates in the format [minX, minY, maxX, maxY]
- `crs`: The coordinate reference system (typically WGS84, EPSG:4326)

#### Data

The `data` parameter defines which satellite collection to use and how to filter the data:

```json
"data": [
  {
    "type": "S2L2A",
    "dataFilter": {
      "timeRange": {
        "from": "2020-05-01T00:00:00Z",
        "to": "2020-06-01T23:59:59Z"
      },
      "mosaickingOrder": "leastCC"
    }
  }
]
```

- `type`: The data collection (e.g., "S2L2A" for Sentinel-2 Level 2A)
- `timeRange`: Time period for which to retrieve data
- `mosaickingOrder`: How to prioritize images when creating a mosaic (e.g., "leastCC" for least cloud coverage)

Additional filtering options include:
- `maxCloudCoverage`: Maximum allowed cloud coverage percentage
- `previewMode`: For quicker, lower-quality previews
- `orbits`: For filtering specific satellite orbits (Sentinel-1)

### 2. Output Section

The `output` section defines the format and dimensions of the response:

```json
"output": {
  "width": 512,
  "height": 512,
  "responses": [
    {
      "identifier": "default",
      "format": {
        "type": "image/png"
      }
    }
  ]
}
```

- `width` and `height`: Dimensions of the output image in pixels
- `responses`: An array of response specifications
  - `identifier`: A name for the response
  - `format`: The format of the response (e.g., "image/png", "image/jpeg", "image/tiff")

### 3. Evalscript

The `evalscript` parameter contains the JavaScript code that defines how to process the data:

```javascript
//VERSION=3
function setup() {
  return {
    input: ["B04", "B03", "B02"],
    output: { bands: 3 }
  };
}

function evaluatePixel(sample) {
  return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
}
```

This example creates a true color image by:
1. Selecting the Red (B04), Green (B03), and Blue (B02) bands
2. Applying a brightness enhancement factor of 2.5
3. Returning the processed values as an RGB array

## Common Evalscript Examples

### True Color (RGB)

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

### False Color Infrared

```javascript
//VERSION=3
function setup() {
  return {
    input: ["B08", "B04", "B03"],
    output: { bands: 3 }
  };
}

function evaluatePixel(sample) {
  return [sample.B08, sample.B04, sample.B03];
}
```

### NDVI (Normalized Difference Vegetation Index)

```javascript
//VERSION=3
function setup() {
  return {
    input: ["B08", "B04"],
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
```

### Raw Band Values

```javascript
//VERSION=3
function setup() {
  return {
    input: ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B11", "B12"],
    output: {
      bands: 12,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  return [
    sample.B01, sample.B02, sample.B03, sample.B04, 
    sample.B05, sample.B06, sample.B07, sample.B08, 
    sample.B8A, sample.B09, sample.B11, sample.B12
  ];
}
```

## Making a Request

### Using cURL

```bash
curl -X POST \
  https://services.sentinel-hub.com/api/v1/process \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "bounds": {
        "bbox": [13.822174072265625, 45.85080395917834, 14.55963134765625, 46.29191774991382],
        "properties": {
          "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
        }
      },
      "data": [
        {
          "type": "S2L2A",
          "dataFilter": {
            "timeRange": {
              "from": "2020-05-01T00:00:00Z",
              "to": "2020-06-01T23:59:59Z"
            },
            "mosaickingOrder": "leastCC"
          }
        }
      ]
    },
    "output": {
      "width": 512,
      "height": 512,
      "responses": [
        {
          "identifier": "default",
          "format": {
            "type": "image/png"
          }
        }
      ]
    },
    "evalscript": "//VERSION=3\nfunction setup() {\n  return {\n    input: [\"B04\", \"B03\", \"B02\"],\n    output: { bands: 3 }\n  };\n}\n\nfunction evaluatePixel(sample) {\n  return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];\n}"
  }' > output.png
```

### Common Error Responses

- **401 Unauthorized**: Invalid or expired access token
- **400 Bad Request**: Malformed request JSON or evalscript
- **413 Payload Too Large**: Requested area or time range is too large
- **500 Internal Server Error**: Server-side issues or evalscript runtime errors

## Best Practices

1. **Start small**: Begin with small areas and simple evalscripts
2. **Check data availability**: Use Catalog API to verify data exists before requesting
3. **Optimize evalscripts**: Only request the bands you need
4. **Use appropriate formats**: PNG/JPEG for visualizations, TIFF for scientific analysis
5. **Consider data type**: Use UINT8 for visualization, FLOAT32 for analysis
6. **Handle no-data**: Include checks for no-data values in your evalscript
7. **Limit time ranges**: Request shorter time periods to reduce processing complexity

## Next Steps

Now that you understand the basics of the Process API, check out [Python Integration](python-integration.md) to learn how to use the Process API programmatically with Python. 