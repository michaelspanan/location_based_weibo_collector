#!/usr/bin/env python3
"""
Flexible Location-based Weibo Data Collector

This script provides a flexible interface for users with different needs:
1. Users with location names only
2. Users with coordinates already
3. Users with API URLs already
4. Users who want to run individual steps
"""

import os
import sys
import pandas as pd

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.workflow import main as run_workflow
from src.utils.file_converter import FileConverter
from src.collectors import AmapCoordinateCollector, WeiboURLGenerator, WeiboDataCollector

def detect_user_scenario():
    """Detect what the user has and suggest the best workflow."""
    print("Location-based Weibo Data Collector - Flexible Interface")
    print("=" * 50)
    
    # Check what files exist
    existing_files = {
        'locations': os.path.exists("data/input/locations.csv"),
        'coordinates': os.path.exists("data/intermediate/locations_with_coordinates.csv"),
        'api_urls': os.path.exists("data/intermediate/weibo_api_urls_iframe_only.csv"),
        'collected_data': os.path.exists("data/output/weibo_data_collected.csv"),
        'cookies': os.path.exists("data/input/cookies.txt")
    }
    
    print("Detecting your current setup...")
    print()
    
    # Determine scenario
    if existing_files['collected_data']:
        print("You have collected data already!")
        print("   - data/output/weibo_data_collected.csv")
        print()
        return "has_data"
        
    elif existing_files['api_urls']:
        print("You have API URLs ready!")
        print("   - data/intermediate/weibo_api_urls_iframe_only.csv")
        print("   - Ready to collect data")
        print()
        return "has_api_urls"
        
    elif existing_files['coordinates']:
        print("You have coordinates ready!")
        print("   - data/intermediate/locations_with_coordinates.csv")
        print("   - Ready to generate API URLs and collect data")
        print()
        return "has_coordinates"
        
    elif existing_files['locations']:
        print("You have location names!")
        print("   - data/input/locations.csv")
        print("   - Ready to collect coordinates")
        print()
        return "has_locations"
        
    else:
        print("No input files found.")
        print("   Please create one of the following:")
        print("   - data/input/locations.csv (location names)")
        print("   - data/intermediate/locations_with_coordinates.csv (coordinates)")
        print("   - data/intermediate/weibo_api_urls_iframe_only.csv (API URLs)")
        print()
        return "no_files"

def show_scenario_options(scenario):
    """Show options based on the detected scenario."""
    print("Available options:")
    print()
    
    if scenario == "has_data":
        print("1. View collected data analysis")
        print("2. Collect more data (if you have new API URLs)")
        print("3. Start fresh with new locations")
        print("4. Exit")
        
    elif scenario == "has_api_urls":
        print("1. Collect data from existing API URLs")
        print("2. Generate new API URLs from coordinates")
        print("3. Start fresh with new locations")
        print("4. Exit")
        
    elif scenario == "has_coordinates":
        print("1. Generate API URLs and collect data")
        print("2. Generate API URLs only")
        print("3. Start fresh with new locations")
        print("4. Exit")
        
    elif scenario == "has_locations":
        print("1. Run complete workflow (coordinates → URLs → data)")
        print("2. Collect coordinates only")
        print("3. Exit")
        
    else:  # no_files
        print("1. Create template files and run complete workflow")
        print("2. Convert existing coordinate files")
        print("3. Exit")

def handle_has_data():
    """Handle scenario where user already has collected data."""
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            # View data analysis
            if os.path.exists("data/output/weibo_data_collected.csv"):
                collector = WeiboDataCollector(
                    cookie_file_path="data/input/cookies.txt",
                    output_dir="data/output"
                )
                collector.analyze_collected_data("data/output/weibo_data_collected.csv")
            break
            
        elif choice == "2":
            # Collect more data
            if os.path.exists("data/intermediate/weibo_api_urls_iframe_only.csv"):
                collector = WeiboDataCollector(
                    cookie_file_path="data/input/cookies.txt",
                    output_dir="data/output"
                )
                collector.collect_weibo_data_from_csv(
                    csv_file_path="data/intermediate/weibo_api_urls_iframe_only.csv",
                    output_file="weibo_data_collected_additional.csv"
                )
            else:
                print("No API URLs found. Please generate them first.")
            break
            
        elif choice == "3":
            # Start fresh
            run_workflow()
            break
            
        elif choice == "4":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter 1-4.")

