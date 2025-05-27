import numpy as np
from PIL import Image
import io
import base64
import matplotlib.pyplot as plt
from .sentinel_data import SentinelDataRetriever

class CyFiAnalyzer:
    def __init__(self):
        self.data_retriever = SentinelDataRetriever()

    def _calculate_density(self, ndwi: np.ndarray) -> np.ndarray:
        """
        Calculate cyanobacteria density using NDWI values.
        This is a simplified version - in production, you'd use a trained ML model.
        """
        # Convert NDWI to density (cells/mL)
        # This is a placeholder calculation - replace with actual ML model
        water_mask = ndwi > 0.2  # Basic water detection
        density = np.zeros_like(ndwi)
        density[water_mask] = np.exp(-ndwi[water_mask] * 10) * 10000
        return density

    def _determine_severity(self, density: np.ndarray) -> tuple:
        """Determine bloom severity based on cell density."""
        mean_density = np.mean(density[density > 0])
        
        if mean_density < 2000:
            return 'low', 0.8
        elif mean_density < 5000:
            return 'moderate', 0.7
        else:
            return 'high', 0.6

    def _create_heatmap(self, density: np.ndarray) -> str:
        """Create a heatmap visualization of the density data."""
        plt.figure(figsize=(10, 8))
        plt.imshow(density, cmap='YlOrRd')
        plt.colorbar(label='Cells/mL')
        plt.title('Cyanobacteria Density')
        
        # Save to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"

    def _create_ndwi_visualization(self, ndwi: np.ndarray) -> str:
        """Create an NDWI visualization."""
        plt.figure(figsize=(10, 8))
        plt.imshow(ndwi, cmap='RdYlBu', vmin=-0.5, vmax=0.5)
        plt.colorbar(label='NDWI Value')
        plt.title('Normalized Difference Water Index')
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"

    def _create_true_color(self, rgb: np.ndarray) -> str:
        """Create a true color visualization."""
        # Normalize and enhance RGB image
        rgb_norm = np.clip(rgb * 3.5, 0, 1)
        
        plt.figure(figsize=(10, 8))
        plt.imshow(rgb_norm)
        plt.title('True Color Image')
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"

    async def analyze(self, bbox_coords: dict, time_range: dict) -> dict:
        """
        Perform CyFi analysis for the given area and time range.
        
        Args:
            bbox_coords: Dict with west, south, east, north coordinates
            time_range: Dict with startDate and endDate strings
            
        Returns:
            Dict containing analysis results and visualizations
        """
        try:
            # Fetch satellite data
            data = await self.data_retriever.fetch_data(bbox_coords, time_range)
            
            # Convert lists back to numpy arrays
            ndwi = np.array(data['ndwi'])
            rgb = np.array(data['rgb'])
            
            # Calculate density
            density = self._calculate_density(ndwi)
            
            # Determine severity and confidence
            severity, confidence = self._determine_severity(density)
            
            # Create visualizations
            visualizations = {
                'heatmap': self._create_heatmap(density),
                'ndwi': self._create_ndwi_visualization(ndwi),
                'trueColor': self._create_true_color(rgb)
            }
            
            return {
                'timestamp': time_range['startDate'],
                'densityCellsPerMl': float(np.mean(density[density > 0])),
                'severity': severity,
                'confidence': confidence * 100,  # Convert to percentage
                'visualizations': visualizations,
                'metadata': {
                    'dataSource': 'sentinel2',
                    'processingTime': 0,  # TODO: Add actual processing time
                    'cloudCoverage': data['metadata']['cloudCoverage']
                }
            }
            
        except Exception as e:
            raise Exception(f"CyFi analysis failed: {str(e)}")

    async def get_time_series(self, bbox_coords: dict, start_date: str, end_date: str) -> list:
        """Get time series data for the given area."""
        # TODO: Implement time series analysis
        return []  # Placeholder 