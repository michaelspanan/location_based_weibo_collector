#!/usr/bin/env python3
"""
Weibo URL Generator (iframe-only)

This script generates Weibo API URLs for location-based data collection.
It ONLY uses the iframe src extracted from the Weibo Place map page (via Selenium).
If the iframe is not found, the location is skipped.
"""

import pandas as pd
import requests
import time
import logging
import os
import re
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class WeiboURLGenerator:
    """Generate Weibo API URLs for location-based data collection (iframe-only)."""
    
    def __init__(self, cookies_file="cookies.txt"):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://weibo.com/',
            'Origin': 'https://weibo.com'
        })
        self.load_cookies(cookies_file)
        self.driver = None
    
    def load_cookies(self, cookies_file):
        try:
            if not os.path.exists(cookies_file):
                logging.warning(f"Cookies file {cookies_file} not found. Continuing without authentication.")
                return
            with open(cookies_file, 'r', encoding='utf-8') as f:
                cookies_str = f.read().strip()
            for cookie in cookies_str.split(';'):
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    self.session.cookies.set(name.strip(), value.strip())
            logging.info(f"Loaded {len(self.session.cookies)} cookies from {cookies_file}")
        except Exception as e:
            logging.error(f"Error loading cookies: {e}")
    
    def init_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            self.driver = webdriver.Chrome(options=chrome_options)
            logging.info("Selenium WebDriver initialized")
            return True
        except Exception as e:
            logging.error(f"Error initializing WebDriver: {e}")
            return False
    
    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            logging.info("Selenium WebDriver closed")
    
    def get_weibo_place_url(self, coordinates):
        try:
            lng, lat = coordinates.split(',')
            lng = lng.strip()
            lat = lat.strip()
            place_url = f"https://place.weibo.com/wandermap/?maploc={lng},{lat},12z"
            return place_url
        except:
            logging.warning(f"Invalid coordinates format: {coordinates}")
            return None
    
    def extract_cardlist_url_with_selenium(self, place_url, location_name):
        try:
            if not self.driver:
                if not self.init_driver():
                    return None
            logging.info(f"Accessing Weibo Place map with Selenium: {place_url}")
            self.driver.get(place_url)
            wait = WebDriverWait(self.driver, 15)
            try:
                iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
                iframe_src = iframe.get_attribute('src')
                if iframe_src and 'cardlist' in iframe_src:
                    cardlist_url = iframe_src.replace('&amp;', '&')
                    logging.info(f"Found cardlist URL for {location_name}: {cardlist_url}")
                    return cardlist_url
                else:
                    logging.warning(f"No cardlist URL found in iframe src for {location_name}")
                    return None
            except Exception as e:
                logging.warning(f"Timeout waiting for iframe for {location_name}: {e}")
                page_source = self.driver.page_source
                iframe_pattern = r'<iframe[^>]*src="([^"]*cardlist[^"]*)"[^>]*>'
                iframe_matches = re.findall(iframe_pattern, page_source)
                if iframe_matches:
                    cardlist_url = iframe_matches[0].replace('&amp;', '&')
                    logging.info(f"Found cardlist URL in page source for {location_name}: {cardlist_url}")
                    return cardlist_url
                logging.warning(f"No cardlist URL found for {location_name}")
                return None
        except Exception as e:
            logging.error(f"Error extracting cardlist URL for {location_name}: {e}")
            return None
    
    def convert_cardlist_to_api_url(self, cardlist_url, page=1):
        api_url = cardlist_url.replace('/p/cardlist', '/api/container/getIndex')
        if '&page=' in api_url:
            api_url = re.sub(r'&page=\d+', f'&page={page}', api_url)
        else:
            api_url += f'&page={page}'
        return api_url
    
    def generate_api_urls(self, location_name, coordinates, max_pages=1):
        urls = []
        place_url = self.get_weibo_place_url(coordinates)
        if not place_url:
            logging.error(f"Failed to generate place URL for {location_name}")
            return urls
        cardlist_url = self.extract_cardlist_url_with_selenium(place_url, location_name)
        if cardlist_url:
            logging.info(f"Successfully extracted cardlist URL for {location_name}")
            # Generate one meta URL per location
            api_url = self.convert_cardlist_to_api_url(cardlist_url, 1)
            urls.append({
                'Location': location_name,
                'URL_Type': 'container_api',
                'API_URL': api_url,
                'Page': 1,
                'Coordinates': coordinates,
                'Cardlist_URL': cardlist_url,
                'Place_URL': place_url
            })
        else:
            logging.warning(f"No cardlist URL found for {location_name}, skipping.")
        return urls
    
    def generate_urls_from_csv(self, input_csv, output_csv, max_pages=1):
        try:
            df = pd.read_csv(input_csv)
            required_columns = ['Location', 'Coordinates']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logging.error(f"Missing required columns: {missing_columns}")
                return False
            all_urls = []
            total_locations = len(df)
            logging.info(f"Generating meta URLs for {total_locations} locations...")
            for idx, row in df.iterrows():
                location = row['Location'].strip()
                coordinates = row['Coordinates'].strip()
                logging.info(f"Processing {idx + 1}/{total_locations}: {location}")
                location_urls = self.generate_api_urls(location, coordinates, max_pages)
                if location_urls:
                    logging.info(f"{location}: Generated meta URL")
                    all_urls.extend(location_urls)
                else:
                    logging.warning(f"{location}: No URLs generated (iframe not found)")
                if idx < total_locations - 1:
                    time.sleep(2)
            self.close_driver()
            results_df = pd.DataFrame(all_urls)
            results_df.to_csv(output_csv, index=False, encoding='utf-8')
            successful_locations = len(results_df['Location'].unique()) if not results_df.empty else 0
            total_urls = len(results_df)
            logging.info(f"\nURL generation completed!")
            logging.info(f"Locations processed: {total_locations}")
            logging.info(f"Successful locations: {successful_locations}")
            logging.info(f"Meta URLs generated: {total_urls}")
            logging.info(f"Results saved to: {output_csv}")
            return True
        except Exception as e:
            logging.error(f"Error in URL generation: {e}")
            self.close_driver()
            return False

def main():
    print("Weibo URL Generator (iframe-only, Selenium)")
    print("=" * 55)
    input_file = "locations_with_coordinates.csv"
    output_file = "weibo_api_urls_iframe_only.csv"
    if not os.path.exists(input_file):
        print(f"{input_file} not found!")
        print("\nPlease run coordinate collection first to create this file.")
        return
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Meta URLs per location: 1")
    print("Using Selenium to extract ONLY iframe URLs from Weibo Place map")
    print()
    generator = WeiboURLGenerator(cookies_file="cookies.txt")
    success = generator.generate_urls_from_csv(
        input_csv=input_file,
        output_csv=output_file,
        max_pages=1
    )
    if success:
        print(f"\nWeibo URL generation completed successfully!")
        print(f"Results saved to: {output_file}")
        try:
            results_df = pd.read_csv(output_file)
            print(f"\nSample results:")
            print(results_df.head(10))
            if 'URL_Type' in results_df.columns:
                print(f"\nURL types generated:")
                type_counts = results_df['URL_Type'].value_counts()
                for url_type, count in type_counts.items():
                    print(f"  {url_type}: {count} URLs")
        except Exception as e:
            print(f"Error reading results: {e}")
    else:
        print(f"\nURL generation failed. Check logs for details.")

if __name__ == "__main__":
    main() 