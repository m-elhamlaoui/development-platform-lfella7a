import asyncio
from analyzer import CyFiAnalyzer
import json
from datetime import datetime, timedelta

async def test_analyzer():
    # Test coordinates for Barcelona coast
    test_bbox = {
        'west': 2.1,
        'south': 41.3,
        'east': 2.3,
        'north': 41.4
    }
    
    # Use yesterday's date to ensure data availability
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        print("Initializing CyFi Analyzer...")
        analyzer = CyFiAnalyzer()
        
        print(f"Running analysis for date: {yesterday}")
        print(f"Coordinates: {json.dumps(test_bbox, indent=2)}")
        
        result = await analyzer.analyze_area(
            bbox=test_bbox,
            date=yesterday,
            grid_size=0.01  # Larger grid size for testing
        )
        
        print("\nAnalysis Results:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        raise

if __name__ == "__main__":
    print("Starting CyFi Analyzer test...")
    asyncio.run(test_analyzer()) 