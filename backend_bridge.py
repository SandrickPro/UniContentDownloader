#!/usr/bin/env python3
"""
UniContentDownloader - Backend Bridge
Provides a web API bridge to integrate browser extension with fansly-downloader-ng
"""

import json
import os
import sys
import threading
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import subprocess
import tempfile
import hashlib

class DownloadRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.download_manager = kwargs.pop('download_manager', None)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/status':
            self.send_json_response({'status': 'running', 'version': '1.0.0'})
        elif parsed_path.path == '/api/downloads':
            downloads = self.download_manager.get_downloads() if self.download_manager else []
            self.send_json_response({'downloads': downloads})
        else:
            self.send_error(404, 'Not Found')
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/download':
            self.handle_download_request()
        else:
            self.send_error(404, 'Not Found')
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def handle_download_request(self):
        """Handle download request from browser extension"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Validate request data
            if not self.validate_download_request(request_data):
                self.send_error(400, 'Invalid request data')
                return
            
            # Queue download
            download_id = self.download_manager.queue_download(request_data)
            
            self.send_json_response({
                'success': True,
                'download_id': download_id,
                'message': 'Download queued successfully'
            })
            
        except json.JSONDecodeError:
            self.send_error(400, 'Invalid JSON')
        except Exception as e:
            self.send_error(500, f'Internal server error: {str(e)}')
    
    def validate_download_request(self, data):
        """Validate download request data"""
        required_fields = ['url', 'items']
        return all(field in data for field in required_fields) and isinstance(data['items'], list)
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response with CORS headers"""
        response = json.dumps(data).encode('utf-8')
        
        self.send_response(status_code)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)
    
    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"[{time.strftime('%H:%M:%S')}] {format % args}")


class DownloadManager:
    def __init__(self, fansly_downloader_path):
        self.fansly_downloader_path = Path(fansly_downloader_path)
        self.download_queue = []
        self.active_downloads = {}
        self.completed_downloads = []
        self.worker_thread = None
        self.running = False
        
    def start(self):
        """Start the download manager"""
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        print("Download manager started")
    
    def stop(self):
        """Stop the download manager"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join()
        print("Download manager stopped")
    
    def queue_download(self, request_data):
        """Queue a download request"""
        download_id = self._generate_download_id(request_data)
        
        download_item = {
            'id': download_id,
            'request_data': request_data,
            'status': 'queued',
            'created_at': time.time(),
            'progress': 0,
            'message': 'Queued for download'
        }
        
        self.download_queue.append(download_item)
        print(f"Queued download {download_id} with {len(request_data['items'])} items")
        
        return download_id
    
    def get_downloads(self):
        """Get all downloads (queued, active, completed)"""
        all_downloads = []
        all_downloads.extend(self.download_queue)
        all_downloads.extend(self.active_downloads.values())
        all_downloads.extend(self.completed_downloads[-10:])  # Last 10 completed
        
        return sorted(all_downloads, key=lambda x: x['created_at'], reverse=True)
    
    def _worker_loop(self):
        """Main worker loop for processing downloads"""
        while self.running:
            if self.download_queue:
                download_item = self.download_queue.pop(0)
                self._process_download(download_item)
            else:
                time.sleep(1)
    
    def _process_download(self, download_item):
        """Process a single download"""
        download_id = download_item['id']
        request_data = download_item['request_data']
        
        try:
            print(f"Processing download {download_id}")
            
            # Move to active downloads
            download_item['status'] = 'downloading'
            download_item['message'] = 'Preparing download...'
            self.active_downloads[download_id] = download_item
            
            # Create temporary config file
            config_data = self._create_download_config(request_data)
            
            # Execute fansly-downloader-ng
            result = self._execute_fansly_downloader(config_data, download_item)
            
            # Move to completed downloads
            download_item['status'] = 'completed' if result['success'] else 'failed'
            download_item['message'] = result['message']
            download_item['progress'] = 100 if result['success'] else 0
            download_item['completed_at'] = time.time()
            
            del self.active_downloads[download_id]
            self.completed_downloads.append(download_item)
            
            print(f"Download {download_id} {'completed' if result['success'] else 'failed'}")
            
        except Exception as e:
            print(f"Error processing download {download_id}: {e}")
            download_item['status'] = 'failed'
            download_item['message'] = f'Error: {str(e)}'
            
            if download_id in self.active_downloads:
                del self.active_downloads[download_id]
            self.completed_downloads.append(download_item)
    
    def _create_download_config(self, request_data):
        """Create configuration for fansly-downloader-ng"""
        # Extract creator name from URL
        creator_name = self._extract_creator_from_url(request_data['url'])
        
        config = {
            'username': creator_name,
            'download_single_posts': True,
            'target_urls': [item['url'] for item in request_data['items']],
            'separate_messages': True,
            'separate_previews': False,
            'show_downloads': False,
            'non_interactive': True
        }
        
        return config
    
    def _extract_creator_from_url(self, url):
        """Extract creator name from Fansly URL"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            
            # Handle different URL patterns
            if len(path_parts) >= 1:
                return path_parts[0]
            
            return 'unknown_creator'
        except:
            return 'unknown_creator'
    
    def _execute_fansly_downloader(self, config_data, download_item):
        """Execute fansly-downloader-ng with the given configuration"""
        try:
            # Create temporary config file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
                self._write_config_file(f, config_data)
                temp_config_path = f.name
            
            try:
                # Prepare command
                cmd = [
                    sys.executable, 
                    str(self.fansly_downloader_path / 'fansly_downloader_ng.py'),
                    '-c', temp_config_path,
                    '-ni',  # non-interactive
                    '-npox'  # no pause on exit
                ]
                
                # Execute command
                download_item['message'] = 'Running fansly-downloader-ng...'
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout
                    cwd=str(self.fansly_downloader_path)
                )
                
                success = result.returncode == 0
                message = 'Download completed successfully' if success else f'Download failed: {result.stderr}'
                
                return {
                    'success': success,
                    'message': message,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
            finally:
                # Clean up temporary config file
                try:
                    os.unlink(temp_config_path)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Download timed out after 10 minutes',
                'stdout': '',
                'stderr': 'Timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Execution error: {str(e)}',
                'stdout': '',
                'stderr': str(e)
            }
    
    def _write_config_file(self, file_handle, config_data):
        """Write configuration to INI file"""
        file_handle.write("[TargetedCreator]\n")
        file_handle.write(f"username = {config_data['username']}\n\n")
        
        file_handle.write("[Authorization]\n")
        file_handle.write("authorization_token = \n")
        file_handle.write("user_agent = \n\n")
        
        file_handle.write("[Download]\n")
        file_handle.write("download_directory = ./Downloads\n")
        file_handle.write(f"separate_messages = {str(config_data['separate_messages']).lower()}\n")
        file_handle.write(f"separate_previews = {str(config_data['separate_previews']).lower()}\n")
        file_handle.write(f"show_downloads = {str(config_data['show_downloads']).lower()}\n")
        
        if config_data.get('target_urls'):
            file_handle.write("\n[TargetUrls]\n")
            for i, url in enumerate(config_data['target_urls']):
                file_handle.write(f"url_{i} = {url}\n")
    
    def _generate_download_id(self, request_data):
        """Generate unique download ID"""
        data_string = json.dumps(request_data, sort_keys=True)
        return hashlib.md5(data_string.encode()).hexdigest()[:8]


