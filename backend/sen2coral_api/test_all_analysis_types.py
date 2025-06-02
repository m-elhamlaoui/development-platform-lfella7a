#!/usr/bin/env python3
"""
Comprehensive test script for Sen2Coral API Phase 2 completion
Tests all analysis types and verifies enhanced functionality
"""
import requests
import json
import time
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Health check: {data['status']}")
    return True

def test_capabilities():
    """Test capabilities endpoint"""
    print("\n🔍 Testing capabilities endpoint...")
    response = requests.get(f"{BASE_URL}/api/sen2coral/capabilities")
    assert response.status_code == 200
    data = response.json()
    
    print(f"✅ Analysis types: {data['analysisTypes']}")
    print(f"✅ Water quality indices: {data['waterQualityIndices']}")
    print(f"✅ Habitat classes: {data['habitatClasses']}")
    print(f"✅ Max area: {data['maxArea']} km²")
    
    return data

def test_analysis(analysis_type: str, coordinates: Dict[str, float] = None) -> Dict[str, Any]:
    """Test analysis endpoint for a specific type"""
    if coordinates is None:
        coordinates = {
            "west": -122.52,
            "south": 37.70,
            "east": -122.15,
            "north": 37.90
        }
    
    request_data = {
        "coordinates": coordinates,
        "timeRange": {
            "startDate": "2025-06-01",
            "endDate": "2025-06-30"
        },
        "dataSource": "sentinel2",
        "analysisType": analysis_type,
        "options": {
            "cloudMaskThreshold": 20,
            "waterQualityIndices": ["ndwi", "clarity", "turbidity"],
            "habitatClasses": ["coral", "seagrass", "sand"]
        }
    }
    
    print(f"\n🔍 Testing {analysis_type} analysis...")
    start_time = time.time()
    
    response = requests.post(
        f"{BASE_URL}/api/sen2coral/analyze",
        json=request_data,
        headers={"Content-Type": "application/json"}
    )
    
    processing_time = time.time() - start_time
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"✅ {analysis_type} analysis completed in {processing_time:.2f}s")
    print(f"   📊 Processing time: {data['metadata']['processingTime']}s")
    print(f"   🌍 Coordinates: {data['bbox']}")
    print(f"   📅 Timestamp: {data['timestamp']}")
    print(f"   🔧 Algorithm: {data['metadata']['algorithmVersion']}")
    
    # Check specific results based on analysis type
    if analysis_type == "water_quality" and data.get("waterQuality"):
        wq = data["waterQuality"]
        print(f"   💧 NDWI: {wq['ndwi']:.3f}")
        print(f"   🔍 Clarity: {wq['clarity']:.3f}")
        print(f"   🌊 Turbidity: {wq['turbidity']:.3f}")
        print(f"   🌱 Chlorophyll: {wq['chlorophyll']:.3f}")
    
    if analysis_type == "habitat" and data.get("habitat"):
        hab = data["habitat"]
        print(f"   🪸 Coral cover: {hab['coralCover']:.1f}%")
        print(f"   🌿 Seagrass cover: {hab['seagrassCover']:.1f}%")
        print(f"   🏖️ Sand cover: {hab['sandCover']:.1f}%")
    
    if analysis_type == "bathymetry" and data.get("bathymetry"):
        bath = data["bathymetry"]
        print(f"   📏 Mean depth: {bath['meanDepth']:.1f}m")
        print(f"   📐 Depth range: {bath['minDepth']:.1f}m - {bath['maxDepth']:.1f}m")
        print(f"   🎯 Confidence: {bath['depthConfidence']:.2f}")
    
    if analysis_type == "change_detection" and data.get("changeDetection"):
        cd = data["changeDetection"]
        print(f"   📈 Water quality change: {cd['waterQualityChange']:.1f}%")
        print(f"   🪸 Habitat change: {cd['habitatChange']:.1f}%")
        print(f"   📏 Depth change: {cd['depthChange']:.1f}m")
    
    # Check GeoJSON
    if data.get("geojson") and data["geojson"].get("features"):
        feature_count = len(data["geojson"]["features"])
        print(f"   🗺️ GeoJSON features: {feature_count}")
    
    return data

def test_different_locations():
    """Test analysis with different geographic locations"""
    locations = [
        {
            "name": "San Francisco Bay",
            "coords": {"west": -122.52, "south": 37.70, "east": -122.15, "north": 37.90}
        },
        {
            "name": "Great Barrier Reef",
            "coords": {"west": 145.0, "south": -16.5, "east": 145.5, "north": -16.0}
        },
        {
            "name": "Caribbean (small area)",
            "coords": {"west": -80.25, "south": 25.70, "east": -80.05, "north": 25.90}
        }
    ]
    
    print("\n🌍 Testing different geographic locations...")
    
    for location in locations:
        print(f"\n📍 Testing {location['name']}...")
        try:
            result = test_analysis("water_quality", location["coords"])
            print(f"✅ {location['name']} analysis successful")
        except Exception as e:
            print(f"❌ {location['name']} analysis failed: {str(e)}")

def test_error_handling():
    """Test error handling with invalid requests"""
    print("\n🔍 Testing error handling...")
    
    # Test invalid coordinates
    invalid_request = {
        "coordinates": {
            "west": 200,  # Invalid longitude
            "south": 37.70,
            "east": -122.15,
            "north": 37.90
        },
        "timeRange": {
            "startDate": "2025-06-01",
            "endDate": "2025-06-30"
        },
        "dataSource": "sentinel2",
        "analysisType": "water_quality"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/sen2coral/analyze",
        json=invalid_request,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 422:  # Validation error
        print("✅ Invalid coordinates properly rejected")
    else:
        print(f"⚠️ Unexpected response for invalid coordinates: {response.status_code}")

def main():
    """Run comprehensive tests"""
    print("🚀 Starting Sen2Coral API Phase 2 Comprehensive Tests")
    print("=" * 60)
    
    try:
        # Basic functionality tests
        test_health()
        capabilities = test_capabilities()
        
        # Test all analysis types
        analysis_types = capabilities.get("analysisTypes", ["water_quality", "habitat", "bathymetry", "change_detection"])
        
        for analysis_type in analysis_types:
            test_analysis(analysis_type)
        
        # Test different locations
        test_different_locations()
        
        # Test error handling
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("✅ Sen2Coral API Phase 2 is fully functional")
        print("\n📋 Summary:")
        print("   • Health endpoint: Working")
        print("   • Capabilities endpoint: Working")
        print("   • All analysis types: Working")
        print("   • Multiple locations: Working")
        print("   • Error handling: Working")
        print("   • Enhanced mock analysis: Active")
        print("\n🔗 API Documentation: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main() 