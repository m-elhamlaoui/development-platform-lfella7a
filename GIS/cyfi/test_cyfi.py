import subprocess
import json
import pandas as pd
from pathlib import Path
import os
import tempfile

def test_cyfi():
    try:
        # Get the absolute path to test_points.csv
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        input_csv = current_dir / 'test_points.csv'
        
        # Create a temporary directory for cache
        temp_dir = Path(tempfile.gettempdir()) / 'cyfi_cache'
        temp_dir.mkdir(exist_ok=True)
        
        print("Running CyFi analysis...")
        print(f"Using input file: {input_csv.absolute()}")
        print(f"Using cache directory: {temp_dir}")
        
        # Set environment variable for cache directory
        os.environ['CYFI_CACHE_DIR'] = str(temp_dir)
        
        # Run cyfi predict command
        result = subprocess.run(
            ['cyfi', 'predict', str(input_csv.absolute())],
            capture_output=True,
            text=True,
            env=os.environ
        )
        
        if result.returncode != 0:
            print("Error running CyFi:")
            print(result.stderr)
            return
            
        # Check if preds.csv was created in the current directory
        preds_file = current_dir / 'preds.csv'
        if not preds_file.exists():
            print("No predictions file was created")
            return
            
        # Read and display predictions
        preds = pd.read_csv(preds_file)
        print("\nPredictions:")
        print(preds)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    test_cyfi() 