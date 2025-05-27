#!/usr/bin/env python3
import sys
import json
import asyncio
from analyzer import CyFiAnalyzer

async def main():
    try:
        # Parse input JSON from command line argument
        input_data = json.loads(sys.argv[1])
        
        # Extract parameters
        bbox = input_data['bbox']
        date = input_data['date']
        grid_size = input_data.get('grid_size', 0.001)
        
        # Initialize analyzer
        analyzer = CyFiAnalyzer()
        
        # Run analysis
        result = await analyzer.analyze_area(bbox, date, grid_size)
        
        # Output result as JSON
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        error_response = {
            'error': True,
            'message': str(e)
        }
        print(json.dumps(error_response), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main()) 