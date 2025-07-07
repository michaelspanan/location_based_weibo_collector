#!/usr/bin/env python3
"""
Complete Weibo Data Collection Workflow

This script guides users through the entire process:
1. Collect coordinates for location names
2. Generate API URLs from coordinates
3. Collect Weibo data using the URLs
"""

import os
import sys
import pandas as pd
from src.collectors.coordinate_collector import AmapCoordinateCollector
from src.collectors.url_generator import WeiboURLGenerator
from src.collectors.weibo_collector import WeiboDataCollector

def check_dependencies():
    """Check if all required dependencies are available."""
    print("Checking dependencies...")
    
    try:
        import pandas
        import requests
        import selenium
        from selenium import webdriver
        print("All Python dependencies available")
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    # Check if ChromeDriver is available
    try:
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.quit()
        print("ChromeDriver available")
    except Exception as e:
        print(f"ChromeDriver not available: {e}")
        print("Please install ChromeDriver: https://chromedriver.chromium.org/")
        return False
    
    return True

def detect_existing_files():
    """Detect what files already exist and determine available options."""
    existing_files = {
        'locations': os.path.exists("data/input/locations.csv"),
        'coordinates': os.path.exists("data/intermediate/locations_with_coordinates.csv"),
        'api_urls': os.path.exists("data/intermediate/weibo_api_urls_iframe_only.csv"),
        'collected_data': os.path.exists("data/output/weibo_data_collected.csv"),
        'cookies': os.path.exists("data/input/cookies.txt")
    }
    
    return existing_files

def get_workflow_options(existing_files):
    """Determine available workflow options based on existing files."""
    options = []
    
    # Option 1: Complete workflow (always available)
    options.append("1. Run complete workflow (all steps)")
    
    # Option 2: Start from coordinates (if coordinates exist)
    if existing_files['coordinates']:
        options.append("2. Start from coordinates (skip coordinate collection)")
    
    # Option 3: Start from API URLs (if API URLs exist)
    if existing_files['api_urls']:
        options.append("3. Start from API URLs (skip to data collection)")
    
    # Option 4: Individual steps
    options.append("4. Run individual steps")
    
    # Option 5: Show current status
    options.append("5. Show current status")
    
    # Option 6: Exit
    options.append("6. Exit")
    
    return options

def step1_collect_coordinates():
    """Step 1: Collect coordinates for locations."""
    print("\n" + "="*50)
    print("STEP 1: COLLECT COORDINATES")
    print("="*50)
    
    input_file = "data/input/locations.csv"
    output_file = "data/intermediate/locations_with_coordinates.csv"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"{input_file} not found!")
        print("\nCreating template file...")
        
        # Create template
        template_data = {
            'Location': ['北京大学', '清华大学', '复旦大学', '中山大学', '浙江大学']
        }
        df = pd.DataFrame(template_data)
        df.to_csv(input_file, index=False, encoding='utf-8')
        
        print(f"Template created: {input_file}")
        print("Please edit this file with your location names and run again.")
        return False
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print("This will take a few minutes...")
    
    # Collect coordinates
    collector = AmapCoordinateCollector(headless=False)
    success = collector.collect_coordinates_from_csv(
        input_csv=input_file,
        output_csv=output_file,
        delay=2.0
    )
    
    if success:
        print("Coordinate collection completed!")
        return True
    else:
        print("Coordinate collection failed!")
        return False

def step2_generate_urls():
    """Step 2: Generate API URLs from coordinates."""
    print("\n" + "="*50)
    print("STEP 2: GENERATE API URLS")
    print("="*50)
    
    input_file = "data/intermediate/locations_with_coordinates.csv"
    output_file = "data/intermediate/weibo_api_urls_iframe_only.csv"
    
    if not os.path.exists(input_file):
        print(f"{input_file} not found!")
        print("Please run Step 1 first.")
        return False
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    
    # Generate URLs
    generator = WeiboURLGenerator()
    success = generator.generate_urls_from_csv(
        input_csv=input_file,
        output_csv=output_file,
        max_pages=10
    )
    
    if success:
        print("URL generation completed!")
        return True
    else:
        print("URL generation failed!")
        return False

