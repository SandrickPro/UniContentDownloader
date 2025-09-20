"""
Utility functions for UniContentDownloader
"""

import re
import os
from urllib.parse import urlparse
from typing import Optional


def validate_url(url: str) -> bool:
    """
    Validate if the given string is a valid URL.
    
    Args:
        url (str): URL string to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def get_content_type(headers: dict) -> str:
    """
    Extract content type from HTTP headers.
    
    Args:
        headers (dict): HTTP response headers
        
    Returns:
        str: Content type string
    """
    # Try different case variations of content-type header
    content_type = (headers.get('content-type', '') or 
                   headers.get('Content-Type', '') or
                   headers.get('CONTENT-TYPE', '')).split(';')[0].strip()
    return content_type.lower()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove invalid characters.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename safe for filesystem
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')
    # Ensure filename is not empty or only underscores
    if not sanitized or sanitized.replace('_', '').strip() == '':
        sanitized = "download"
    return sanitized


def get_file_extension(content_type: str, url: str) -> str:
    """
    Determine file extension based on content type and URL.
    
    Args:
        content_type (str): MIME content type
        url (str): Source URL
        
    Returns:
        str: File extension including dot (e.g., '.html', '.jpg')
    """
    # Common content type to extension mapping
    content_type_map = {
        'text/html': '.html',
        'text/plain': '.txt',
        'application/json': '.json',
        'application/xml': '.xml',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/webp': '.webp',
        'application/pdf': '.pdf',
        'application/zip': '.zip',
        'video/mp4': '.mp4',
        'video/avi': '.avi',
        'video/webm': '.webm',
        'audio/mp3': '.mp3',
        'audio/wav': '.wav',
    }
    
    # First try to get extension from content type
    if content_type in content_type_map:
        return content_type_map[content_type]
    
    # Fall back to URL-based extension
    parsed_url = urlparse(url)
    path = parsed_url.path
    if '.' in path:
        return os.path.splitext(path)[1]
    
    # Default extension
    return '.html' if content_type.startswith('text/') else '.bin'


def format_bytes(bytes_count: int) -> str:
    """
    Format byte count as human-readable string.
    
    Args:
        bytes_count (int): Number of bytes
        
    Returns:
        str: Formatted string (e.g., "1.2 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} PB"