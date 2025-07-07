# Location-based Weibo Data Collector API Documentation

## Overview

The Location-based Weibo Data Collector provides a comprehensive API for collecting Weibo posts from specific locations. The system consists of three main components:

1. **Coordinate Collection** - Convert location names to GPS coordinates
2. **URL Generation** - Create Weibo API URLs from coordinates
3. **Data Collection** - Collect Weibo posts from API URLs

## Core Classes

### CoordinateCollector

Collects GPS coordinates from location names using Amap coordinate picker.

```python
from src.collectors.coordinate_collector import CoordinateCollector

collector = CoordinateCollector(headless=False)
success = collector.collect_coordinates_from_csv(
    input_csv="data/input/locations.csv",
    output_csv="data/intermediate/locations_with_coordinates.csv",
    delay=2.0
)
```

**Methods:**
- `collect_coordinates_from_csv(input_csv, output_csv, delay=2.0)` - Process CSV file
- `collect_coordinate(location_name, delay=2.0)` - Collect single location coordinate

### WeiboURLGenerator

Generates Weibo API URLs from coordinates using iframe src extraction.

```python
from src.collectors.url_generator import WeiboURLGenerator

generator = WeiboURLGenerator()
success = generator.generate_urls_from_csv(
    input_csv="data/intermediate/locations_with_coordinates.csv",
    output_csv="data/intermediate/weibo_api_urls_iframe_only.csv",
    max_pages=10
)
```

**Methods:**
- `generate_urls_from_csv(input_csv, output_csv, max_pages=10)` - Process CSV file
- `generate_url_for_location(coordinates, page=1)` - Generate single URL

### WeiboDataCollector

Collects Weibo posts from API URLs with automatic page discovery.

```python
from src.collectors.weibo_collector import WeiboDataCollector

collector = WeiboDataCollector(
    cookie_file_path="data/input/cookies.txt",
    output_dir="data/output"
)

success = collector.collect_weibo_data_from_csv(
    csv_file_path="data/intermediate/weibo_api_urls_iframe_only.csv",
    output_file="weibo_data_collected.csv",
    delay_between_requests=1.0,
    auto_extend_pages=True,
    max_pages_to_test=100
)
```

**Methods:**
- `collect_weibo_data_from_csv(csv_file_path, output_file, delay_between_requests=1.0, auto_extend_pages=True, max_pages_to_test=100)` - Main collection method
- `analyze_collected_data(csv_file_path)` - Analyze collected data
- `fetch_weibo_data_from_api(api_url, location, page, coordinates='', retry_count=3, delay=1.0)` - Fetch single API response

## Workflow Integration

### Complete Workflow

```python
from src.utils.workflow import run_workflow

# Run complete interactive workflow
run_workflow()
```

### Individual Steps

```python
from src.collectors import CoordinateCollector, WeiboURLGenerator, WeiboDataCollector

# Step 1: Collect coordinates
coord_collector = CoordinateCollector(headless=False)
coord_collector.collect_coordinates_from_csv(
    input_csv="data/input/locations.csv",
    output_csv="data/intermediate/locations_with_coordinates.csv"
)

# Step 2: Generate URLs
url_generator = WeiboURLGenerator()
url_generator.generate_urls_from_csv(
    input_csv="data/intermediate/locations_with_coordinates.csv",
    output_csv="data/intermediate/weibo_api_urls_iframe_only.csv"
)

# Step 3: Collect data
data_collector = WeiboDataCollector(
    cookie_file_path="data/input/cookies.txt",
    output_dir="data/output"
)
data_collector.collect_weibo_data_from_csv(
    csv_file_path="data/intermediate/weibo_api_urls_iframe_only.csv",
    output_file="weibo_data_collected.csv"
)
```

## Data Structures

### Input CSV Format (locations.csv)
```csv
Location
北京大学
清华大学
复旦大学
```

### Intermediate CSV Format (locations_with_coordinates.csv)
```csv
Location,Coordinates
北京大学,116.31,39.99
清华大学,116.33,39.99
```

### Output CSV Format (weibo_data_collected.csv)
```csv
mid,created_at,text,text_length,source,favorited,reposts_count,comments_count,attitudes_count,pic_num,user_id,screen_name,follow_count,followers_count,statuses_count,verified,verified_type,gender,retweeted_status,is_long_text,pic_urls,coordinates,location
```

## Configuration

### Environment Variables
- `WEIBO_COOKIE_FILE` - Path to cookies file (default: "data/input/cookies.txt")
- `WEIBO_OUTPUT_DIR` - Output directory (default: "data/output")
- `WEIBO_DELAY` - Delay between requests (default: 1.0)

### Configuration Files
- `requirements.txt` - Python dependencies
- `setup.py` - Package configuration
- `.gitignore` - Git ignore rules

## Error Handling

The system includes comprehensive error handling:

- **Retry Logic**: Failed requests are retried with exponential backoff
- **Rate Limiting**: Configurable delays between requests
- **Validation**: Input validation for coordinates and URLs
- **Logging**: Detailed logging for debugging and monitoring

## Performance Considerations

- **Batch Processing**: Process multiple locations efficiently
- **Memory Management**: Stream processing for large datasets
- **Rate Limiting**: Respectful requests to avoid blocking
- **Parallel Processing**: Future enhancement for concurrent collection

## Security

- **Cookie Management**: Secure handling of authentication cookies
- **Input Validation**: Validate all user inputs
- **Error Messages**: Avoid exposing sensitive information in errors 