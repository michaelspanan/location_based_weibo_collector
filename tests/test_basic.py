"""
Basic tests for Location-based Weibo Data Collector
"""

import pytest
import pandas as pd
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.file_converter import FileConverter


class TestFileConverter:
    """Test the FileConverter utility"""
    
    def test_convert_coordinates_to_standard_format(self, tmp_path):
        """Test coordinate format conversion"""
        # Create test data
        test_data = {
            'Location': ['Test Location'],
            'Latitude': [39.9995],
            'Longitude': [116.3074]
        }
        df = pd.DataFrame(test_data)
        
        input_file = tmp_path / "test_input.csv"
        output_file = tmp_path / "test_output.csv"
        
        df.to_csv(input_file, index=False)
        
        # Test conversion
        converter = FileConverter()
        success = converter.convert_coordinates_to_standard_format(
            str(input_file), str(output_file)
        )
        
        assert success is True
        assert output_file.exists()
        
        # Check output format
        result_df = pd.read_csv(output_file)
        assert 'Location' in result_df.columns
        assert 'Coordinates' in result_df.columns
        assert result_df.iloc[0]['Coordinates'] == '116.3074,39.9995'
    
    def test_validate_coordinates_file(self, tmp_path):
        """Test coordinate file validation"""
        # Create valid test data
        test_data = {
            'Location': ['Test Location'],
            'Coordinates': ['116.3074,39.9995']
        }
        df = pd.DataFrame(test_data)
        
        valid_file = tmp_path / "valid_coordinates.csv"
        df.to_csv(valid_file, index=False)
        
        converter = FileConverter()
        is_valid = converter.validate_coordinates_file(str(valid_file))
        
        assert is_valid is True
    
    def test_validate_invalid_coordinates_file(self, tmp_path):
        """Test invalid coordinate file validation"""
        # Create invalid test data
        test_data = {
            'Location': ['Test Location'],
            'Coordinates': ['invalid,coordinates']
        }
        df = pd.DataFrame(test_data)
        
        invalid_file = tmp_path / "invalid_coordinates.csv"
        df.to_csv(invalid_file, index=False)
        
        converter = FileConverter()
        is_valid = converter.validate_coordinates_file(str(invalid_file))
        
        assert is_valid is False


class TestProjectStructure:
    """Test project structure and imports"""
    
    def test_imports_work(self):
        """Test that all main modules can be imported"""
        try:
            from src.collectors.coordinate_collector import AmapCoordinateCollector
            from src.collectors.url_generator import WeiboURLGenerator
            from src.collectors.weibo_collector import WeiboDataCollector
            from src.utils.workflow import main
            from src.utils.file_converter import FileConverter
            assert True
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")
    
    def test_project_files_exist(self):
        """Test that essential project files exist"""
        essential_files = [
            "README.md",
            "requirements.txt",
            "setup.py",
            "pyproject.toml",
            "LICENSE",
            "CONTRIBUTING.md",
            "SECURITY.md",
            ".gitignore",
            "src/__init__.py",
            "src/collectors/__init__.py",
            "src/utils/__init__.py",
        ]
        
        for file_path in essential_files:
            assert os.path.exists(file_path), f"Missing file: {file_path}"


if __name__ == "__main__":
    pytest.main([__file__]) 