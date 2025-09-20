"""
Tests for CLI module
"""

import pytest
import tempfile
import shutil
import os
from unittest.mock import patch, MagicMock
from unicontentdownloader.cli import main, handle_info_command, handle_download_command
from unicontentdownloader import ContentDownloader


class TestCLI:
    """Test CLI functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('sys.argv', ['unicontentdownloader', '--version'])
    def test_version_argument(self):
        """Test --version argument."""
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
    
    @patch('sys.argv', ['unicontentdownloader', 'https://example.com/test.txt'])
    @patch('unicontentdownloader.cli.ContentDownloader')
    def test_basic_download(self, mock_downloader_class):
        """Test basic download command."""
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        mock_downloader.download.return_value = {
            'success': True,
            'filename': 'test.txt',
            'file_size_formatted': '1.0 KB',
            'filepath': '/path/to/test.txt'
        }
        
        result = main()
        
        assert result == 0
        mock_downloader.download.assert_called_once_with(
            'https://example.com/test.txt', None, True
        )
    
    @patch('sys.argv', ['unicontentdownloader', '-d', '/custom/dir', 'https://example.com/test.txt'])
    @patch('unicontentdownloader.cli.ContentDownloader')
    def test_custom_directory(self, mock_downloader_class):
        """Test download with custom directory."""
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        mock_downloader.download.return_value = {
            'success': True,
            'filename': 'test.txt',
            'file_size_formatted': '1.0 KB',
            'filepath': '/custom/dir/test.txt'
        }
        
        result = main()
        
        assert result == 0
        mock_downloader_class.assert_called_with(
            download_dir='/custom/dir',
            timeout=30,
            chunk_size=8192,
            user_agent=None
        )
    
    @patch('sys.argv', ['unicontentdownloader', '-o', 'custom.txt', 'https://example.com/test.txt'])
    @patch('unicontentdownloader.cli.ContentDownloader')
    def test_custom_output_filename(self, mock_downloader_class):
        """Test download with custom output filename."""
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        mock_downloader.download.return_value = {
            'success': True,
            'filename': 'custom.txt',
            'file_size_formatted': '1.0 KB',
            'filepath': '/path/to/custom.txt'
        }
        
        result = main()
        
        assert result == 0
        mock_downloader.download.assert_called_once_with(
            'https://example.com/test.txt', 'custom.txt', True
        )
    
    @patch('sys.argv', ['unicontentdownloader', '--info', 'https://example.com/test.txt'])
    @patch('unicontentdownloader.cli.ContentDownloader')
    def test_info_command(self, mock_downloader_class):
        """Test --info command."""
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        mock_downloader.get_content_info.return_value = {
            'success': True,
            'content_type': 'text/plain',
            'content_length_formatted': '1.0 KB'
        }
        
        result = main()
        
        assert result == 0
        mock_downloader.get_content_info.assert_called_once_with('https://example.com/test.txt')
    
    @patch('sys.argv', ['unicontentdownloader', '--no-progress', 'https://example.com/test.txt'])
    @patch('unicontentdownloader.cli.ContentDownloader')
    def test_no_progress_flag(self, mock_downloader_class):
        """Test --no-progress flag."""
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        mock_downloader.download.return_value = {
            'success': True,
            'filename': 'test.txt',
            'file_size_formatted': '1.0 KB',
            'filepath': '/path/to/test.txt'
        }
        
        result = main()
        
        assert result == 0
        mock_downloader.download.assert_called_once_with(
            'https://example.com/test.txt', None, False  # show_progress=False
        )
    
    @patch('sys.argv', ['unicontentdownloader', 
           'https://example.com/file1.txt', 
           'https://example.com/file2.txt'])
    @patch('unicontentdownloader.cli.ContentDownloader')
    def test_multiple_urls(self, mock_downloader_class):
        """Test downloading multiple URLs."""
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        mock_downloader.download_multiple.return_value = [
            {'success': True, 'filename': 'file1.txt'},
            {'success': True, 'filename': 'file2.txt'}
        ]
        
        result = main()
        
        assert result == 0
        mock_downloader.download_multiple.assert_called_once_with(
            ['https://example.com/file1.txt', 'https://example.com/file2.txt'], True
        )
    
    @patch('sys.argv', ['unicontentdownloader', '-o', 'output.txt', 
           'https://example.com/file1.txt', 'https://example.com/file2.txt'])
    def test_output_with_multiple_urls_error(self):
        """Test error when using -o with multiple URLs."""
        result = main()
        assert result == 1
    
    @patch('sys.argv', ['unicontentdownloader', '--user-agent', 'CustomAgent/1.0', 
           'https://example.com/test.txt'])
    @patch('unicontentdownloader.cli.ContentDownloader')
    def test_custom_user_agent(self, mock_downloader_class):
        """Test custom user agent."""
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        mock_downloader.download.return_value = {
            'success': True,
            'filename': 'test.txt',
            'file_size_formatted': '1.0 KB',
            'filepath': '/path/to/test.txt'
        }
        
        result = main()
        
        assert result == 0
        mock_downloader_class.assert_called_with(
            download_dir='downloads',
            timeout=30,
            chunk_size=8192,
            user_agent='CustomAgent/1.0'
        )
    
    def test_handle_info_command_success(self):
        """Test handle_info_command with successful result."""
        mock_downloader = MagicMock()
        mock_downloader.get_content_info.return_value = {
            'success': True,
            'content_type': 'text/plain',
            'content_length_formatted': '1.0 KB'
        }
        
        result = handle_info_command(mock_downloader, ['https://example.com/test.txt'])
        assert result == 0
    
    def test_handle_info_command_failure(self):
        """Test handle_info_command with failed result."""
        mock_downloader = MagicMock()
        mock_downloader.get_content_info.return_value = {
            'success': False,
            'error': 'Not found'
        }
        
        result = handle_info_command(mock_downloader, ['https://example.com/test.txt'])
        assert result == 1
    
    def test_handle_download_command_single_success(self):
        """Test handle_download_command with single successful download."""
        mock_downloader = MagicMock()
        mock_downloader.download.return_value = {
            'success': True,
            'filename': 'test.txt',
            'file_size_formatted': '1.0 KB',
            'filepath': '/path/to/test.txt'
        }
        
        result = handle_download_command(
            mock_downloader, 
            ['https://example.com/test.txt'],
            show_progress=False
        )
        assert result == 0
    
    def test_handle_download_command_single_failure(self):
        """Test handle_download_command with single failed download."""
        mock_downloader = MagicMock()
        mock_downloader.download.return_value = {
            'success': False,
            'error': 'Not found'
        }
        
        result = handle_download_command(
            mock_downloader,
            ['https://example.com/test.txt'],
            show_progress=False
        )
        assert result == 1
    
    def test_handle_download_command_multiple_partial_success(self):
        """Test handle_download_command with partial success."""
        mock_downloader = MagicMock()
        mock_downloader.download_multiple.return_value = [
            {'success': True, 'filename': 'file1.txt'},
            {'success': False, 'error': 'Not found'}
        ]
        
        result = handle_download_command(
            mock_downloader,
            ['https://example.com/file1.txt', 'https://example.com/file2.txt'],
            show_progress=False
        )
        assert result == 2  # Partial success
    
    @patch('sys.argv', ['unicontentdownloader', 'https://example.com/test.txt'])
    @patch('unicontentdownloader.cli.ContentDownloader')
    def test_keyboard_interrupt(self, mock_downloader_class):
        """Test handling of KeyboardInterrupt."""
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        mock_downloader.download.side_effect = KeyboardInterrupt()
        
        result = main()
        assert result == 130  # Standard exit code for Ctrl+C