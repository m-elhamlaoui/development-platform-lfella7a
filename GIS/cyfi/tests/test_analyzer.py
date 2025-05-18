import pytest
from datetime import datetime, timedelta
from ..core.analyzer import CyFiAnalyzer

@pytest.fixture
def analyzer():
    """Create a CyFiAnalyzer instance for testing."""
    return CyFiAnalyzer()

@pytest.fixture
def sample_bbox():
    """Create a sample bounding box for testing."""
    return {
        'west': -122.4194,
        'south': 37.7749,
        'east': -122.4094,
        'north': 37.7849
    }

@pytest.fixture
def sample_date():
    """Create a sample date for testing (yesterday to ensure data availability)."""
    return (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

def test_point_grid_generation(analyzer, sample_bbox):
    """Test that the point grid generation works correctly."""
    grid_size = 0.005  # Larger grid size for testing
    points = analyzer._generate_points_grid(sample_bbox, grid_size)
    
    assert len(points) > 0, "Should generate at least one point"
    
    # Check point structure
    first_point = points[0]
    assert 'latitude' in first_point
    assert 'longitude' in first_point
    
    # Check points are within bounds
    for point in points:
        assert sample_bbox['south'] <= point['latitude'] <= sample_bbox['north']
        assert sample_bbox['west'] <= point['longitude'] <= sample_bbox['east']

def test_input_df_creation(analyzer, sample_bbox, sample_date):
    """Test that the input DataFrame is created correctly."""
    points = analyzer._generate_points_grid(sample_bbox, 0.005)
    df = analyzer._create_input_df(points, sample_date)
    
    assert len(df) == len(points), "DataFrame should have same number of rows as points"
    assert all(col in df.columns for col in ['latitude', 'longitude', 'date'])
    assert all(df['date'] == sample_date)

@pytest.mark.asyncio
async def test_point_analysis(analyzer, sample_date):
    """Test single point analysis."""
    # Test coordinates (San Francisco Bay)
    lat, lon = 37.7749, -122.4194
    
    result = await analyzer.analyze_point(lat, lon, sample_date)
    
    assert isinstance(result, dict)
    assert 'timestamp' in result
    assert 'location' in result
    assert 'predictions' in result
    assert 'metadata' in result
    
    # Check predictions structure
    predictions = result['predictions']
    assert 'density_cells_per_ml' in predictions
    assert 'severity' in predictions
    assert predictions['severity'] in ['low', 'moderate', 'high']

@pytest.mark.asyncio
async def test_area_analysis(analyzer, sample_bbox, sample_date):
    """Test area analysis."""
    result = await analyzer.analyze_area(sample_bbox, sample_date, grid_size=0.005)
    
    assert isinstance(result, dict)
    assert 'timestamp' in result
    assert 'bbox' in result
    assert 'predictions' in result
    assert 'metadata' in result
    
    # Check predictions structure
    predictions = result['predictions']
    assert 'density_cells_per_ml' in predictions
    assert 'severity' in predictions
    assert 'confidence' in predictions
    assert predictions['severity'] in ['low', 'moderate', 'high']
    assert 0 <= predictions['confidence'] <= 100

def test_missing_credentials():
    """Test that missing credentials raise appropriate error."""
    with pytest.raises(ValueError) as exc_info:
        # Temporarily modify environment variables
        import os
        os.environ.pop('SENTINEL_CLIENT_ID', None)
        
        # Should raise error due to missing credentials
        CyFiAnalyzer()
    
    assert "Missing Sentinel Hub credentials" in str(exc_info.value) 