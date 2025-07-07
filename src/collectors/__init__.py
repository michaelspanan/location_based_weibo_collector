"""
Data Collection Modules

This package contains the core data collection functionality:
- coordinate_collector: Collect GPS coordinates from location names
- url_generator: Generate Weibo API URLs from coordinates
- weibo_collector: Collect Weibo posts from API URLs
"""

from .coordinate_collector import AmapCoordinateCollector
from .url_generator import WeiboURLGenerator
from .weibo_collector import WeiboDataCollector

__all__ = ['AmapCoordinateCollector', 'WeiboURLGenerator', 'WeiboDataCollector'] 