"""
UniContentDownloader - Universal Content Downloader

A Python library for downloading content from various sources including
web pages, images, videos, and documents.
"""

__version__ = "1.0.0"
__author__ = "SandrickPro"

from .downloader import ContentDownloader
from .utils import validate_url, get_content_type, sanitize_filename

__all__ = ["ContentDownloader", "validate_url", "get_content_type", "sanitize_filename"]