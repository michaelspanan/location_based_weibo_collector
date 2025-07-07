import pandas as pd
import requests
import json
import time
from datetime import datetime
import re
import os
from typing import List, Dict, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weibo_collection.log'),
        logging.StreamHandler()
    ]
)

class WeiboDataCollector:
    """
    Enhanced location-based Weibo data collector with improved features and error handling.
    """
    
    def __init__(self, cookie_file_path: str, output_dir: str = "data"):
        """
        Initialize the location-based Weibo data collector.
        
        Args:
            cookie_file_path (str): Path to cookie file
            output_dir (str): Directory to save output files
        """
        self.cookie_file_path = cookie_file_path
        self.output_dir = output_dir
        self.cookies = self._load_cookies()
        self.session = requests.Session()
        self._setup_session()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_posts': 0,
            'start_time': datetime.now()
        }
    
    def _load_cookies(self) -> str:
        """Load cookies from file."""
        try:
            with open(self.cookie_file_path, 'r', encoding='utf-8') as f:
                cookies = f.read().strip()
            logging.info(f"Cookies loaded from {self.cookie_file_path}")
            return cookies
        except Exception as e:
            logging.error(f"Error loading cookies: {e}")
            return ""
    
    def _setup_session(self):
        """Setup session with headers and cookies."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://m.weibo.cn/',
            'Connection': 'keep-alive',
            'Cookie': self.cookies
        }
        self.session.headers.update(headers)
    
    def extract_mblog_info(self, mblog: Dict, coordinates: str = '') -> Dict:
        """
        Extract specific information from a single mblog object.
        
        Args:
            mblog (dict): Mblog object from Weibo API
            
        Returns:
            dict: Extracted Weibo information with only required fields
        """
        # Validate mblog is a dictionary
        if not isinstance(mblog, dict):
            logging.warning(f"Mblog is not a dictionary: {type(mblog)}")
            return {}
        
        user = mblog.get('user', {})
        if not isinstance(user, dict):
            logging.warning(f"User field is not a dictionary: {type(user)}")
            user = {}
        
        # Extract and clean text content
        raw_text = mblog.get('text', '')
        
        # Remove content after "全文" (full text) link
        if '<a href="/status/' in raw_text and '">全文</a>' in raw_text:
            # Find the position of the "全文" link and cut the text there
            full_text_start = raw_text.find('<a href="/status/')
            if full_text_start != -1:
                # Find the end of the "全文" link
                full_text_end = raw_text.find('">全文</a>', full_text_start)
                if full_text_end != -1:
                    # Remove everything from the start of the link onwards
                    raw_text = raw_text[:full_text_start].strip()
        
        # Remove HTML tags and noise, keeping meaningful text content
        import re
        from bs4 import BeautifulSoup
        
        # Remove HTML tags but preserve text content
        if raw_text:
            soup = BeautifulSoup(raw_text, 'html.parser')
            raw_text = soup.get_text()
        
        # Remove URLs but keep other text
        raw_text = re.sub(r'http[s]?://[^\s]+', '', raw_text)
        
        # Remove location references (like "北京·静园(北京大学校本部)") since we have location column
        raw_text = re.sub(r'[^\s]*·[^\s]*\([^)]*\)', '', raw_text)  # Remove "城市·地点(描述)" pattern
        raw_text = re.sub(r'[^\s]*·[^\s]*', '', raw_text)  # Remove "城市·地点" pattern
        
        # Clean up extra whitespace and normalize
        raw_text = re.sub(r'\s+', ' ', raw_text).strip()
        
        # Extract only the required fields
        weibo_info = {
            # Post information
            'mid': mblog.get('mid', ''),
            'created_at': mblog.get('created_at', ''),
            'text': raw_text,
            'text_length': len(raw_text),
            'source': mblog.get('source', ''),
            'favorited': mblog.get('favorited', False),
            'reposts_count': mblog.get('reposts_count', 0),
            'comments_count': mblog.get('comments_count', 0),
            'attitudes_count': mblog.get('attitudes_count', 0),
            'pic_num': mblog.get('pic_num', 0),
            
            # User information
            'user_id': user.get('id', ''),
            'screen_name': user.get('screen_name', ''),
            'follow_count': user.get('follow_count', 0),
            'followers_count': user.get('followers_count', 0),
            'statuses_count': user.get('statuses_count', 0),
            'verified': user.get('verified', False),
            'verified_type': user.get('verified_type', -1),
            'gender': user.get('gender', ''),
            
            # Additional metadata
            'retweeted_status': bool(mblog.get('retweeted_status')),
            'is_long_text': mblog.get('isLongText', False),
        }
        
        # Extract image URLs
        pics = mblog.get('pics', [])
        if isinstance(pics, list) and pics:
            pic_urls = []
            for pic in pics:
                if isinstance(pic, dict):
                    pic_url = pic.get('url', '')
                    if pic_url:
                        pic_urls.append(pic_url)
            weibo_info['pic_urls'] = '; '.join(pic_urls)
        else:
            weibo_info['pic_urls'] = ''
        
        # Add coordinates as the last column
        weibo_info['coordinates'] = coordinates
        
        return weibo_info
    
    def extract_weibo_info_from_json(self, json_data: Dict, coordinates: str = '', location: str = '', page: int = 0) -> List[Dict]:
        """
        Extract Weibo posts from API JSON response.
        
        Args:
            json_data (dict): JSON response from Weibo API
            coordinates (str): Location coordinates
            location (str): Location name for logging
            page (int): Page number for logging
            
        Returns:
            list: List of Weibo post information
        """
        weibo_posts = []
        
        try:
            # Check if json_data is actually a dictionary
            if not isinstance(json_data, dict):
                logging.warning(f"API response is not a dictionary: {type(json_data)}")
                return weibo_posts
            
            # Check for "no content" response - this indicates end of data
            if json_data.get('ok') == 0 and json_data.get('msg') == '这里还没有内容':
                logging.info(f"{location} Page {page}: No content available (end of data)")
                return weibo_posts
            
            # Check for other error responses
            if json_data.get('ok') != 1:
                logging.warning(f"{location} Page {page}: API response indicates error: {json_data.get('msg', 'Unknown error')}")
                return weibo_posts
            
            data = json_data.get('data', {})
            if not isinstance(data, dict):
                logging.warning(f"Data field is not a dictionary: {type(data)}")
                return weibo_posts
            
            cards = data.get('cards', [])
            if not isinstance(cards, list):
                logging.warning(f"Cards field is not a list: {type(cards)}")
                return weibo_posts
            
            for card in cards:
                # Check if card is a dictionary
                if not isinstance(card, dict):
                    logging.warning(f"Card is not a dictionary: {type(card)}")
                    continue
                
                # Handle different card types
                if card.get('card_type') == 9:  # Direct Weibo post
                    mblog = card.get('mblog', {})
                    if isinstance(mblog, dict) and mblog:
                        weibo_info = self.extract_mblog_info(mblog, coordinates)
                        weibo_posts.append(weibo_info)
                
                elif card.get('card_type') == 11:  # Card group container
                    card_group = card.get('card_group', [])
                    if not isinstance(card_group, list):
                        logging.warning(f"Card group is not a list: {type(card_group)}")
                        continue
                    
                    for group_item in card_group:
                        if not isinstance(group_item, dict):
                            logging.warning(f"Group item is not a dictionary: {type(group_item)}")
                            continue
                            
                        if group_item.get('card_type') == 9:  # Weibo post in card group
                            mblog = group_item.get('mblog', {})
                            if isinstance(mblog, dict) and mblog:
                                weibo_info = self.extract_mblog_info(mblog, coordinates)
                                weibo_posts.append(weibo_info)
            
            return weibo_posts
            
        except Exception as e:
            logging.error(f"Error extracting Weibo info from JSON: {e}")
            return weibo_posts
    
    def fetch_weibo_data_from_api(self, api_url: str, location: str, page: int, 
                                 coordinates: str = '', retry_count: int = 3, delay: float = 1.0) -> Tuple[List[Dict], bool]:
        """
        Fetch Weibo data from API URL with retry mechanism.
        
        Args:
            api_url (str): API URL to fetch data from
            location (str): Location name
            page (int): Page number
            retry_count (int): Number of retries on failure
            delay (float): Delay between requests in seconds
            
        Returns:
            tuple: (List of Weibo post information, bool indicating if this is the end of data)
        """
        self.stats['total_requests'] += 1
        
        for attempt in range(retry_count):
            try:
                logging.info(f"Fetching {location} Page {page} (attempt {attempt + 1}/{retry_count})")
                
                response = self.session.get(api_url, timeout=15)
                
                if response.status_code == 200:
                    try:
                        json_data = response.json()
                        
                        # Log response structure for debugging
                        if isinstance(json_data, dict):
                            logging.debug(f"{location} Page {page}: Response keys: {list(json_data.keys())}")
                            
                            if 'ok' in json_data:
                                logging.debug(f"{location} Page {page}: ok = {json_data['ok']}")
                            
                            if 'data' in json_data:
                                data = json_data['data']
                                if isinstance(data, dict) and 'cards' in data:
                                    cards = data['cards']
                                    if isinstance(cards, list):
                                        logging.info(f"{location} Page {page}: Found {len(cards)} cards")
                                        
                                        # Count card types
                                        card_types = {}
                                        for card in cards:
                                            if isinstance(card, dict):
                                                card_type = card.get('card_type', 'unknown')
                                                card_types[card_type] = card_types.get(card_type, 0) + 1
                                        logging.debug(f"{location} Page {page}: Card types: {card_types}")
                        
                        weibo_posts = self.extract_weibo_info_from_json(json_data, coordinates, location, page)
                        
                        # Check if this is the end of data (no content response)
                        is_end_of_data = (json_data.get('ok') == 0 and json_data.get('msg') == '这里还没有内容')
                        
                    except ValueError as e:
                        logging.error(f"{location} Page {page}: Invalid JSON response - {e}")
                        if attempt < retry_count - 1:
                            time.sleep(delay * (attempt + 1))
                            continue
                        else:
                            self.stats['failed_requests'] += 1
                            return [], False
                    
                    # Add location metadata
                    for post in weibo_posts:
                        post['location'] = location
                    
                    self.stats['successful_requests'] += 1
                    self.stats['total_posts'] += len(weibo_posts)
                    
                    logging.info(f"{location} Page {page}: Successfully collected {len(weibo_posts)} posts")
                    return weibo_posts, is_end_of_data
                    
                else:
                    logging.warning(f"{location} Page {page}: HTTP {response.status_code}")
                    if attempt < retry_count - 1:
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        self.stats['failed_requests'] += 1
                        return [], False
                        
            except Exception as e:
                logging.error(f"{location} Page {page}: Error on attempt {attempt + 1} - {e}")
                if attempt < retry_count - 1:
                    time.sleep(delay * (attempt + 1))
                    continue
                else:
                    self.stats['failed_requests'] += 1
                    return [], False
        
        return [], False
    
    def collect_weibo_data_from_csv(self, csv_file_path: str, 
                                   output_file: str = "weibo_data_collected.csv",
                                   delay_between_requests: float = 1.0,
                                   auto_extend_pages: bool = True,
                                   max_pages_to_test: int = 100) -> bool:
        """
        Collect Weibo data from API URLs in CSV file.
        
        Args:
            csv_file_path (str): Path to CSV file with API URLs
            output_file (str): Output CSV file name
            delay_between_requests (float): Delay between requests in seconds
            auto_extend_pages (bool): Automatically discover more pages beyond CSV
            max_pages_to_test (int): Maximum pages to test per location
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.cookies:
                logging.error("No cookies available. Cannot proceed.")
                return False
            
            # Read the CSV file
            df = pd.read_csv(csv_file_path)
            
            if 'API_URL' not in df.columns:
                logging.error("'API_URL' column not found in CSV file")
                return False
            
            all_weibo_data = []
            location_stats = {}
            
            # Group by location
            for location in df['Location'].unique():
                location_df = df[df['Location'] == location].sort_values('Page')
                location_posts = []
                
                logging.info(f"\nProcessing {location} (collecting all available pages)...")
                
                # Get base URL pattern for this location
                first_row = location_df.iloc[0]
                base_url = first_row['API_URL']
                coordinates = first_row.get('Coordinates', '')
                
                # Extract the base URL without page parameter
                if '&page=' in base_url:
                    base_url_without_page = base_url.split('&page=')[0]
                else:
                    base_url_without_page = base_url
                
                # Get current max page from CSV
                current_max_page = location_df['Page'].max()
                logging.info(f"Starting from page 1, will test up to page {max_pages_to_test}")
                
                # Collect from all available pages (starting from 1)
                for page in range(1, max_pages_to_test + 1):
                    # Use existing URL if available in CSV, otherwise generate new one
                    if page <= current_max_page:
                        # Use existing URL from CSV
                        existing_row = location_df[location_df['Page'] == page]
                        if not existing_row.empty:
                            api_url = existing_row.iloc[0]['API_URL']
                        else:
                            api_url = f"{base_url_without_page}&page={page}"
                    else:
                        # Generate new URL for extended pages
                        api_url = f"{base_url_without_page}&page={page}"
                    
                    # Fetch data from API
                    weibo_posts, is_end_of_data = self.fetch_weibo_data_from_api(
                        api_url, location, page, coordinates, delay=delay_between_requests
                    )
                    
                    # Check if this page has content
                    if weibo_posts:
                        location_posts.extend(weibo_posts)
                        logging.info(f"{location} Page {page}: {len(weibo_posts)} posts collected")
                    else:
                        logging.info(f"{location} Page {page}: No posts found")
                    
                    # Check if we've reached the end of data
                    if is_end_of_data:
                        logging.info(f"{location}: Reached end of data at page {page}")
                        break
                    
                    # Add delay between requests
                    if delay_between_requests > 0:
                        time.sleep(delay_between_requests)
                
                all_weibo_data.extend(location_posts)
                location_stats[location] = len(location_posts)
                
                logging.info(f"{location}: {len(location_posts)} posts collected")
            
            # Save results
            if all_weibo_data:
                output_path = os.path.join(self.output_dir, output_file)
                df_results = pd.DataFrame(all_weibo_data)
                df_results.to_csv(output_path, index=False, encoding='utf-8')
                
                # Save statistics
                self._save_statistics(location_stats, output_path)
                
                logging.info(f"\nResults saved to {output_path}")
                self._print_summary(location_stats, all_weibo_data)
                
                return True
            else:
                logging.warning("No Weibo data collected.")
                return False
                
        except Exception as e:
            logging.error(f"Error processing file: {e}")
            return False
    
    def _save_statistics(self, location_stats: Dict, output_path: str):
        """Save collection statistics to a separate file."""
        stats_file = output_path.replace('.csv', '_stats.txt')
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write("=== Weibo Data Collection Statistics ===\n")
            f.write(f"Collection Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Requests: {self.stats['total_requests']}\n")
            f.write(f"Successful Requests: {self.stats['successful_requests']}\n")
            f.write(f"Failed Requests: {self.stats['failed_requests']}\n")
            f.write(f"Total Posts Collected: {self.stats['total_posts']}\n")
            f.write(f"Collection Duration: {datetime.now() - self.stats['start_time']}\n\n")
            
            f.write("Location Statistics:\n")
            for location, count in location_stats.items():
                f.write(f"  {location}: {count} posts\n")
        
        logging.info(f"Statistics saved to {stats_file}")
    
    def _print_summary(self, location_stats: Dict, all_weibo_data: List[Dict]):
        """Print collection summary."""
        print("\n" + "="*50)
        print("COLLECTION SUMMARY")
        print("="*50)
        
        for location, count in location_stats.items():
            print(f"  {location}: {count} posts")
        
        print(f"\nTotal posts collected: {len(all_weibo_data)}")
        print(f"Collection time: {datetime.now() - self.stats['start_time']}")
        print(f"Success rate: {self.stats['successful_requests']}/{self.stats['total_requests']} requests")
        
        if all_weibo_data:
            print(f"\nSample post from {all_weibo_data[0]['location']}:")
            sample = all_weibo_data[0]
            print(f"  User: {sample['screen_name']} (ID: {sample['user_id']})")
            print(f"  Text: {sample['text'][:100]}...")
            print(f"  Created: {sample['created_at']}")
            print(f"  Likes: {sample['attitudes_count']}, Comments: {sample['comments_count']}, Reposts: {sample['reposts_count']}")
            print(f"  Images: {sample['pic_num']} ({'Yes' if sample['pic_urls'] else 'No'} URLs)")
            print(f"  Verified: {sample['verified']}, Followers: {sample['followers_count']}")
    
    def analyze_collected_data(self, csv_file_path: str):
        """
        Analyze the collected Weibo data and provide insights.
        
        Args:
            csv_file_path (str): Path to CSV file with collected data
        """
        try:
            df = pd.read_csv(csv_file_path)
            
            print("\n" + "="*50)
            print("DATA ANALYSIS")
            print("="*50)
            
            print(f"Total posts collected: {len(df)}")
            print(f"Locations: {df['location'].nunique()}")
            print(f"Unique users: {df['screen_name'].nunique()}")
            
            # Top users by followers
            print(f"\nTop 5 users by followers:")
            df['followers_count_numeric'] = pd.to_numeric(df['followers_count'], errors='coerce')
            top_users = df.nlargest(5, 'followers_count_numeric')[['screen_name', 'followers_count', 'location']]
            for _, user in top_users.iterrows():
                print(f"  {user['screen_name']}: {user['followers_count']} followers ({user['location']})")
            
            # Engagement analysis
            print(f"\nEngagement Statistics:")
            print(f"  Average likes: {df['attitudes_count'].mean():.1f}")
            print(f"  Average comments: {df['comments_count'].mean():.1f}")
            print(f"  Average reposts: {df['reposts_count'].mean():.1f}")
            
            # Posts with images
            posts_with_images = df[df['pic_num'] > 0]
            print(f"  Posts with images: {len(posts_with_images)} ({len(posts_with_images)/len(df)*100:.1f}%)")
            
            # Verified users
            verified_users = df[df['verified'] == True]
            print(f"  Posts from verified users: {len(verified_users)} ({len(verified_users)/len(df)*100:.1f}%)")
            
            # Retweeted posts
            retweeted_posts = df[df['retweeted_status'] == True]
            print(f"  Retweeted posts: {len(retweeted_posts)} ({len(retweeted_posts)/len(df)*100:.1f}%)")
            
            # Long text posts
            long_text_posts = df[df['is_long_text'] == True]
            print(f"  Long text posts: {len(long_text_posts)} ({len(long_text_posts)/len(df)*100:.1f}%)")
            
            # Location distribution
            print(f"\nLocation Distribution:")
            location_counts = df['location'].value_counts()
            for location, count in location_counts.items():
                print(f"  {location}: {count} posts")
            
            # Gender distribution
            print(f"\nGender Distribution:")
            gender_counts = df['gender'].value_counts()
            for gender, count in gender_counts.items():
                gender_name = {'m': 'Male', 'f': 'Female', '': 'Unknown'}.get(gender, gender)
                print(f"  {gender_name}: {count} posts")
            
        except Exception as e:
            logging.error(f"Error analyzing data: {e}")

