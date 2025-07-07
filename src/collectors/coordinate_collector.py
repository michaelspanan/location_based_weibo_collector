#!/usr/bin/env python3
"""
Coordinate Collector using Amap Coordinate Picker

This script collects coordinates for locations using the Amap coordinate picker webpage.
Uses Selenium to automate the coordinate picker for accurate Chinese location coordinates.
"""

import pandas as pd
import time
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AmapCoordinateCollector:
    """Collect coordinates using Amap coordinate picker webpage."""
    
    def __init__(self, headless=True):
        """
        Initialize the coordinate collector.
        
        Args:
            headless (bool): Run browser in headless mode
        """
        self.headless = headless
        self.driver = None
        self.wait = None
        self.collected_coordinates = {}  # Track to avoid duplicates
        
    def setup_driver(self):
        """Set up the Chrome WebDriver."""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)
            
            logging.info("Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize WebDriver: {e}")
            return False
    
    def search_and_select_location(self, location_name):
        """
        Search for a location and select it from results.
        
        Args:
            location_name (str): Name of the location to search
            
        Returns:
            bool: True if location was found and selected
        """
        try:
            # Find and fill the search input
            search_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "txtSearch"))
            )
            search_input.clear()
            search_input.send_keys(location_name)
            search_input.send_keys(Keys.ENTER)
            
            # Wait for search results (reduced wait time)
            time.sleep(1.5)
            
            # Try multiple strategies to find and select the location
            strategies = [
                # Strategy 1: Look for search result items
                (By.CSS_SELECTOR, ".search-result-item"),
                (By.CSS_SELECTOR, ".poi-item"),
                (By.CSS_SELECTOR, "[class*='result']"),
                (By.CSS_SELECTOR, "[class*='item']"),
                # Strategy 2: Look for any clickable elements with location name
                (By.XPATH, f"//*[contains(text(), '{location_name}')]"),
                # Strategy 3: Look for any div containing the location name
                (By.XPATH, f"//div[contains(text(), '{location_name}')]"),
            ]
            
            for by, selector in strategies:
                try:
                    elements = self.driver.find_elements(by, selector)
                    if elements:
                        # Click the first element that contains the location name
                        for element in elements:
                            if location_name in element.text:
                                element.click()
                                time.sleep(1)
                                return True
                        # If no exact match, click the first element
                        elements[0].click()
                        time.sleep(1)
                        return True
                except:
                    continue
            
            # Strategy 4: Try clicking on the map center
            try:
                map_element = self.driver.find_element(By.ID, "map")
                map_element.click()
                time.sleep(1)
                return True
            except:
                pass
            
            logging.warning(f"Could not select location: {location_name}")
            return False
            
        except Exception as e:
            logging.error(f"Error searching for {location_name}: {e}")
            return False
    
    def get_coordinates(self, location_name):
        """
        Get coordinates for a single location using Amap picker.
        
        Args:
            location_name (str): Name of the location to search
            
        Returns:
            tuple: (latitude, longitude) or (None, None) if failed
        """
        try:
            # Navigate to Amap coordinate picker
            self.driver.get("https://lbs.amap.com/tools/picker")
            time.sleep(2)
            
            # Search and select the location
            if not self.search_and_select_location(location_name):
                logging.warning(f"Could not find/select location: {location_name}")
                return None, None
            
            # Get coordinates from the coordinate display
            coordinate_element = self.wait.until(
                EC.presence_of_element_located((By.ID, "txtCoordinate"))
            )
            
            coordinates = coordinate_element.get_attribute("value")
            
            if coordinates and "," in coordinates:
                # Parse coordinates (Amap returns lng,lat format)
                coords = coordinates.strip().split(",")
                if len(coords) >= 2:
                    lng = float(coords[0].strip())
                    lat = float(coords[1].strip())
                    
                    # Round to 2 decimal places
                    lat = round(lat, 2)
                    lng = round(lng, 2)
                    
                    # Check for duplicates
                    coord_key = f"{lng:.2f},{lat:.2f}"
                    if coord_key in self.collected_coordinates:
                        logging.warning(f"Duplicate coordinates for {location_name}: {coord_key}")
                        logging.warning(f"Already collected for: {self.collected_coordinates[coord_key]}")
                        return None, None
                    
                    # Store to avoid duplicates
                    self.collected_coordinates[coord_key] = location_name
                    
                    return lat, lng
                else:
                    logging.warning(f"Invalid coordinates format for {location_name}")
                    return None, None
            else:
                logging.warning(f"No valid coordinates found for {location_name}")
                return None, None
                
        except TimeoutException:
            logging.error(f"Timeout while collecting coordinates for {location_name}")
            return None, None
        except Exception as e:
            logging.error(f"Error collecting coordinates for {location_name}: {e}")
            return None, None
    
    def collect_coordinates_from_csv(self, input_csv, output_csv, delay=1.0):
        """
        Collect coordinates for all locations in a CSV file.
        
        Args:
            input_csv (str): Path to input CSV with location names
            output_csv (str): Path to output CSV with coordinates
            delay (float): Delay between requests in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read input CSV
            df = pd.read_csv(input_csv)
            
            if 'Location' not in df.columns:
                logging.error("'Location' column not found in input CSV")
                return False
            
            # Setup WebDriver
            if not self.setup_driver():
                return False
            
            # Collect coordinates for each location
            results = []
            total_locations = len(df)
            
            logging.info(f"Starting coordinate collection for {total_locations} locations...")
            logging.info(f"Using delay: {delay}s between requests")
            
            for idx, row in df.iterrows():
                location = row['Location'].strip()
                logging.info(f"Processing {idx + 1}/{total_locations}: {location}")
                
                coords = self.get_coordinates(location)
                
                if coords:
                    lat, lng = coords
                    results.append({
                        'Location': location,
                        'Latitude': f"{lat:.2f}",
                        'Longitude': f"{lng:.2f}",
                        'Coordinates': f"{lng:.2f},{lat:.2f}"
                    })
                    logging.info(f"Success for {location}: {lat:.2f}, {lng:.2f}")
                else:
                    results.append({
                        'Location': location,
                        'Latitude': None,
                        'Longitude': None,
                        'Coordinates': None
                    })
                    logging.warning(f"No coordinates found for {location}")
                
                # Add delay between requests
                if delay > 0 and idx < total_locations - 1:
                    time.sleep(delay)
            
            # Save results
            results_df = pd.DataFrame(results)
            results_df.to_csv(output_csv, index=False, encoding='utf-8')
            
            # Print summary
            successful = len([r for r in results if r['Coordinates'] is not None])
            logging.info(f"\nCoordinate collection completed!")
            logging.info(f"Successful: {successful}/{total_locations}")
            logging.info(f"Failed: {total_locations - successful}/{total_locations}")
            logging.info(f"Results saved to: {output_csv}")
            
            # Show unique coordinates
            unique_coords = set([r['Coordinates'] for r in results if r['Coordinates']])
            logging.info(f"Unique coordinate sets: {len(unique_coords)}")
            
            return True
            
        except Exception as e:
            logging.error(f"Error in coordinate collection: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("WebDriver closed")

def create_location_template(output_file="locations_template.csv"):
    """Create a template CSV file for locations."""
    template_data = {
        'Location': ['北京大学', '清华大学', '复旦大学', '中山大学', '浙江大学']
    }
    
    df = pd.DataFrame(template_data)
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"Location template created: {output_file}")
    print("Template format:")
    print("Location")
    print("北京大学")
    print("清华大学")
    print("...")
    print("\nInstructions:")
    print("1. Add your location names to this CSV")
    print("2. Run: python coordinate_collector.py")
    print("3. Coordinates will be collected automatically")

def main():
    """Main function to run coordinate collection."""
    print("Amap Coordinate Collector (Selenium-based)")
    print("=" * 50)
    
    # Check if input file exists
    input_file = "locations.csv"
    output_file = "locations_with_coordinates.csv"
    
    if not os.path.exists(input_file):
        print(f"{input_file} not found!")
        print("\nCreating template file...")
        create_location_template(input_file)
        print(f"\nTemplate created: {input_file}")
        print("Please add your location names to this file and run again.")
        return
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Delay between requests: 1 second")
    print(f"Features: Amap picker, accurate coordinates, duplicate detection")
    print()
    
    # Initialize collector
    collector = AmapCoordinateCollector(headless=False)  # Set to True for headless mode
    
    # Collect coordinates
    success = collector.collect_coordinates_from_csv(
        input_csv=input_file,
        output_csv=output_file,
        delay=1.0
    )
    
    if success:
        print(f"\nCoordinate collection completed successfully!")
        print(f"Results saved to: {output_file}")
        
        # Show sample results
        try:
            results_df = pd.read_csv(output_file)
            print(f"\nSample results:")
            print(results_df.head())
        except:
            pass
    else:
        print(f"\nCoordinate collection failed. Check logs for details.")

if __name__ == "__main__":
    main() 