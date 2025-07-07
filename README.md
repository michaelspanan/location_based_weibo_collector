# Location-based Weibo Data Collector

A comprehensive Python toolkit for collecting Weibo posts from specific locations using coordinate-based search.

## Project Structure

```
weibo-data-collector/
├── src/                          # Source code
│   ├── collectors/               # Data collection modules
│   │   ├── coordinate_collector.py  # GPS coordinate collection
│   │   ├── url_generator.py     # Weibo API URL generation
│   │   └── weibo_collector.py   # Main data collection
│   └── utils/                    # Utility modules
│       └── workflow.py          # Interactive workflow
├── data/                         # Data files
│   ├── input/                    # Input files
│   │   ├── locations.csv        # Location names
│   │   └── cookies.txt          # Weibo authentication
│   ├── intermediate/             # Processing files
│   │   ├── locations_with_coordinates.csv
│   │   └── weibo_api_urls_iframe_only.csv
│   └── output/                   # Final output files
│       ├── weibo_data_collected.csv
│       └── weibo_data_collected_stats.txt
├── examples/                     # Example scripts
├── docs/                         # Documentation
├── logs/                         # Log directory (auto-created)
├── tests/                        # Test files
├── main.py                       # Main entry point
├── setup.py                      # Package configuration
└── requirements.txt              # Dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Choose Your Workflow

The project offers multiple entry points depending on your needs:

#### Option A: Flexible Interface (Recommended)
```bash
python flexible_collector.py
```
This automatically detects what files you have and offers appropriate options.

#### Option B: Traditional Workflow
```bash
python main.py
```
This runs the complete workflow from start to finish.

### 3. User Scenarios

The flexible interface handles different user scenarios:

#### New Users (Location Names Only)
1. Create `data/input/locations.csv` with your location names
2. Add `data/input/cookies.txt` with your Weibo cookies
3. Run `python flexible_collector.py`
4. Choose "Run complete workflow"

#### Users with Coordinates
1. Place your coordinates file in `data/intermediate/locations_with_coordinates.csv`
2. Or convert your existing coordinate file using the converter utility
3. Run `python flexible_collector.py`
4. Choose "Generate API URLs and collect data"

#### Users with API URLs
1. Place your API URLs file in `data/intermediate/weibo_api_urls_iframe_only.csv`
2. Run `python flexible_collector.py`
3. Choose "Collect data from existing API URLs"

#### Users with Collected Data
1. If you already have `data/output/weibo_data_collected.csv`
2. Run `python flexible_collector.py`
3. Choose "View collected data analysis" or "Collect more data"

### 4. File Conversion Utility

If you have coordinates in different formats, use the conversion utility:

```bash
# Convert from separate lat/lng columns to standard format
python src/utils/file_converter.py \
  --input your_coordinates.csv \
  --output data/intermediate/locations_with_coordinates.csv \
  --type coordinates
```

Supported input formats:
- `Location,Latitude,Longitude`
- `Location,lat,lng`
- `Location,Coordinates` (already in standard format)

### 5. Individual Steps (Advanced)

You can also run individual steps:

```bash
# Step 1: Collect coordinates
python -c "from src.collectors.coordinate_collector import AmapCoordinateCollector; AmapCoordinateCollector().collect_coordinates_from_csv('data/input/locations.csv', 'data/intermediate/locations_with_coordinates.csv')"

# Step 2: Generate API URLs
python -c "from src.collectors.url_generator import WeiboURLGenerator; WeiboURLGenerator().generate_urls_from_csv('data/intermediate/locations_with_coordinates.csv', 'data/intermediate/weibo_api_urls_iframe_only.csv')"