def main():
    """Main function to run the Weibo data collection."""
    # Configuration
    config = {
        'input_csv': "weibo_api_urls_iframe_only.csv",
        'cookie_file': "cookies.txt",
        'output_file': "weibo_data_collected.csv",
        'delay_between_requests': 1.0,
        'output_dir': "data"
    }
    
    print("Starting Weibo Data Collection...")
    print(f"Output directory: {config['output_dir']}")
    print(f"Input file: {config['input_csv']}")
    print(f"Cookie file: {config['cookie_file']}")
    print(f"Collection strategy: Auto-extend pages up to 100 per location")
    print(f"Delay between requests: {config['delay_between_requests']}s")
    print()
    
    # Initialize collector
    collector = WeiboDataCollector(
        cookie_file_path=config['cookie_file'],
        output_dir=config['output_dir']
    )
    
    # Collect data
    success = collector.collect_weibo_data_from_csv(
        csv_file_path=config['input_csv'],
        output_file=config['output_file'],
        delay_between_requests=config['delay_between_requests'],
        auto_extend_pages=True,
        max_pages_to_test=100  # Test up to 100 pages per location
    )
    
    if success:
        # Analyze the collected data
        output_path = os.path.join(config['output_dir'], config['output_file'])
        collector.analyze_collected_data(output_path)
        
        print(f"\nCollection completed successfully!")
        print(f"Data saved to: {output_path}")
    else:
        print(f"\nCollection failed. Check logs for details.")

if __name__ == "__main__":
    main() 