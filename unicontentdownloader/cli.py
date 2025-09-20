#!/usr/bin/env python3
"""
Command-line interface for UniContentDownloader
"""

import argparse
import sys
import os
from typing import List

from . import ContentDownloader, __version__


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='UniContentDownloader - Universal Content Downloader',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  unicontentdownloader https://example.com/file.pdf
  unicontentdownloader -d /downloads https://example.com/image.jpg
  unicontentdownloader -o custom_name.html https://example.com/page.html
  unicontentdownloader --info https://example.com/file.zip
        """
    )
    
    parser.add_argument(
        'urls',
        nargs='+',
        help='URLs to download'
    )
    
    parser.add_argument(
        '-d', '--directory',
        default='downloads',
        help='Download directory (default: downloads)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output filename (only for single URL)'
    )
    
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=8192,
        help='Chunk size for downloads (default: 8192)'
    )
    
    parser.add_argument(
        '--user-agent',
        help='Custom user agent string'
    )
    
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Disable progress bar'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Get content information without downloading'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'UniContentDownloader {__version__}'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.output and len(args.urls) > 1:
        print("Error: --output can only be used with a single URL", file=sys.stderr)
        return 1
    
    # Create downloader
    downloader = ContentDownloader(
        download_dir=args.directory,
        timeout=args.timeout,
        chunk_size=args.chunk_size,
        user_agent=args.user_agent
    )
    
    try:
        if args.info:
            # Get content information
            return handle_info_command(downloader, args.urls)
        else:
            # Download content
            return handle_download_command(downloader, args.urls, args.output, not args.no_progress)
            
    except KeyboardInterrupt:
        print("\nDownload interrupted by user", file=sys.stderr)
        return 130  # Standard exit code for Ctrl+C
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def handle_info_command(downloader: ContentDownloader, urls: List[str]) -> int:
    """Handle --info command."""
    success_count = 0
    
    for url in urls:
        print(f"\nGetting info for: {url}")
        result = downloader.get_content_info(url)
        
        if result['success']:
            print(f"  Content Type: {result['content_type']}")
            print(f"  Content Length: {result['content_length_formatted']}")
            success_count += 1
        else:
            print(f"  Error: {result['error']}")
    
    if success_count == len(urls):
        return 0
    elif success_count > 0:
        return 2  # Partial success
    else:
        return 1  # All failed


def handle_download_command(downloader: ContentDownloader, 
                           urls: List[str], 
                           output_filename: str = None,
                           show_progress: bool = True) -> int:
    """Handle download command."""
    if len(urls) == 1:
        # Single URL download
        result = downloader.download(urls[0], output_filename, show_progress)
        
        if result['success']:
            print(f"✓ Successfully downloaded: {result['filename']}")
            print(f"  Size: {result['file_size_formatted']}")
            print(f"  Location: {result['filepath']}")
            return 0
        else:
            print(f"✗ Download failed: {result['error']}")
            return 1
    else:
        # Multiple URLs download
        results = downloader.download_multiple(urls, show_progress)
        
        success_count = sum(1 for r in results if r['success'])
        
        print(f"\nDownload Summary:")
        print(f"  Successful: {success_count}/{len(results)}")
        print(f"  Failed: {len(results) - success_count}/{len(results)}")
        
        if success_count == len(results):
            return 0  # All successful
        elif success_count > 0:
            return 2  # Partial success
        else:
            return 1  # All failed


if __name__ == '__main__':
    sys.exit(main())