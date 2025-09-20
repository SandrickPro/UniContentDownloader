"""
Unit tests for utils module
"""

import pytest
import os
from unicontentdownloader.utils import (
    validate_url, 
    get_content_type, 
    sanitize_filename, 
    get_file_extension,
    format_bytes
)


class TestValidateUrl:
    """Test URL validation function."""
    
    def test_valid_http_url(self):
        assert validate_url("http://example.com") == True
    
    def test_valid_https_url(self):
        assert validate_url("https://example.com") == True
    
    def test_valid_url_with_path(self):
        assert validate_url("https://example.com/path/to/file.html") == True
    
    def test_valid_url_with_query(self):
        assert validate_url("https://example.com/search?q=test") == True
    
    def test_invalid_url_no_scheme(self):
        assert validate_url("example.com") == False
    
    def test_invalid_url_no_domain(self):
        assert validate_url("https://") == False
    
    def test_invalid_url_empty(self):
        assert validate_url("") == False
    
    def test_invalid_url_malformed(self):
        assert validate_url("not a url") == False


class TestGetContentType:
    """Test content type extraction function."""
    
    def test_simple_content_type(self):
        headers = {'content-type': 'text/html'}
        assert get_content_type(headers) == 'text/html'
    
    def test_content_type_with_charset(self):
        headers = {'content-type': 'text/html; charset=utf-8'}
        assert get_content_type(headers) == 'text/html'
    
    def test_content_type_with_boundary(self):
        headers = {'content-type': 'multipart/form-data; boundary=something'}
        assert get_content_type(headers) == 'multipart/form-data'
    
    def test_missing_content_type(self):
        headers = {}
        assert get_content_type(headers) == ''
    
    def test_case_insensitive_header(self):
        headers = {'Content-Type': 'IMAGE/JPEG'}
        assert get_content_type(headers) == 'image/jpeg'


class TestSanitizeFilename:
    """Test filename sanitization function."""
    
    def test_normal_filename(self):
        assert sanitize_filename("document.pdf") == "document.pdf"
    
    def test_filename_with_spaces(self):
        assert sanitize_filename("my document.pdf") == "my document.pdf"
    
    def test_filename_with_invalid_chars(self):
        assert sanitize_filename("file<>:\"/\\|?*.txt") == "file_________.txt"
    
    def test_filename_with_leading_trailing_spaces(self):
        assert sanitize_filename("  filename.txt  ") == "filename.txt"
    
    def test_filename_with_leading_trailing_dots(self):
        assert sanitize_filename("...filename.txt...") == "filename.txt"
    
    def test_empty_filename(self):
        assert sanitize_filename("") == "download"
    
    def test_filename_only_invalid_chars(self):
        assert sanitize_filename("<>:\"/\\|?*") == "download"


class TestGetFileExtension:
    """Test file extension detection function."""
    
    def test_html_content_type(self):
        assert get_file_extension('text/html', 'http://example.com') == '.html'
    
    def test_image_content_type(self):
        assert get_file_extension('image/jpeg', 'http://example.com') == '.jpg'
    
    def test_pdf_content_type(self):
        assert get_file_extension('application/pdf', 'http://example.com') == '.pdf'
    
    def test_unknown_content_type_with_url_extension(self):
        assert get_file_extension('application/unknown', 'http://example.com/file.doc') == '.doc'
    
    def test_unknown_content_type_text_fallback(self):
        assert get_file_extension('text/unknown', 'http://example.com') == '.html'
    
    def test_unknown_content_type_binary_fallback(self):
        assert get_file_extension('application/unknown', 'http://example.com') == '.bin'
    
    def test_no_extension_in_url(self):
        assert get_file_extension('image/png', 'http://example.com/path') == '.png'


class TestFormatBytes:
    """Test byte formatting function."""
    
    def test_bytes(self):
        assert format_bytes(512) == "512.0 B"
    
    def test_kilobytes(self):
        assert format_bytes(1024) == "1.0 KB"
    
    def test_megabytes(self):
        assert format_bytes(1024 * 1024) == "1.0 MB"
    
    def test_gigabytes(self):
        assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"
    
    def test_fractional_megabytes(self):
        result = format_bytes(1536 * 1024)  # 1.5 MB
        assert result == "1.5 MB"
    
    def test_zero_bytes(self):
        assert format_bytes(0) == "0.0 B"