# Step 3: Collect data
python -c "from src.collectors.weibo_collector import WeiboDataCollector; WeiboDataCollector('data/input/cookies.txt', 'data/output').collect_weibo_data_from_csv('data/intermediate/weibo_api_urls_iframe_only.csv', 'weibo_data_collected.csv')"
```

## Features

- **Flexible workflow** - Works with different input formats and user scenarios
- **Smart file detection** - Automatically detects existing files and suggests appropriate workflows
- **File conversion utility** - Converts between different coordinate formats
- **Automated coordinate collection** using Amap picker
- **Batch processing** for multiple locations
- **Automatic page discovery** (up to 100 pages per location)
- **Smart end-of-data detection** using Weibo API responses
- **Comprehensive data collection** (all post metadata)
- **Error handling and retry logic**
- **Rate limiting and respectful requests**
- **Data analysis and statistics**
- **Clean text processing**
- **User and engagement data**

## Data Flow

```
data/input/locations.csv
    ↓ (coordinate_collector.py)
data/intermediate/locations_with_coordinates.csv
    ↓ (url_generator.py)
data/intermediate/weibo_api_urls_iframe_only.csv
    ↓ (weibo_collector.py)
data/output/weibo_data_collected.csv
```

## Configuration

### Environment Variables
- `WEIBO_COOKIE_FILE` - Path to cookies file (default: "data/input/cookies.txt")
- `WEIBO_OUTPUT_DIR` - Output directory (default: "data/output")
- `WEIBO_DELAY` - Delay between requests (default: 1.0)

### Key Parameters
- **Coordinate Collection**: 2.0s delay between requests
- **URL Generation**: Up to 10 pages per location
- **Data Collection**: 1.0s delay, up to 100 pages per location

## Output

The system generates several output files:

1. **data/intermediate/locations_with_coordinates.csv** - Location names with coordinates
2. **data/intermediate/weibo_api_urls_iframe_only.csv** - Generated API URLs
3. **data/output/weibo_data_collected.csv** - Collected Weibo posts
4. **data/output/weibo_data_collected_stats.txt** - Collection statistics

## Example Output

```
Starting Weibo Data Collection...
Output directory: data/output
Input file: data/intermediate/weibo_api_urls_iframe_only.csv
Cookie file: data/input/cookies.txt
Collection strategy: Auto-extend pages up to 100 per location
Delay between requests: 1.0s

Processing 北京师范大学 (collecting all available pages)...
北京师范大学 Page 1: 10 posts collected
北京师范大学 Page 2: 10 posts collected
...
北京师范大学: Reached end of data at page 74
北京师范大学: 724 posts collected

Processing 华南理工大学 (collecting all available pages)...
华南理工大学 Page 1: 10 posts collected
...
华南理工大学: 100 posts collected

COLLECTION SUMMARY
==================================================
  北京师范大学: 724 posts
  华南理工大学: 100 posts

Total posts collected: 824
Collection time: 0:02:18
Success rate: 85/85 requests
```

## Documentation

- **[API Documentation](docs/API.md)** - Detailed API reference
- **[Changelog](docs/CHANGELOG.md)** - Version history and changes
- **[Examples](examples/)** - Usage examples and tutorials
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project
- **[Security Policy](SECURITY.md)** - Security and vulnerability reporting

## Development

### Installation for Development

```bash
# Clone the repository
git clone <repository-url>
cd weibo-data-collector

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run tests
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## Important Notes

- **Rate Limiting**: The system respects Weibo's rate limits with configurable delays
- **Authentication**: Valid cookies are required for data collection
- **Data Accuracy**: Coordinates are collected using Amap's official picker
- **Error Handling**: Failed requests are retried with exponential backoff
- **End Detection**: Uses Weibo API's "no content" response for accurate stopping

## Troubleshooting

### Common Issues

- **"cookies.txt not found"**: Copy data/input/cookies_template.txt to data/input/cookies.txt and add your Weibo cookies
- **"ChromeDriver not available"**: Install ChromeDriver for coordinate collection
- **"No posts found"**: Check if the location has recent Weibo activity
- **"API response error"**: Verify cookies are valid and not expired

### Performance Tips

- Use headless mode for faster coordinate collection
- Adjust delays based on your network speed
- Monitor the logs for detailed progress information

## License

This project is for educational and research purposes. Please respect Weibo's terms of service and rate limits.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

1. How to set up your development environment
2. Code style and quality standards
3. Testing requirements
4. Pull request process
5. Issue reporting guidelines

## Support

For issues and questions, please check the documentation or create an issue in the repository. 