"""
Unit tests for ContentDownloader class
"""

import pytest
import os
import tempfile
import shutil
import responses
from unittest.mock import patch, mock_open
from unicontentdownloader.downloader import ContentDownloader


class TestContentDownloader:
    """Test ContentDownloader class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = ContentDownloader(download_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init_default_values(self):
        """Test ContentDownloader initialization with default values."""
        downloader = ContentDownloader()
        assert downloader.download_dir == "downloads"
        assert downloader.timeout == 30
        assert downloader.chunk_size == 8192
        assert "UniContentDownloader" in downloader.session.headers['User-Agent']
    
    def test_init_custom_values(self):
        """Test ContentDownloader initialization with custom values."""
        custom_temp_dir = tempfile.mkdtemp()
        try:
            downloader = ContentDownloader(
                download_dir=custom_temp_dir,
                timeout=60,
                chunk_size=4096,
                user_agent="Custom Agent"
            )
            assert downloader.download_dir == custom_temp_dir
            assert downloader.timeout == 60
            assert downloader.chunk_size == 4096
            assert downloader.session.headers['User-Agent'] == "Custom Agent"
        finally:
            if os.path.exists(custom_temp_dir):
                shutil.rmtree(custom_temp_dir)
    
    def test_download_invalid_url(self):
        """Test download with invalid URL."""
        result = self.downloader.download("not a url")
        assert result['success'] == False
        assert 'Invalid URL' in result['error']
    
    @responses.activate
    def test_download_successful(self):
        """Test successful download."""
        test_content = b"Hello, World!"
        # Mock both HEAD and GET requests
        responses.add(
            responses.HEAD,
            'https://example.com/test.txt',
            content_type='text/plain',
            headers={'content-length': str(len(test_content))}
        )
        responses.add(
            responses.GET,
            'https://example.com/test.txt',
            body=test_content,
            content_type='text/plain',
            headers={'content-length': str(len(test_content))}
        )
        
        result = self.downloader.download('https://example.com/test.txt', show_progress=False)
        
        assert result['success'] == True
        assert result['url'] == 'https://example.com/test.txt'
        assert 'text/plain' in result['content_type']  # May have multiple values due to responses library
        assert result['file_size'] == len(test_content)
        assert os.path.exists(result['filepath'])
        
        # Verify file content
        with open(result['filepath'], 'rb') as f:
            assert f.read() == test_content
    
    @responses.activate
    def test_download_custom_filename(self):
        """Test download with custom filename."""
        test_content = b"Test content"
        # Mock both HEAD and GET requests
        responses.add(
            responses.HEAD,
            'https://example.com/test.txt',
            content_type='text/plain'
        )
        responses.add(
            responses.GET,
            'https://example.com/test.txt',
            body=test_content,
            content_type='text/plain'
        )
        
        result = self.downloader.download(
            'https://example.com/test.txt', 
            filename='custom_name.txt',
            show_progress=False
        )
        
        assert result['success'] == True
        assert result['filename'] == 'custom_name.txt'
        assert os.path.basename(result['filepath']) == 'custom_name.txt'
    
    @responses.activate 
    def test_download_with_content_disposition(self):
        """Test download with Content-Disposition header."""
        test_content = b"Test content"
        # Mock both HEAD and GET requests
        responses.add(
            responses.HEAD,
            'https://example.com/download',
            content_type='application/octet-stream',
            headers={'content-disposition': 'attachment; filename="document.pdf"'}
        )
        responses.add(
            responses.GET,
            'https://example.com/download',
            body=test_content,
            content_type='application/octet-stream',
            headers={'content-disposition': 'attachment; filename="document.pdf"'}
        )
        
        result = self.downloader.download('https://example.com/download', show_progress=False)
        
        assert result['success'] == True
        assert result['filename'] == 'document.pdf'
    
    @responses.activate
    def test_download_request_error(self):
        """Test download with request error."""
        responses.add(
            responses.GET,
            'https://example.com/nonexistent',
            status=404
        )
        
        result = self.downloader.download('https://example.com/nonexistent')
        
        assert result['success'] == False
        assert 'Request failed' in result['error']
    
    @responses.activate
    def test_get_content_info_successful(self):
        """Test successful content info retrieval."""
        responses.add(
            responses.HEAD,
            'https://example.com/test.pdf',
            content_type='application/pdf',
            headers={'content-length': '1024'}
        )
        
        result = self.downloader.get_content_info('https://example.com/test.pdf')
        
        assert result['success'] == True
        # The content type might include the default text/plain, so check if our type is in it
        assert 'application/pdf' in result['content_type']
        assert result['content_length'] == 1024
        assert result['content_length_formatted'] == '1.0 KB'
    
    def test_get_content_info_invalid_url(self):
        """Test content info with invalid URL."""
        result = self.downloader.get_content_info("not a url")
        assert result['success'] == False
        assert 'Invalid URL' in result['error']
    
    def test_get_filename_from_url_or_headers(self):
        """Test filename extraction from URL and headers."""
        # Test Content-Disposition header
        headers = {'content-disposition': 'attachment; filename="test.pdf"'}
        filename = self.downloader._get_filename_from_url_or_headers(
            'https://example.com/download', headers
        )
        assert filename == 'test.pdf'
        
        # Test URL path
        filename = self.downloader._get_filename_from_url_or_headers(
            'https://example.com/path/document.txt', {}
        )
        assert filename == 'document.txt'
        
        # Test domain fallback
        filename = self.downloader._get_filename_from_url_or_headers(
            'https://example.com/', {}
        )
        assert filename == 'example.com_download'
    
    def test_get_unique_filepath(self):
        """Test unique filepath generation."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        
        # Test unique filepath generation
        unique_path = self.downloader._get_unique_filepath(test_file)
        expected_path = os.path.join(self.temp_dir, 'test_1.txt')
        assert unique_path == expected_path
        
        # Create the first unique file
        with open(unique_path, 'w') as f:
            f.write('test')
        
        # Test second unique filepath
        unique_path2 = self.downloader._get_unique_filepath(test_file)
        expected_path2 = os.path.join(self.temp_dir, 'test_2.txt')
        assert unique_path2 == expected_path2
    
    def test_set_custom_headers(self):
        """Test setting custom headers."""
        custom_headers = {'Authorization': 'Bearer token', 'Custom-Header': 'value'}
        self.downloader.set_custom_headers(custom_headers)
        
        for key, value in custom_headers.items():
            assert self.downloader.session.headers[key] == value
    
    @responses.activate
    def test_download_multiple(self):
        """Test downloading multiple URLs."""
        urls = [
            'https://example.com/file1.txt',
            'https://example.com/file2.txt',
            'https://invalid-url'
        ]
        
        # Mock successful downloads with both HEAD and GET
        responses.add(
            responses.HEAD,
            'https://example.com/file1.txt',
            content_type='text/plain'
        )
        responses.add(
            responses.GET,
            'https://example.com/file1.txt',
            body=b"Content 1",
            content_type='text/plain'
        )
        responses.add(
            responses.HEAD,
            'https://example.com/file2.txt',
            content_type='text/plain'
        )
        responses.add(
            responses.GET,
            'https://example.com/file2.txt',
            body=b"Content 2",
            content_type='text/plain'
        )
        
        results = self.downloader.download_multiple(urls, show_progress=False)
        
        assert len(results) == 3
        assert results[0]['success'] == True
        assert results[1]['success'] == True
        assert results[2]['success'] == False  # Invalid URL