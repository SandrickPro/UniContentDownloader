"""
Main ContentDownloader class for UniContentDownloader
"""

import os
import requests
from typing import Optional, Dict, Any
from urllib.parse import urlparse, urljoin
from tqdm import tqdm

from .utils import validate_url, get_content_type, sanitize_filename, get_file_extension, format_bytes


class ContentDownloader:
    """
    Main content downloader class that handles downloading content from various sources.
    """
    
    def __init__(self, 
                 download_dir: str = "downloads",
                 timeout: int = 30,
                 chunk_size: int = 8192,
                 user_agent: str = None):
        """
        Initialize ContentDownloader.
        
        Args:
            download_dir (str): Directory to save downloaded files
            timeout (int): Request timeout in seconds
            chunk_size (int): Chunk size for downloading large files
            user_agent (str): Custom user agent string
        """
        self.download_dir = download_dir
        self.timeout = timeout
        self.chunk_size = chunk_size
        self.session = requests.Session()
        
        # Set default user agent if not provided
        if user_agent:
            self.session.headers.update({'User-Agent': user_agent})
        else:
            self.session.headers.update({
                'User-Agent': 'UniContentDownloader/1.0 (Universal Content Downloader)'
            })
        
        # Create download directory if it doesn't exist
        os.makedirs(self.download_dir, exist_ok=True)
    
    def download(self, 
                 url: str, 
                 filename: Optional[str] = None,
                 show_progress: bool = True) -> Dict[str, Any]:
        """
        Download content from the given URL.
        
        Args:
            url (str): URL to download from
            filename (str, optional): Custom filename for the downloaded file
            show_progress (bool): Whether to show download progress
            
        Returns:
            Dict[str, Any]: Download result information
        """
        # Validate URL
        if not validate_url(url):
            return {
                'success': False,
                'error': 'Invalid URL provided',
                'url': url
            }
        
        try:
            # Make initial request to get headers
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            
            # If HEAD request fails, try GET with stream=True
            if response.status_code >= 400:
                response = self.session.get(url, timeout=self.timeout, stream=True)
            
            response.raise_for_status()
            
            # Get content information
            content_type = get_content_type(response.headers)
            content_length = response.headers.get('content-length')
            
            # Determine filename
            if not filename:
                filename = self._get_filename_from_url_or_headers(url, response.headers)
            
            # Sanitize filename
            filename = sanitize_filename(filename)
            
            # Add extension if not present
            if '.' not in filename:
                extension = get_file_extension(content_type, url)
                filename += extension
            
            # Full path for the file
            filepath = os.path.join(self.download_dir, filename)
            
            # Ensure we don't overwrite existing files
            filepath = self._get_unique_filepath(filepath)
            
            # Download the file
            if response.request.method == 'HEAD':
                # Need to make actual GET request
                response = self.session.get(url, timeout=self.timeout, stream=True)
                response.raise_for_status()
            
            total_size = int(content_length) if content_length else None
            
            with open(filepath, 'wb') as file:
                if show_progress and total_size:
                    # Show progress bar
                    with tqdm(
                        total=total_size, 
                        unit='B', 
                        unit_scale=True,
                        desc=os.path.basename(filepath)
                    ) as pbar:
                        for chunk in response.iter_content(chunk_size=self.chunk_size):
                            if chunk:
                                file.write(chunk)
                                pbar.update(len(chunk))
                else:
                    # No progress bar
                    for chunk in response.iter_content(chunk_size=self.chunk_size):
                        if chunk:
                            file.write(chunk)
            
            # Get final file size
            file_size = os.path.getsize(filepath)
            
            return {
                'success': True,
                'url': url,
                'filepath': filepath,
                'filename': os.path.basename(filepath),
                'content_type': content_type,
                'file_size': file_size,
                'file_size_formatted': format_bytes(file_size)
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request failed: {str(e)}',
                'url': url
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'url': url
            }
    
    def download_multiple(self, urls: list, show_progress: bool = True) -> list:
        """
        Download multiple URLs.
        
        Args:
            urls (list): List of URLs to download
            show_progress (bool): Whether to show progress for each download
            
        Returns:
            list: List of download results
        """
        results = []
        for i, url in enumerate(urls, 1):
            print(f"Downloading {i}/{len(urls)}: {url}")
            result = self.download(url, show_progress=show_progress)
            results.append(result)
            
            if result['success']:
                print(f"✓ Downloaded: {result['filename']} ({result['file_size_formatted']})")
            else:
                print(f"✗ Failed: {result['error']}")
        
        return results
    
    def _get_filename_from_url_or_headers(self, url: str, headers: dict) -> str:
        """
        Extract filename from URL or Content-Disposition header.
        
        Args:
            url (str): Source URL
            headers (dict): Response headers
            
        Returns:
            str: Extracted filename
        """
        # Try to get filename from Content-Disposition header
        content_disposition = headers.get('content-disposition', '')
        if 'filename=' in content_disposition:
            try:
                filename = content_disposition.split('filename=')[1].strip('"\'')
                if filename:
                    return filename
            except:
                pass
        
        # Fall back to URL path
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        if path and path != '/':
            filename = os.path.basename(path)
            if filename:
                return filename
        
        # Last resort: use domain name
        domain = parsed_url.netloc.replace('www.', '')
        return f"{domain}_download"
    
    def _get_unique_filepath(self, filepath: str) -> str:
        """
        Get a unique filepath by adding numbers if file already exists.
        
        Args:
            filepath (str): Original filepath
            
        Returns:
            str: Unique filepath
        """
        if not os.path.exists(filepath):
            return filepath
        
        base, ext = os.path.splitext(filepath)
        counter = 1
        
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        
        return f"{base}_{counter}{ext}"
    
    def set_custom_headers(self, headers: dict):
        """
        Set custom headers for requests.
        
        Args:
            headers (dict): Dictionary of headers to set
        """
        self.session.headers.update(headers)
    
    def get_content_info(self, url: str) -> Dict[str, Any]:
        """
        Get information about content without downloading it.
        
        Args:
            url (str): URL to get information about
            
        Returns:
            Dict[str, Any]: Content information
        """
        if not validate_url(url):
            return {
                'success': False,
                'error': 'Invalid URL provided',
                'url': url
            }
        
        try:
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            content_type = get_content_type(response.headers)
            content_length = response.headers.get('content-length')
            
            return {
                'success': True,
                'url': url,
                'content_type': content_type,
                'content_length': int(content_length) if content_length else None,
                'content_length_formatted': format_bytes(int(content_length)) if content_length else 'Unknown',
                'headers': dict(response.headers)
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request failed: {str(e)}',
                'url': url
            }