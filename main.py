#!/usr/bin/env python3
"""
Location-based Weibo Data Collector - Main Entry Point

This script provides the main entry point for the Location-based Weibo Data Collector.
It can be used to run the complete workflow or individual steps.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.workflow import main as run_workflow

def main():
    """Main entry point for the Location-based Weibo Data Collector."""
    print("Location-based Weibo Data Collector v1.0.0")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("src"):
        print("Error: Please run this script from the project root directory.")
        print("Current directory:", os.getcwd())
        print("Expected structure: weibo-data-collector/")
        sys.exit(1)
    
    # Run the workflow
    run_workflow()

if __name__ == "__main__":
    main() 