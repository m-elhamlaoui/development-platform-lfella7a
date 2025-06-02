import os
import pandas as pd
from typing import Dict, List, Union
from datetime import datetime
from cyfi import CyFi
from loguru import logger
from .config import SentinelConfig
from sentinelhub import (
    DataCollection,
    SentinelHubRequest,
    MosaickingOrder,
    BBox,
    CRS
)

class CyFiAnalyzer:
    def __init__(self):
        """Initialize the CyFi analyzer with the official CyFi package."""
        # Initialize Sentinel Hub configuration
        self.sentinel_config = SentinelConfig()
        
        # Initialize CyFi with Sentinel Hub configuration
        self.cyfi = CyFi()
        self.cyfi.sh_config = self.sentinel_config.get_credentials()
        logger.info("CyFi analyzer initialized with Sentinel Hub credentials")

    def _generate_points_grid(self, bbox: Dict[str, float], grid_size: float = 0.001) -> List[Dict[str, float]]:
        """Generate a grid of points within the bounding box."""
        points = []
        lat_start = bbox['south']
        while lat_start <= bbox['north']:
            lon_start = bbox['west']
            while lon_start <= bbox['east']:
                points.append({
                    'latitude': lat_start,
                    'longitude': lon_start
                })
                lon_start += grid_size
            lat_start += grid_size
        return points

    def _create_input_df(self, points: List[Dict[str, float]], date: str) -> pd.DataFrame:
        """Create input DataFrame for CyFi analysis."""
        return pd.DataFrame({
            'latitude': [p['latitude'] for p in points],
            'longitude': [p['longitude'] for p in points],
            'date': [date] * len(points)
        })

    async def analyze_area(
        self,
        bbox: Dict[str, float],
        date: str,
        grid_size: float = 0.001
    ) -> Dict[str, Union[str, float, dict]]:
        """
        Analyze a geographical area for cyanobacteria presence.
        
        Args:
            bbox: Dict with 'west', 'south', 'east', 'north' coordinates
            date: Analysis date in YYYY-MM-DD format
            grid_size: Grid size for sampling points in degrees
            
        Returns:
            Dict containing analysis results and visualizations
        """
        try:
            # Generate grid points
            points = self._generate_points_grid(bbox, grid_size)
            
            # Create input DataFrame
            input_df = self._create_input_df(points, date)
            
            # Save temporary CSV for CyFi
            temp_csv = 'temp_points.csv'
            input_df.to_csv(temp_csv, index=False)
            
            # Run CyFi prediction
            logger.info(f"Running CyFi analysis for {len(points)} points")
            predictions = self.cyfi.predict(temp_csv)
            
            # Clean up temporary file
            os.remove(temp_csv)
            
            # Process results
            mean_density = predictions['density_cells_per_ml'].mean()
            severity_counts = predictions['severity'].value_counts()
            dominant_severity = severity_counts.index[0]
            
            # Calculate confidence based on severity agreement
            confidence = (severity_counts.max() / len(predictions)) * 100
            
            return {
                'timestamp': datetime.now().isoformat(),
                'bbox': bbox,
                'predictions': {
                    'density_cells_per_ml': float(mean_density),
                    'severity': dominant_severity,
                    'confidence': float(confidence)
                },
                'metadata': {
                    'points_analyzed': len(points),
                    'date_analyzed': date,
                    'grid_size': grid_size
                }
            }
            
        except Exception as e:
            logger.error(f"Error in CyFi analysis: {str(e)}")
            raise Exception(f"CyFi analysis failed: {str(e)}")

    async def analyze_point(
        self,
        latitude: float,
        longitude: float,
        date: str
    ) -> Dict[str, Union[str, float, dict]]:
        """
        Analyze a single point for cyanobacteria presence.
        
        Args:
            latitude: Point latitude
            longitude: Point longitude
            date: Analysis date in YYYY-MM-DD format
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Create input DataFrame for single point
            input_df = pd.DataFrame({
                'latitude': [latitude],
                'longitude': [longitude],
                'date': [date]
            })
            
            # Save temporary CSV
            temp_csv = 'temp_point.csv'
            input_df.to_csv(temp_csv, index=False)
            
            # Run CyFi prediction
            logger.info(f"Running CyFi analysis for point ({latitude}, {longitude})")
            prediction = self.cyfi.predict(temp_csv)
            
            # Clean up
            os.remove(temp_csv)
            
            if len(prediction) == 0:
                raise Exception("No prediction generated")
                
            return {
                'timestamp': datetime.now().isoformat(),
                'location': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'predictions': {
                    'density_cells_per_ml': float(prediction['density_cells_per_ml'].iloc[0]),
                    'severity': prediction['severity'].iloc[0]
                },
                'metadata': {
                    'date_analyzed': date
                }
            }
            
        except Exception as e:
            logger.error(f"Error in point analysis: {str(e)}")
            raise Exception(f"Point analysis failed: {str(e)}") 