#!/usr/bin/env python
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import os

class MLWaterDetector:
    """
    Enhanced water detection using machine learning approaches.
    Combines traditional indices with ML for improved accuracy.
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the ML water detector.
        
        Args:
            model_path: Path to saved model file (optional)
        """
        self.model = None
        self.model_path = model_path
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def prepare_features(self, sentinel_data):
        """
        Prepare feature matrix from Sentinel-2 data.
        
        Args:
            sentinel_data: Dictionary containing band data and indices
            
        Returns:
            numpy array: Feature matrix
        """
        # Extract all relevant bands and indices
        features = []
        
        # Add NDWI
        ndwi = (sentinel_data['B03'] - sentinel_data['B08']) / (sentinel_data['B03'] + sentinel_data['B08'])
        features.append(ndwi.flatten())
        
        # Add individual bands
        for band in ['B02', 'B03', 'B04', 'B08', 'B11', 'B12']:
            if band in sentinel_data:
                features.append(sentinel_data[band].flatten())
        
        # Calculate additional indices
        if all(band in sentinel_data for band in ['B03', 'B08']):
            # MNDWI (Modified NDWI)
            mndwi = (sentinel_data['B03'] - sentinel_data['B11']) / (sentinel_data['B03'] + sentinel_data['B11'])
            features.append(mndwi.flatten())
        
        if all(band in sentinel_data for band in ['B04', 'B08']):
            # NDVI (Normalized Difference Vegetation Index)
            ndvi = (sentinel_data['B08'] - sentinel_data['B04']) / (sentinel_data['B08'] + sentinel_data['B04'])
            features.append(ndvi.flatten())
        
        # Stack features
        feature_matrix = np.vstack(features).T
        return feature_matrix
    
    def train(self, training_data, labels):
        """
        Train the Random Forest model.
        
        Args:
            training_data: Dictionary of Sentinel-2 data for training
            labels: Binary array indicating water (1) vs non-water (0)
        """
        # Prepare features
        X = self.prepare_features(training_data)
        y = labels.flatten()
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Initialize and train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1  # Use all available cores
        )
        
        self.model.fit(X_train, y_train)
        
        # Validate model
        val_predictions = self.model.predict(X_val)
        metrics = {
            'accuracy': accuracy_score(y_val, val_predictions),
            'precision': precision_score(y_val, val_predictions),
            'recall': recall_score(y_val, val_predictions),
            'f1': f1_score(y_val, val_predictions)
        }
        
        print("Validation Metrics:")
        for metric, value in metrics.items():
            print(f"{metric}: {value:.4f}")
        
        return metrics
    
    def predict(self, sentinel_data):
        """
        Predict water bodies using the trained model.
        
        Args:
            sentinel_data: Dictionary containing band data and indices
            
        Returns:
            numpy array: Binary prediction mask (1 for water, 0 for non-water)
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded. Call train() or load_model() first.")
        
        # Prepare features
        X = self.prepare_features(sentinel_data)
        
        # Make predictions
        predictions = self.model.predict(X)
        
        # Reshape back to original dimensions
        original_shape = sentinel_data['B03'].shape
        prediction_mask = predictions.reshape(original_shape)
        
        return prediction_mask
    
    def save_model(self, path):
        """Save the trained model to disk."""
        if self.model is None:
            raise ValueError("No model to save. Train the model first.")
        joblib.dump(self.model, path)
        self.model_path = path
    
    def load_model(self, path):
        """Load a trained model from disk."""
        self.model = joblib.load(path)
        self.model_path = path

def create_training_data(ndwi_data, true_color_data, threshold=0.03):
    """
    Create training data using traditional NDWI threshold as initial labels.
    
    Args:
        ndwi_data: NDWI values
        true_color_data: RGB image data
        threshold: NDWI threshold for water classification
        
    Returns:
        tuple: (features, labels)
    """
    # Create initial labels using NDWI threshold
    labels = (ndwi_data > threshold).astype(int)
    
    # Prepare feature dictionary
    training_data = {
        'B03': true_color_data[:,:,1],  # Green channel
        'B08': ndwi_data,  # NIR (approximated from NDWI calculation)
        'B04': true_color_data[:,:,0],  # Red channel
        'B02': true_color_data[:,:,2]   # Blue channel
    }
    
    return training_data, labels

def enhance_water_detection(ndwi_data, true_color_data, model_path=None):
    """
    Enhance water detection using machine learning.
    
    Args:
        ndwi_data: NDWI values
        true_color_data: RGB image data
        model_path: Path to saved model (optional)
        
    Returns:
        numpy array: Enhanced water detection mask
    """
    # Initialize detector
    detector = MLWaterDetector(model_path)
    
    if detector.model is None:
        # Create training data from traditional method
        training_data, labels = create_training_data(ndwi_data, true_color_data)
        
        # Train model
        print("Training new model...")
        detector.train(training_data, labels)
        
        # Save model if path provided
        if model_path:
            detector.save_model(model_path)
    
    # Make predictions
    prediction_mask = detector.predict(training_data)
    
    return prediction_mask 