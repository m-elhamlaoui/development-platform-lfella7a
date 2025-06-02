import sys
import subprocess
import json

if len(sys.argv) != 4:
    print("Usage: python cyanonet_predict.py <lat> <lon> <date>")
    print("Example: python cyanonet_predict.py 41.2 -73.2 2023-09-14")
    sys.exit(1)

lat = float(sys.argv[1])
lon = float(sys.argv[2])
date = sys.argv[3]

print(f"🌊 Predicting cyanobacteria for:")
print(f"   Latitude: {lat}")
print(f"   Longitude: {lon}")
print(f"   Date: {date}")
print()

try:
    print("🚀 Running CyFi prediction...")
    
    # Use predict-point for single location (should be faster)
    result = subprocess.run([
        "cyfi", "predict-point", 
        "--lat", str(lat), 
        "--lon", str(lon), 
        "--date", date,
        "-v"  # Verbose output
    ], capture_output=True, text=True, check=True)
    
    print("✅ CyFi completed successfully!")
    print()
    
    # Parse the output
    output_lines = result.stdout.strip().split('\n')
    
    print("🎯 PREDICTION RESULTS:")
    print("=" * 40)
    
    # Look for the prediction result in the output
    for line in output_lines:
        if "density" in line.lower() or "prediction" in line.lower():
            print(f"Result: {line}")
    
    # Print all output for debugging
    print("\n📋 Full CyFi Output:")
    print("-" * 30)
    print(result.stdout)
    
    if result.stderr:
        print("\n⚠️  Warnings/Errors:")
        print("-" * 20)
        print(result.stderr)
            
except subprocess.CalledProcessError as e:
    print(f"❌ CyFi command failed:")
    print(f"   Return code: {e.returncode}")
    print(f"   Error output: {e.stderr}")
    print(f"   Standard output: {e.stdout}")
except Exception as e:
    print(f"❌ Unexpected error: {e}") 