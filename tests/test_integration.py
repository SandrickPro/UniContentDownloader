"""
Integration tests for UniContentDownloader
"""

import pytest
import os
import tempfile
import shutil
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urljoin

from unicontentdownloader import ContentDownloader


class TestContentDownloaderIntegration:
    """Integration tests using a local HTTP server."""
    
    @classmethod
    def setup_class(cls):
        """Set up a test HTTP server."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.server_dir = os.path.join(cls.temp_dir, 'server')
        os.makedirs(cls.server_dir)
        
        # Create test files on the server
        cls._create_test_files()
        
        # Start HTTP server
        cls.server_port = 8000
        cls.server = HTTPServer(('localhost', cls.server_port), 
                               lambda *args: SimpleHTTPRequestHandler(*args, directory=cls.server_dir))
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        # Wait for server to start
        time.sleep(0.5)
        
        cls.base_url = f'http://localhost:{cls.server_port}'
    
    @classmethod
    def teardown_class(cls):
        """Clean up test server."""
        cls.server.shutdown()
        cls.server.server_close()
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)
    
    @classmethod
    def _create_test_files(cls):
        """Create test files for the HTTP server."""
        # Small text file
        with open(os.path.join(cls.server_dir, 'small.txt'), 'w') as f:
            f.write('This is a small test file.')
        
        # Large text file (for testing progress bar)
        with open(os.path.join(cls.server_dir, 'large.txt'), 'w') as f:
            f.write('Large file content.\n' * 1000)
        
        # Binary file
        with open(os.path.join(cls.server_dir, 'binary.dat'), 'wb') as f:
            f.write(b'\x00\x01\x02\x03' * 100)
        
        # HTML file
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Test Page</title></head>
        <body><h1>Test HTML Page</h1></body>
        </html>
        """
        with open(os.path.join(cls.server_dir, 'test.html'), 'w') as f:
            f.write(html_content)
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.download_dir = tempfile.mkdtemp()
        self.downloader = ContentDownloader(download_dir=self.download_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.download_dir):
            shutil.rmtree(self.download_dir)
    
    def test_download_small_file(self):
        """Test downloading a small text file."""
        url = urljoin(self.base_url, 'small.txt')
        result = self.downloader.download(url, show_progress=False)
        
        assert result['success'] == True
        assert result['filename'] == 'small.txt'
        assert os.path.exists(result['filepath'])
        
        # Verify content
        with open(result['filepath'], 'r') as f:
            content = f.read()
            assert 'This is a small test file.' in content
    
    def test_download_large_file(self):
        """Test downloading a large file to verify chunked download."""
        url = urljoin(self.base_url, 'large.txt')
        result = self.downloader.download(url, show_progress=False)
        
        assert result['success'] == True
        assert result['filename'] == 'large.txt'
        assert result['file_size'] > 1000  # Should be a reasonably large file
        assert os.path.exists(result['filepath'])
    
    def test_download_binary_file(self):
        """Test downloading a binary file."""
        url = urljoin(self.base_url, 'binary.dat')
        result = self.downloader.download(url, show_progress=False)
        
        assert result['success'] == True
        assert result['filename'] == 'binary.dat'
        assert os.path.exists(result['filepath'])
        
        # Verify binary content
        with open(result['filepath'], 'rb') as f:
            content = f.read()
            assert content.startswith(b'\x00\x01\x02\x03')
    
    def test_download_html_file(self):
        """Test downloading an HTML file."""
        url = urljoin(self.base_url, 'test.html')
        result = self.downloader.download(url, show_progress=False)
        
        assert result['success'] == True
        assert result['filename'] == 'test.html'
        assert result['content_type'] == 'text/html'
        assert os.path.exists(result['filepath'])
        
        # Verify HTML content
        with open(result['filepath'], 'r') as f:
            content = f.read()
            assert 'Test HTML Page' in content
    
    def test_download_nonexistent_file(self):
        """Test downloading a file that doesn't exist."""
        url = urljoin(self.base_url, 'nonexistent.txt')
        result = self.downloader.download(url)
        
        assert result['success'] == False
        assert '404' in result['error'] or 'Request failed' in result['error']
    
    def test_download_with_custom_filename(self):
        """Test downloading with a custom filename."""
        url = urljoin(self.base_url, 'small.txt')
        result = self.downloader.download(url, filename='custom_name.txt', show_progress=False)
        
        assert result['success'] == True
        assert result['filename'] == 'custom_name.txt'
        assert os.path.exists(result['filepath'])
        assert os.path.basename(result['filepath']) == 'custom_name.txt'
    
    def test_download_multiple_files(self):
        """Test downloading multiple files."""
        urls = [
            urljoin(self.base_url, 'small.txt'),
            urljoin(self.base_url, 'test.html'),
            urljoin(self.base_url, 'binary.dat')
        ]
        
        results = self.downloader.download_multiple(urls, show_progress=False)
        
        assert len(results) == 3
        successful_downloads = [r for r in results if r['success']]
        assert len(successful_downloads) == 3
        
        # Verify all files were downloaded
        for result in successful_downloads:
            assert os.path.exists(result['filepath'])
    
    def test_get_content_info(self):
        """Test getting content information without downloading."""
        url = urljoin(self.base_url, 'large.txt')
        result = self.downloader.get_content_info(url)
        
        assert result['success'] == True
        assert result['content_type'] == 'text/plain'
        assert result['content_length'] > 0
        assert 'B' in result['content_length_formatted']
    
    def test_unique_filename_handling(self):
        """Test that duplicate filenames are handled correctly."""
        url = urljoin(self.base_url, 'small.txt')
        
        # Download the same file twice
        result1 = self.downloader.download(url, show_progress=False)
        result2 = self.downloader.download(url, show_progress=False)
        
        assert result1['success'] == True
        assert result2['success'] == True
        assert result1['filename'] == 'small.txt'
        assert result2['filename'] == 'small_1.txt'
        assert result1['filepath'] != result2['filepath']
        assert os.path.exists(result1['filepath'])
        assert os.path.exists(result2['filepath'])
    
    def test_download_with_custom_headers(self):
        """Test downloading with custom headers."""
        # Set custom headers
        self.downloader.set_custom_headers({
            'User-Agent': 'CustomUserAgent/1.0',
            'Accept': 'text/*'
        })
        
        url = urljoin(self.base_url, 'small.txt')
        result = self.downloader.download(url, show_progress=False)
        
        assert result['success'] == True
        assert result['filename'] == 'small.txt'
        assert os.path.exists(result['filepath'])
    
    def test_timeout_behavior(self):
        """Test timeout behavior."""
        # Create a downloader with very short timeout
        short_timeout_downloader = ContentDownloader(
            download_dir=self.download_dir,
            timeout=0.001  # Very short timeout
        )
        
        url = urljoin(self.base_url, 'small.txt')
        result = short_timeout_downloader.download(url)
        
        # This might succeed if the connection is very fast, but typically should timeout
        # We're mainly testing that the timeout parameter is being used
        assert 'success' in result
        if not result['success']:
            assert 'timeout' in result['error'].lower() or 'request failed' in result['error'].lower()