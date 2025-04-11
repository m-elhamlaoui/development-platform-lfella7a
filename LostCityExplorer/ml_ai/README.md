# ML/AI Development Guide - Python

This directory contains the Machine Learning and AI components for the Lost City Explorer application, built with Python.

## Setup Instructions

### Prerequisites

- Python 3.9 or later
- pip
- Docker (for containerized development)
- CUDA-capable GPU (recommended for training models)

### Project Setup

1. Set up a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. The directory already contains:
   - `app.py`: A minimal Flask application with health check endpoint
   - `requirements.txt`: Basic dependencies for ML/AI development
   - `Dockerfile`: Configuration for containerized development

### Project Structure

Organize your codebase as follows:

```
ml_ai/
├── app.py                    # Flask API entry point
├── requirements.txt          # Python dependencies
├── models/                   # Trained ML models
│   ├── feature_detection/    # Models for detecting archaeological features
│   └── terrain_analysis/     # Models for terrain analysis
├── data/                     # Data processing and management
│   ├── preprocessing/        # Scripts for data preprocessing
│   ├── augmentation/         # Data augmentation utilities
│   └── loaders/              # Data loading utilities
├── training/                 # Model training scripts
│   ├── feature_detection/    # Training scripts for feature detection
│   └── terrain_analysis/     # Training scripts for terrain analysis
├── inference/                # Inference and prediction modules
│   ├── api/                  # API endpoints for inference
│   └── batch/                # Batch processing scripts
├── utils/                    # Utility functions and helpers
├── tests/                    # Unit and integration tests
├── notebooks/                # Jupyter notebooks for experimentation
└── Dockerfile                # Docker configuration
```

### Key Implementation Tasks

1. Implement satellite imagery preprocessing:
   - Normalization and standardization
   - Band selection and combination
   - Image enhancement techniques

2. Develop feature detection models:
   - CNN-based architecture for archaeological feature detection
   - Transfer learning with pre-trained models (ResNet, EfficientNet)
   - Anomaly detection for identifying unusual patterns

3. Create terrain analysis algorithms:
   - Water proximity analysis
   - Elevation pattern recognition
   - Vegetation index calculation and analysis

4. Implement API endpoints:
   - Image analysis endpoints
   - Model training and fine-tuning endpoints
   - Batch processing capabilities

### Docker Development

The Dockerfile is already configured. To build and run:

```bash
docker build -t lostcity-ml .
docker run -p 5000:5000 lostcity-ml
```

Or use docker-compose from the project root:

```bash
cd ..
docker-compose up -d ml_ai
```

This will start the ML/AI service at http://localhost:5000.

### Data Management

For model training, you'll need to manage datasets:

1. Create a data directory structure:

```bash
mkdir -p data/{raw,processed,augmented}
```

2. Set up data version control (recommended):

```bash
pip install dvc
dvc init
dvc add data/raw
```

3. For large datasets, consider using cloud storage with appropriate access controls.

### Example Inference Endpoint

Implement an image analysis endpoint in `app.py`:

```python
@app.route('/api/analyze/features', methods=['POST'])
def analyze_features():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
        
    image_file = request.files['image']
    img = preprocess_image(image_file)
    
    # Run inference with model
    results = model.predict(img)
    
    # Process and format results
    formatted_results = post_process_results(results)
    
    return jsonify({
        'features': formatted_results,
        'confidence': float(results.confidence),
        'processing_time': results.processing_time
    })
```

### Model Training

Set up a training pipeline in `training/feature_detection/train.py`:

```python
def train_model(data_path, output_path, epochs=100, batch_size=32):
    # Load and preprocess data
    train_data, val_data = load_data(data_path)
    
    # Define model architecture
    model = build_model()
    
    # Train model
    model.fit(
        train_data,
        validation_data=val_data,
        epochs=epochs,
        batch_size=batch_size
    )
    
    # Save model
    model.save(output_path)
    
    return model
```

## Integration Points

The ML/AI service will need to interact with:
- The backend service for data access and result storage
- The frontend for visualizing analysis results
- The GIS Tools service for spatial context and analysis

## Additional Resources

- [TensorFlow Documentation](https://www.tensorflow.org/api_docs)
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [Scikit-learn Documentation](https://scikit-learn.org/stable/) 