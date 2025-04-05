#!/usr/bin/env python
"""
Command line script to analyze a Nigerian bank statement file
"""
import argparse
import json
import time
import os
import sys
import logging
from app.core.pdf_processor import process_pdf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Analyze Nigerian Bank Statement PDF')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('--output', '-o', help='Output JSON file path (optional)')
    parser.add_argument('--pretty', '-p', action='store_true', help='Pretty print JSON output')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    try:
        # Check if file exists
        if not os.path.isfile(args.pdf_path):
            print(f"Error: File '{args.pdf_path}' does not exist")
            return 1
            
        print(f"Analyzing '{args.pdf_path}'...")
        start_time = time.time()
        
        # Process the PDF
        result = process_pdf(args.pdf_path)
        
        # Add processing duration
        result["metadata"]["processing_duration"] = f"{time.time() - start_time:.2f}s"
        
        # Format output
        output = json.dumps(result, indent=2 if args.pretty else None)
        
        # Save to file if specified
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Analysis saved to {args.output}")
        else:
            print(output)
            
        duration = time.time() - start_time
        print(f"Analysis completed in {duration:.2f} seconds")
        
        return 0
            
    except Exception as e:
        if args.debug:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main()) 