def handle_has_api_urls():
    """Handle scenario where user has API URLs."""
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            # Collect data
            if os.path.exists("data/input/cookies.txt"):
                collector = WeiboDataCollector(
                    cookie_file_path="data/input/cookies.txt",
                    output_dir="data/output"
                )
                collector.collect_weibo_data_from_csv(
                    csv_file_path="data/intermediate/weibo_api_urls_iframe_only.csv",
                    output_file="weibo_data_collected.csv"
                )
            else:
                print("Please create data/input/cookies.txt first.")
            break
            
        elif choice == "2":
            # Generate new API URLs
            if os.path.exists("data/intermediate/locations_with_coordinates.csv"):
                generator = WeiboURLGenerator()
                generator.generate_urls_from_csv(
                    input_csv="data/intermediate/locations_with_coordinates.csv",
                    output_csv="data/intermediate/weibo_api_urls_iframe_only.csv"
                )
            else:
                print("No coordinates found. Please collect coordinates first.")
            break
            
        elif choice == "3":
            # Start fresh
            run_workflow()
            break
            
        elif choice == "4":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter 1-4.")

def handle_has_coordinates():
    """Handle scenario where user has coordinates."""
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            # Generate URLs and collect data
            generator = WeiboURLGenerator()
            if generator.generate_urls_from_csv(
                input_csv="data/intermediate/locations_with_coordinates.csv",
                output_csv="data/intermediate/weibo_api_urls_iframe_only.csv"
            ):
                if os.path.exists("data/input/cookies.txt"):
                    collector = WeiboDataCollector(
                        cookie_file_path="data/input/cookies.txt",
                        output_dir="data/output"
                    )
                    collector.collect_weibo_data_from_csv(
                        csv_file_path="data/intermediate/weibo_api_urls_iframe_only.csv",
                        output_file="weibo_data_collected.csv"
                    )
                else:
                    print("Please create data/input/cookies.txt first.")
            break
            
        elif choice == "2":
            # Generate URLs only
            generator = WeiboURLGenerator()
            generator.generate_urls_from_csv(
                input_csv="data/intermediate/locations_with_coordinates.csv",
                output_csv="data/intermediate/weibo_api_urls_iframe_only.csv"
            )
            break
            
        elif choice == "3":
            # Start fresh
            run_workflow()
            break
            
        elif choice == "4":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter 1-4.")

def handle_has_locations():
    """Handle scenario where user has location names."""
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            # Run complete workflow
            run_workflow()
            break
            
        elif choice == "2":
            # Collect coordinates only
            collector = AmapCoordinateCollector(headless=False)
            collector.collect_coordinates_from_csv(
                input_csv="data/input/locations.csv",
                output_csv="data/intermediate/locations_with_coordinates.csv"
            )
            break
            
        elif choice == "3":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter 1-3.")

def handle_no_files():
    """Handle scenario where user has no files."""
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            # Create template and run workflow
            print("Creating template files...")
            
            # Create locations template
            os.makedirs("data/input", exist_ok=True)
            template_data = {
                'Location': ['北京大学', '清华大学', '复旦大学', '中山大学', '浙江大学']
            }
            df = pd.DataFrame(template_data)
            df.to_csv("data/input/locations.csv", index=False, encoding='utf-8')
            
            print("Created data/input/locations.csv")
            print("Please edit this file with your location names, then run again.")
            break
            
        elif choice == "2":
            # Convert existing coordinate files
            print("File conversion utility")
            print("Please use the command line interface:")
            print("python src/utils/file_converter.py --input your_file.csv --output data/intermediate/locations_with_coordinates.csv --type coordinates")
            break
            
        elif choice == "3":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter 1-3.")

def main():
    """Main function for flexible collector."""
    # Detect user scenario
    scenario = detect_user_scenario()
    
    # Show options based on scenario
    show_scenario_options(scenario)
    
    # Handle the scenario
    if scenario == "has_data":
        handle_has_data()
    elif scenario == "has_api_urls":
        handle_has_api_urls()
    elif scenario == "has_coordinates":
        handle_has_coordinates()
    elif scenario == "has_locations":
        handle_has_locations()
    else:  # no_files
        handle_no_files()

if __name__ == "__main__":
    main() 