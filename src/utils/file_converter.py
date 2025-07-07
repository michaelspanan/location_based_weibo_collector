"""
File Converter Utility

This module provides utilities to convert between different input formats
for the Location-based Weibo Data Collector.
"""

import pandas as pd
import os
import re

class FileConverter:
    """Convert between different input formats."""
    
    @staticmethod
    def convert_coordinates_to_standard_format(input_file, output_file):
        """
        Convert various coordinate formats to the standard format.
        
        Args:
            input_file (str): Path to input file
            output_file (str): Path to output file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read the input file
            df = pd.read_csv(input_file)
            
            # Check what columns we have
            columns = df.columns.tolist()
            
            # Handle different possible formats
            if 'Location' in columns and 'Coordinates' in columns:
                # Already in standard format
                df.to_csv(output_file, index=False, encoding='utf-8')
                return True
                
            elif 'Location' in columns and ('Latitude' in columns or 'lat' in columns):
                # Has separate lat/lng columns
                lat_col = next((col for col in columns if 'lat' in col.lower()), None)
                lng_col = next((col for col in columns if 'lng' in col.lower() or 'lon' in col.lower()), None)
                
                if lat_col and lng_col:
                    df['Coordinates'] = df[lng_col].astype(str) + ',' + df[lat_col].astype(str)
                    df = df[['Location', 'Coordinates']]
                    df.to_csv(output_file, index=False, encoding='utf-8')
                    return True
                    
            elif 'Location' in columns and ('lat' in columns or 'lng' in columns):
                # Has lat/lng as separate columns
                lat_col = next((col for col in columns if 'lat' in col.lower()), None)
                lng_col = next((col for col in columns if 'lng' in col.lower() or 'lon' in col.lower()), None)
                
                if lat_col and lng_col:
                    df['Coordinates'] = df[lng_col].astype(str) + ',' + df[lat_col].astype(str)
                    df = df[['Location', 'Coordinates']]
                    df.to_csv(output_file, index=False, encoding='utf-8')
                    return True
            
            # If we can't determine the format, return False
            print(f"Could not determine coordinate format in {input_file}")
            print(f"Available columns: {columns}")
            return False
            
        except Exception as e:
            print(f"Error converting file: {e}")
            return False
    
    @staticmethod
    def validate_coordinates_file(file_path):
        """
        Validate that a coordinates file is in the correct format.
        
        Args:
            file_path (str): Path to the file to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            df = pd.read_csv(file_path)
            
            # Check required columns
            if 'Location' not in df.columns or 'Coordinates' not in df.columns:
                return False
            
            # Check coordinate format
            for idx, row in df.iterrows():
                coords = str(row['Coordinates'])
                # Should be in format "longitude,latitude"
                if not re.match(r'^-?\d+\.?\d*,-?\d+\.?\d*$', coords):
                    print(f"Invalid coordinate format at row {idx + 1}: {coords}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error validating file: {e}")
            return False
    
    @staticmethod
    def create_locations_from_coordinates(coordinates_file, output_file):
        """
        Create a locations.csv file from a coordinates file.
        
        Args:
            coordinates_file (str): Path to coordinates file
            output_file (str): Path to output locations file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            df = pd.read_csv(coordinates_file)
            
            if 'Location' in df.columns:
                locations_df = df[['Location']].copy()
                locations_df.to_csv(output_file, index=False, encoding='utf-8')
                return True
            else:
                print("No 'Location' column found in coordinates file")
                return False
                
        except Exception as e:
            print(f"Error creating locations file: {e}")
            return False

def main():
    """Command-line interface for file conversion."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert between different input formats')
    parser.add_argument('--input', required=True, help='Input file path')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--type', choices=['coordinates', 'locations'], required=True,
                       help='Type of conversion')
    
    args = parser.parse_args()
    
    converter = FileConverter()
    
    if args.type == 'coordinates':
        success = converter.convert_coordinates_to_standard_format(args.input, args.output)
        if success:
            print(f"Successfully converted coordinates to {args.output}")
        else:
            print("Conversion failed")
            
    elif args.type == 'locations':
        success = converter.create_locations_from_coordinates(args.input, args.output)
        if success:
            print(f"Successfully created locations file: {args.output}")
        else:
            print("Creation failed")

if __name__ == "__main__":
    main() 