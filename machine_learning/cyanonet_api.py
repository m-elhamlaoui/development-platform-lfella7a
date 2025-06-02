from fastapi import FastAPI, Query
import subprocess
import tempfile
import pandas as pd
import os

app = FastAPI()

@app.get("/predict_cyano")
def predict_cyano(lat: float = Query(...), lon: float = Query(...), date: str = Query(...)):
    """
    Predict cyanobacteria density for a given latitude, longitude, and date using CyFi.
    Returns a JSON object with prediction results.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        input_csv = os.path.join(tmpdir, "input.csv")
        output_csv = os.path.join(tmpdir, "preds.csv")
        # Write input CSV
        pd.DataFrame([{"latitude": lat, "longitude": lon, "date": date}]).to_csv(input_csv, index=False)
        # Run CyFi batch prediction
        subprocess.run(["cyfi", "predict", input_csv, "--output", output_csv], check=True)
        # Read result
        result = pd.read_csv(output_csv).iloc[0].to_dict()
    return result 