"""
Sen2Coral Bridge - Java-Python Communication Interface
"""
import subprocess
import json
import tempfile
import os
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np

logger = logging.getLogger(__name__)

class Sen2CoralBridge:
    """
    Bridge between Python API and Sen2Coral Java toolbox
    """
    
    def __init__(self, sen2coral_path: Optional[str] = None, java_executable: str = "java"):
        """
        Initialize the Sen2Coral bridge
        
        Args:
            sen2coral_path: Path to Sen2Coral toolbox installation
            java_executable: Path to Java executable
        """
        self.sen2coral_path = Path(sen2coral_path) if sen2coral_path else self._find_sen2coral_path()
        self.java_executable = java_executable
        self.mock_mode = not self._validate_sen2coral_installation()
        
        if self.mock_mode:
            logger.warning("Sen2Coral toolbox not found. Running in mock mode.")
        else:
            logger.info(f"Sen2Coral bridge initialized with toolbox at: {self.sen2coral_path}")
    
    def _find_sen2coral_path(self) -> Path:
        """
        Attempt to find Sen2Coral installation
        
        Returns:
            Path to Sen2Coral toolbox
        """
        # Check common installation locations
        possible_paths = [
            Path("../sen2coral_toolbox/sen2coral-box"),
            Path("./sen2coral_toolbox/sen2coral-box"),
            Path(os.path.expanduser("~/sen2coral-box")),
            Path("/opt/sen2coral-box"),
            Path("C:/Program Files/sen2coral-box"),
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "bin").exists():
                return path
        
        # Default path for development
        return Path("../sen2coral_toolbox/sen2coral-box")
    
    def _validate_sen2coral_installation(self) -> bool:
        """
        Validate that Sen2Coral is properly installed
        
        Returns:
            True if Sen2Coral is available, False otherwise
        """
        try:
            # Check if the main Sen2Coral directory exists
            if not self.sen2coral_path.exists():
                logger.warning(f"Sen2Coral path does not exist: {self.sen2coral_path}")
                return False
            
            # Check for essential Sen2Coral components
            required_components = [
                "bin",
                "lib", 
                "modules"
            ]
            
            for component in required_components:
                component_path = self.sen2coral_path / component
                if not component_path.exists():
                    logger.warning(f"Missing Sen2Coral component: {component_path}")
                    return False
            
            # Check if Java is available
            try:
                result = subprocess.run([self.java_executable, "-version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    logger.warning("Java executable not found or not working")
                    return False
            except Exception as e:
                logger.warning(f"Error checking Java: {str(e)}")
                return False
            
            logger.info("Sen2Coral installation validated successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Error validating Sen2Coral installation: {str(e)}")
            return False
    
    def run_analysis(self, input_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Sen2Coral analysis
        
        Args:
            input_params: Analysis parameters
            
        Returns:
            Analysis results
        """
        if self.mock_mode:
            return self._mock_analysis(input_params)
        else:
            return self._real_analysis(input_params)
    
    def _real_analysis(self, input_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute real Sen2Coral analysis using Java bridge
        
        Args:
            input_params: Analysis parameters
            
        Returns:
            Analysis results
        """
        input_file = None
        output_file = None
        
        try:
            logger.info("Starting Sen2Coral analysis")
            
            # Create temporary input file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(input_params, f, indent=2)
                input_file = f.name
            
            # Create temporary output file
            output_file = tempfile.mktemp(suffix='.json')
            
            # Build Sen2Coral command
            # Note: This is a simplified command structure. 
            # The actual Sen2Coral command line interface may differ
            cmd = self._build_sen2coral_command(input_file, output_file, input_params)
            
            logger.info(f"Executing Sen2Coral command: {' '.join(cmd)}")
            
            # Execute Sen2Coral with timeout
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            execution_time = time.time() - start_time
            
            if result.returncode != 0:
                error_msg = f"Sen2Coral execution failed with return code {result.returncode}"
                if result.stderr:
                    error_msg += f": {result.stderr}"
                raise Exception(error_msg)
            
            # Read results
            if not os.path.exists(output_file):
                raise Exception("Sen2Coral did not produce output file")
            
            with open(output_file, 'r') as f:
                results = json.load(f)
            
            # Add execution metadata
            results['metadata'] = results.get('metadata', {})
            results['metadata']['execution_time'] = execution_time
            results['metadata']['algorithm_version'] = self._get_sen2coral_version()
            
            logger.info(f"Sen2Coral analysis completed in {execution_time:.2f} seconds")
            return results
            
        except subprocess.TimeoutExpired:
            raise Exception("Sen2Coral analysis timed out after 5 minutes")
        except Exception as e:
            logger.error(f"Sen2Coral analysis failed: {str(e)}")
            raise Exception(f"Sen2Coral bridge error: {str(e)}")
        finally:
            # Cleanup temporary files
            if input_file and os.path.exists(input_file):
                os.unlink(input_file)
            if output_file and os.path.exists(output_file):
                os.unlink(output_file)
    
    def _build_sen2coral_command(self, input_file: str, output_file: str, params: Dict[str, Any]) -> List[str]:
        """
        Build Sen2Coral command line
        
        Args:
            input_file: Path to input parameter file
            output_file: Path to output results file
            params: Analysis parameters
            
        Returns:
            Command line arguments
        """
        # This is a simplified command structure
        # The actual Sen2Coral command line interface may be different
        cmd = [
            self.java_executable,
            "-Xmx4G",  # Allocate 4GB memory
            "-jar", str(self.sen2coral_path / "bin" / "sen2coral.jar"),
            "--input", input_file,
            "--output", output_file,
            "--format", "json"
        ]
        
        # Add analysis type specific parameters
        analysis_type = params.get('analysisType', 'water_quality')
        cmd.extend(["--analysis", analysis_type])
        
        # Add data source
        data_source = params.get('dataSource', 'sentinel2')
        cmd.extend(["--source", data_source])
        
        # Add optional parameters
        options = params.get('options', {})
        if 'cloudMaskThreshold' in options:
            cmd.extend(["--cloud-threshold", str(options['cloudMaskThreshold'])])
        
        return cmd
    
    def _get_sen2coral_version(self) -> str:
        """
        Get Sen2Coral version information
        
        Returns:
            Version string
        """
        try:
            cmd = [
                self.java_executable,
                "-jar", str(self.sen2coral_path / "bin" / "sen2coral.jar"),
                "--version"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        return "unknown"
    
    def _mock_analysis(self, input_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock Sen2Coral analysis for testing when toolbox is not available
        
        Args:
            input_params: Analysis parameters
            
        Returns:
            Mock analysis results
        """
        logger.info("Running mock Sen2Coral analysis")
        
        # Simulate processing time
        time.sleep(1)
        
        # Extract parameters
        bbox = input_params.get('bbox', [-122.52, 37.70, -122.15, 37.90])
        analysis_type = input_params.get('analysisType', 'water_quality')
        data_source = input_params.get('dataSource', 'sentinel2')
        
        # Calculate area for realistic mock data
        area_deg = abs(bbox[2] - bbox[0]) * abs(bbox[3] - bbox[1])
        
        # Generate mock results based on analysis type
        results = {
            "bbox": {
                "west": bbox[0],
                "south": bbox[1],
                "east": bbox[2],
                "north": bbox[3]
            },
            "timestamp": "2025-01-26T12:00:00Z",
            "analysisType": analysis_type,
            "dataSource": data_source
        }
        
        # Water quality metrics
        if analysis_type in ["water_quality", "change_detection"]:
            results["waterQuality"] = {
                "ndwi": 0.75 + (area_deg * 0.1),
                "clarity": 0.82 - (area_deg * 0.05),
                "turbidity": 0.15 + (area_deg * 0.02),
                "chlorophyll": 0.25 + (area_deg * 0.03),
                "dissolvedOrganics": 0.18 + (area_deg * 0.01)
            }
        
        # Habitat mapping
        if analysis_type in ["habitat", "change_detection"]:
            results["habitat"] = {
                "coralCover": max(0, 45.2 - (area_deg * 20)),
                "seagrassCover": 23.8 + (area_deg * 10),
                "sandCover": 31.0 + (area_deg * 5),
                "rockCover": 0.0,
                "classification": {
                    "healthy_coral": max(0, 35.2 - (area_deg * 15)),
                    "stressed_coral": max(0, 10.0 - (area_deg * 5)),
                    "dense_seagrass": 15.8 + (area_deg * 8),
                    "sparse_seagrass": 8.0 + (area_deg * 2),
                    "sand": 31.0 + (area_deg * 5)
                }
            }
        
        # Bathymetry
        if analysis_type in ["bathymetry", "change_detection"]:
            results["bathymetry"] = {
                "meanDepth": 12.5 + (area_deg * 20),
                "minDepth": 2.1,
                "maxDepth": 25.8 + (area_deg * 50),
                "depthConfidence": max(0.5, 0.87 - (area_deg * 0.1))
            }
        
        # Change detection
        if analysis_type == "change_detection":
            results["changeDetection"] = {
                "waterQualityChange": -5.2,
                "habitatChange": -8.1,
                "depthChange": 0.3,
                "changeConfidence": 0.78
            }
        
        # Generate mock GeoJSON
        results["geojson"] = self._generate_mock_geojson(bbox, analysis_type)
        
        # Metadata
        results["metadata"] = {
            "processingTime": 1.0,
            "cloudCover": 12.5,
            "dataQuality": 0.92,
            "algorithmVersion": "2.1.0-mock",
            "timestamp": "2025-01-26T12:00:00Z",
            "inputParameters": input_params,
            "mock": True
        }
        
        return results
    
    def _generate_mock_geojson(self, bbox: List[float], analysis_type: str) -> Dict[str, Any]:
        """
        Generate mock GeoJSON data for testing
        
        Args:
            bbox: Bounding box coordinates [west, south, east, north]
            analysis_type: Type of analysis
            
        Returns:
            Mock GeoJSON feature collection
        """
        west, south, east, north = bbox
        
        # Create a simple polygon covering the bbox
        polygon_coords = [[
            [west, south],
            [east, south],
            [east, north],
            [west, north],
            [west, south]
        ]]
        
        features = []
        
        if analysis_type == "water_quality":
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": polygon_coords
                },
                "properties": {
                    "analysisType": "water_quality",
                    "metrics": {
                        "ndwi": 0.75,
                        "clarity": 0.82,
                        "turbidity": 0.15
                    },
                    "confidence": 0.92
                }
            })
        
        elif analysis_type == "habitat":
            # Create multiple habitat zones
            mid_lon = (west + east) / 2
            mid_lat = (south + north) / 2
            
            # Coral zone
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [west, south],
                        [mid_lon, south],
                        [mid_lon, mid_lat],
                        [west, mid_lat],
                        [west, south]
                    ]]
                },
                "properties": {
                    "analysisType": "habitat",
                    "habitatType": "coral",
                    "metrics": {"coralCover": 65.2},
                    "confidence": 0.88
                }
            })
            
            # Seagrass zone
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [mid_lon, south],
                        [east, south],
                        [east, mid_lat],
                        [mid_lon, mid_lat],
                        [mid_lon, south]
                    ]]
                },
                "properties": {
                    "analysisType": "habitat",
                    "habitatType": "seagrass",
                    "metrics": {"seagrassCover": 78.5},
                    "confidence": 0.85
                }
            })
        
        elif analysis_type == "bathymetry":
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": polygon_coords
                },
                "properties": {
                    "analysisType": "bathymetry",
                    "metrics": {
                        "meanDepth": 12.5,
                        "minDepth": 2.1,
                        "maxDepth": 25.8
                    },
                    "confidence": 0.87
                }
            })
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get Sen2Coral system capabilities
        
        Returns:
            System capabilities information
        """
        capabilities = {
            "available": not self.mock_mode,
            "version": self._get_sen2coral_version() if not self.mock_mode else "mock",
            "analysisTypes": ["water_quality", "habitat", "bathymetry", "change_detection"],
            "supportedSatellites": ["sentinel2", "landsat8"],
            "algorithms": {
                "sambuca": {
                    "available": not self.mock_mode,
                    "description": "Semi-analytical model for bathymetry, un-mixing, and concentration assessment"
                },
                "habitat_mapping": {
                    "available": not self.mock_mode,
                    "description": "Machine learning-based coral reef habitat classification"
                },
                "water_quality": {
                    "available": True,
                    "description": "Advanced water quality parameter estimation"
                }
            }
        }
        
        if self.mock_mode:
            capabilities["note"] = "Running in mock mode - Sen2Coral toolbox not available"
        
        return capabilities 