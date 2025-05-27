#!/usr/bin/env python3
import sys
import json
import asyncio
from cyfi_analyzer import CyFiAnalyzer

async def main():
    try:
        # Read input from command line argument
        input_data = json.loads(sys.argv[1])
        
        # Initialize analyzer
        analyzer = CyFiAnalyzer()
        
        # Run analysis
        result = await analyzer.analyze(
            bbox_coords=input_data['bbox'],
            time_range=input_data['timeRange']
        )
        
        # Print result as JSON (will be captured by Node.js)
        print(json.dumps(result))
        
    except Exception as e:
        # Print error message to stderr
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze.py '<json-input>'", file=sys.stderr)
        sys.exit(1)
    
    asyncio.run(main()) 