class UniContentDownloaderBackend:
    def __init__(self, port=8080, fansly_downloader_path=None):
        self.port = port
        self.fansly_downloader_path = fansly_downloader_path or Path.home() / "UniContentDownloader"
        self.download_manager = DownloadManager(self.fansly_downloader_path)
        self.server = None
        
    def start(self):
        """Start the backend server"""
        print(f"Starting UniContentDownloader Backend on port {self.port}")
        print(f"Fansly Downloader path: {self.fansly_downloader_path}")
        
        # Check if fansly-downloader-ng is available
        if not self._check_fansly_downloader():
            print("ERROR: fansly-downloader-ng not found!")
            print("Please run the install.py script first to set up fansly-downloader-ng")
            return False
        
        # Start download manager
        self.download_manager.start()
        
        # Create request handler class with download manager
        def request_handler_factory(*args, **kwargs):
            return DownloadRequestHandler(*args, download_manager=self.download_manager, **kwargs)
        
        # Start HTTP server
        try:
            self.server = HTTPServer(('localhost', self.port), request_handler_factory)
            print(f"Backend server running at http://localhost:{self.port}")
            print("Press Ctrl+C to stop")
            
            self.server.serve_forever()
            
        except KeyboardInterrupt:
            print("\nShutting down backend server...")
            self.stop()
            return True
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
    
    def stop(self):
        """Stop the backend server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        
        self.download_manager.stop()
        print("Backend server stopped")
    
    def _check_fansly_downloader(self):
        """Check if fansly-downloader-ng is properly installed"""
        fansly_script = self.fansly_downloader_path / 'fansly_downloader_ng.py'
        return fansly_script.exists()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='UniContentDownloader Backend Bridge')
    parser.add_argument('--port', '-p', type=int, default=8080, 
                       help='Port to run the backend server on (default: 8080)')
    parser.add_argument('--fansly-path', '-f', type=str,
                       help='Path to fansly-downloader-ng installation')
    
    args = parser.parse_args()
    
    backend = UniContentDownloaderBackend(
        port=args.port,
        fansly_downloader_path=args.fansly_path
    )
    
    success = backend.start()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()