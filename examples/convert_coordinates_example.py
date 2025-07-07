#!/usr/bin/env python3
"""
Example: Converting Different Coordinate Formats

This script demonstrates how to convert various coordinate formats
to the standard format required by the Location-based Weibo Data Collector.
"""

import os
import sys
import pandas as pd

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.file_converter import FileConverter

def create_example_files():
    """Create example files in different formats."""
    print("Creating example files...")
    
    # Create examples directory
    os.makedirs("examples", exist_ok=True)
    
    # Example 1: Separate lat/lng columns
    lat_lng_data = {
        'Location': ['北京大学', '清华大学', '复旦大学'],
        'Latitude': [39.9995, 40.0000, 31.2990],
        'Longitude': [116.3074, 116.3264, 121.5034]
    }
    df1 = pd.DataFrame(lat_lng_data)
    df1.to_csv("examples/coordinates_lat_lng.csv", index=False, encoding='utf-8')
    print("Created: examples/coordinates_lat_lng.csv")
    
    # Example 2: Lowercase column names
    lat_lng_lower_data = {
        'Location': ['中山大学', '浙江大学'],
        'lat': [23.0990, 30.2741],
        'lng': [113.2990, 120.1551]
    }
    df2 = pd.DataFrame(lat_lng_lower_data)
    df2.to_csv("examples/coordinates_lat_lng_lower.csv", index=False, encoding='utf-8')
    print("Created: examples/coordinates_lat_lng_lower.csv")
    
    # Example 3: Already in standard format
    standard_data = {
        'Location': ['北京师范大学', '华南理工大学'],
        'Coordinates': ['116.3564,39.9612', '113.3764,23.0489']
    }
    df3 = pd.DataFrame(standard_data)
    df3.to_csv("examples/coordinates_standard.csv", index=False, encoding='utf-8')
    print("Created: examples/coordinates_standard.csv")

def demonstrate_conversion():
    """Demonstrate the conversion process."""
    print("\n" + "="*50)
    print("COORDINATE CONVERSION DEMONSTRATION")
    print("="*50)
    
    converter = FileConverter()
    
    # Convert lat/lng format
    print("\n1. Converting lat/lng format...")
    success = converter.convert_coordinates_to_standard_format(
        "examples/coordinates_lat_lng.csv",
        "examples/converted_lat_lng.csv"
    )
    if success:
        print("Successfully converted lat/lng format")
        df = pd.read_csv("examples/converted_lat_lng.csv")
        print(f"   Result: {len(df)} locations")
        print(f"   Format: {df.columns.tolist()}")
    else:
        print("Conversion failed")
    
    # Convert lowercase format
    print("\n2. Converting lowercase format...")
    success = converter.convert_coordinates_to_standard_format(
        "examples/coordinates_lat_lng_lower.csv",
        "examples/converted_lowercase.csv"
    )
    if success:
        print("Successfully converted lowercase format")
        df = pd.read_csv("examples/converted_lowercase.csv")
        print(f"   Result: {len(df)} locations")
    else:
        print("Conversion failed")
    
    # Validate standard format
    print("\n3. Validating standard format...")
    is_valid = converter.validate_coordinates_file("examples/coordinates_standard.csv")
    if is_valid:
        print("Standard format is valid")
    else:
        print("Standard format is invalid")

def show_usage_instructions():
    """Show how to use the conversion utility."""
    print("\n" + "="*50)
    print("USAGE INSTRUCTIONS")
    print("="*50)
    
    print("\nCommand Line Usage:")
    print("python src/utils/file_converter.py --input your_file.csv --output converted.csv --type coordinates")
    
    print("\nProgrammatic Usage:")
    print("""
from src.utils.file_converter import FileConverter

converter = FileConverter()

# Convert coordinates
success = converter.convert_coordinates_to_standard_format(
    'your_file.csv', 
    'converted.csv'
)

# Validate format
is_valid = converter.validate_coordinates_file('converted.csv')
""")
    
    print("\nSupported Input Formats:")
    print("- Location,Latitude,Longitude")
    print("- Location,lat,lng")
    print("- Location,Coordinates (already standard)")
    
    print("\nOutput Format:")
    print("- Location,Coordinates (longitude,latitude)")

def main():
    """Main demonstration function."""
    print("Coordinate Format Conversion Example")
    print("=" * 50)
    
    # Create example files
    create_example_files()
    
    # Demonstrate conversion
    demonstrate_conversion()
    
    # Show usage instructions
    show_usage_instructions()
    
    print("\n" + "="*50)
    print("DEMONSTRATION COMPLETE")
    print("="*50)
    print("Check the 'examples/' directory for the generated files.")

if __name__ == "__main__":
    main() 