# Changelog

All notable changes to the Location-based Weibo Data Collector project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Added
- Complete project reorganization with professional structure
- Modular package architecture with src/collectors and src/utils
- Comprehensive API documentation
- Setup.py for package distribution
- Professional .gitignore file
- Changelog and project documentation
- Clean, emoji-free codebase

### Changed
- Reorganized file structure for better maintainability
- Moved source code to src/ directory
- Separated data files into input/, intermediate/, and output/ directories
- Updated import paths for modular structure
- Removed all emojis from code and documentation
- Enhanced error handling and logging

### Fixed
- Smart end-of-data detection using Weibo API responses
- Improved coordinate collection accuracy
- Better URL generation with iframe src extraction
- Enhanced retry logic and rate limiting

### Removed
- Redundant and duplicate files
- Unnecessary test scripts
- Old documentation files
- Temporary and cache files

## [0.9.0] - 2024-01-XX

### Added
- Initial coordinate collection functionality
- URL generation from coordinates
- Weibo data collection with automatic page discovery
- Interactive workflow script
- Basic error handling and retry logic

### Changed
- Improved coordinate collection using Amap picker
- Enhanced URL generation with iframe extraction
- Better data collection with end-of-data detection

### Fixed
- Coordinate parsing and validation
- URL generation accuracy
- Data collection reliability

## [0.8.0] - 2024-01-XX

### Added
- Basic Weibo data collection functionality
- Coordinate collection from location names
- URL generation capabilities

### Changed
- Initial project structure
- Basic documentation

### Fixed
- Initial bugs and issues 