def step3_collect_data():
    """Step 3: Collect Weibo data."""
    print("\n" + "="*50)
    print("STEP 3: COLLECT WEIBO DATA")
    print("="*50)
    
    input_file = "data/intermediate/weibo_api_urls_iframe_only.csv"
    
    if not os.path.exists(input_file):
        print(f"{input_file} not found!")
        print("Please run Step 2 first.")
        return False
    
    if not os.path.exists("data/input/cookies.txt"):
        print("cookies.txt not found!")
        print("Please create data/input/cookies.txt with your Weibo cookies.")
        return False
    
    print(f"Input file: {input_file}")
    print(f"Cookie file: data/input/cookies.txt")
    print("This will take 10-15 minutes...")
    
    # Collect data
    collector = WeiboDataCollector(
        cookie_file_path="data/input/cookies.txt",
        output_dir="data/output"
    )
    
    success = collector.collect_weibo_data_from_csv(
        csv_file_path=input_file,
        output_file="weibo_data_collected.csv",
        delay_between_requests=1.0,
        auto_extend_pages=True,
        max_pages_to_test=100
    )
    
    if success:
        print("Data collection completed!")
        
        # Analyze results
        output_file = "data/output/weibo_data_collected.csv"
        if os.path.exists(output_file):
            collector.analyze_collected_data(output_file)
        
        return True
    else:
        print("Data collection failed!")
        return False

def workflow_from_coordinates():
    """Run workflow starting from existing coordinates."""
    print("\n" + "="*50)
    print("WORKFLOW: STARTING FROM COORDINATES")
    print("="*50)
    
    if step2_generate_urls():
        step3_collect_data()
        return True
    return False

def workflow_from_api_urls():
    """Run workflow starting from existing API URLs."""
    print("\n" + "="*50)
    print("WORKFLOW: STARTING FROM API URLS")
    print("="*50)
    
    if step3_collect_data():
        return True
        return False

def show_summary():
    """Show summary of collected data."""
    print("\n" + "="*50)
    print("COLLECTION SUMMARY")
    print("="*50)
    
    files_to_check = [
        ("data/input/locations.csv", "Location names"),
        ("data/intermediate/locations_with_coordinates.csv", "Coordinates"),
        ("data/intermediate/weibo_api_urls_iframe_only.csv", "API URLs"),
        ("data/output/weibo_data_collected.csv", "Collected data")
    ]
    
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            if file_path.endswith('.csv'):
                try:
                    df = pd.read_csv(file_path)
                    if 'Location' in df.columns:
                        locations = df['Location'].nunique()
                        print(f"{description}: {locations} locations")
                    else:
                        print(f"{description}: {len(df)} rows")
                except:
                    print(f"{description}: File exists")
            else:
                print(f"{description}: File exists")
        else:
            print(f"{description}: Not found")

def show_individual_steps_menu():
    """Show menu for individual steps."""
    print("\n" + "="*50)
    print("INDIVIDUAL STEPS")
    print("="*50)
    print("1. Step 1: Collect coordinates")
    print("2. Step 2: Generate API URLs")
    print("3. Step 3: Collect Weibo data")
    print("4. Back to main menu")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            step1_collect_coordinates()
            break
        elif choice == "2":
            step2_generate_urls()
            break
        elif choice == "3":
            step3_collect_data()
            break
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please enter 1-4.")

def main():
    """Main workflow function."""
    print("Weibo Data Collection - Complete Workflow")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Detect existing files
    existing_files = detect_existing_files()
    
    # Show current status
    print("\nCurrent Status:")
    show_summary()
    
    # Determine available options
    options = get_workflow_options(existing_files)
    
    # Show workflow options
    print("\n" + "="*50)
    print("WORKFLOW OPTIONS")
    print("="*50)
    
    for option in options:
        print(option)
    
    while True:
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            print("\nRunning complete workflow...")
            
            if step1_collect_coordinates():
                if step2_generate_urls():
                    step3_collect_data()
            
            print("\nWorkflow completed!")
            break
            
        elif choice == "2" and existing_files['coordinates']:
            workflow_from_coordinates()
            print("\nWorkflow completed!")
            break
            
        elif choice == "3" and existing_files['api_urls']:
            workflow_from_api_urls()
            print("\nWorkflow completed!")
            break
            
        elif choice == "4":
            show_individual_steps_menu()
            # After individual steps, show main menu again
            existing_files = detect_existing_files()
            options = get_workflow_options(existing_files)
            print("\n" + "="*50)
            print("WORKFLOW OPTIONS")
            print("="*50)
            for option in options:
                print(option)
            continue
            
        elif choice == "5":
            show_summary()
            break
            
        elif choice == "6":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main() 