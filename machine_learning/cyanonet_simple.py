import sys
import random
import math
from datetime import datetime

def mock_cyano_prediction(lat, lon, date):
    """
    Mock cyanobacteria prediction based on realistic factors:
    - Warmer months = higher risk
    - Shallow/warm water bodies = higher risk
    - Some randomness for realism
    """
    
    # Parse date to get month
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        month = date_obj.month
    except:
        month = 7  # Default to summer
    
    # Base risk factors
    seasonal_factor = 0.5 + 0.5 * math.sin((month - 3) * math.pi / 6)  # Peak in summer
    latitude_factor = max(0, 1 - abs(lat) / 90)  # Lower latitudes = warmer
    
    # Add some location-based variation
    location_seed = int((lat * 1000 + lon * 1000) % 1000)
    random.seed(location_seed)
    location_factor = random.uniform(0.3, 1.0)
    
    # Calculate density (cells/mL)
    base_density = 1000
    density = base_density * seasonal_factor * latitude_factor * location_factor
    density = max(0, density + random.uniform(-200, 500))
    
    # Risk classification
    if density < 500:
        risk = "Low"
    elif density < 2000:
        risk = "Moderate"
    elif density < 10000:
        risk = "High"
    else:
        risk = "Very High"
    
    return {
        "latitude": lat,
        "longitude": lon,
        "date": date,
        "cyanobacteria_density_cells_per_ml": round(density, 2),
        "risk_level": risk,
        "seasonal_factor": round(seasonal_factor, 3),
        "confidence": round(random.uniform(0.7, 0.95), 3)
    }

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python cyanonet_simple.py <lat> <lon> <date>")
        print("Example: python cyanonet_simple.py 41.2 -73.2 2023-09-14")
        sys.exit(1)

    lat = float(sys.argv[1])
    lon = float(sys.argv[2])
    date = sys.argv[3]

    print(f"🌊 FAST Cyanonet Prediction")
    print(f"   Latitude: {lat}")
    print(f"   Longitude: {lon}")
    print(f"   Date: {date}")
    print()

    result = mock_cyano_prediction(lat, lon, date)
    
    print("🎯 PREDICTION RESULTS:")
    print("=" * 40)
    for key, value in result.items():
        print(f"{key}: {value}")
    
    print()
    print("⚡ Note: This is a fast mock prediction.")
    print("   For real satellite-based predictions, use cyanonet_predict.py") 