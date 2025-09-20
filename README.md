# UniContentDownloader

[![CI/CD Pipeline](https://github.com/SandrickPro/UniContentDownloader/actions/workflows/ci.yml/badge.svg)](https://github.com/SandrickPro/UniContentDownloader/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/SandrickPro/UniContentDownloader/branch/main/graph/badge.svg)](https://codecov.io/gh/SandrickPro/UniContentDownloader)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Universal Content Downloader - A Python library and CLI tool for downloading content from various sources including web pages, images, videos, and documents.

## Features

- **Universal downloading**: Support for various content types (text, images, videos, documents)
- **Progress tracking**: Real-time download progress with progress bars
- **Custom headers**: Support for custom user agents and headers
- **Multiple URLs**: Download multiple files in batch
- **Content info**: Get file information without downloading
- **Safe filenames**: Automatic filename sanitization and duplicate handling
- **CLI interface**: Easy-to-use command-line interface
- **Python API**: Full-featured Python library for integration

## Installation

### From source

```bash
git clone https://github.com/SandrickPro/UniContentDownloader.git
cd UniContentDownloader
pip install -e .
```

### For development

```bash
git clone https://github.com/SandrickPro/UniContentDownloader.git
cd UniContentDownloader
pip install -e .[dev]
```

## Quick Start

### Command Line Usage

```bash
# Download a single file
unicontentdownloader https://example.com/file.pdf

# Download to a specific directory
unicontentdownloader -d /path/to/downloads https://example.com/file.pdf

# Download with custom filename
unicontentdownloader -o custom_name.pdf https://example.com/file.pdf

# Download multiple files
unicontentdownloader https://example.com/file1.pdf https://example.com/file2.jpg

# Get file information without downloading
unicontentdownloader --info https://example.com/file.pdf

# Download without progress bar
unicontentdownloader --no-progress https://example.com/file.pdf
```

### Python API Usage

```python
from unicontentdownloader import ContentDownloader

# Create downloader instance
downloader = ContentDownloader(download_dir="downloads")

# Download a single file
result = downloader.download("https://example.com/file.pdf")
if result['success']:
    print(f"Downloaded: {result['filename']} ({result['file_size_formatted']})")
else:
    print(f"Error: {result['error']}")

# Download multiple files
urls = [
    "https://example.com/file1.pdf",
    "https://example.com/file2.jpg",
    "https://example.com/file3.txt"
]
results = downloader.download_multiple(urls)

# Get content information
info = downloader.get_content_info("https://example.com/file.pdf")
if info['success']:
    print(f"Content type: {info['content_type']}")
    print(f"Size: {info['content_length_formatted']}")
```

## Advanced Usage

### Custom Headers and User Agent

```python
from unicontentdownloader import ContentDownloader

downloader = ContentDownloader(
    download_dir="downloads",
    user_agent="MyBot/1.0"
)

# Set additional custom headers
downloader.set_custom_headers({
    "Authorization": "Bearer token",
    "Referer": "https://example.com"
})

result = downloader.download("https://example.com/protected-file.pdf")
```

### Configuration Options

```python
from unicontentdownloader import ContentDownloader

downloader = ContentDownloader(
    download_dir="custom/downloads",    # Download directory
    timeout=60,                         # Request timeout in seconds
    chunk_size=16384,                   # Chunk size for large files
    user_agent="CustomAgent/1.0"        # Custom user agent
)
```

## CLI Options

```
usage: unicontentdownloader [-h] [-d DIRECTORY] [-o OUTPUT] [-t TIMEOUT]
                           [--chunk-size CHUNK_SIZE] [--user-agent USER_AGENT]
                           [--no-progress] [--info] [--version]
                           urls [urls ...]

UniContentDownloader - Universal Content Downloader

positional arguments:
  urls                  URLs to download

optional arguments:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        Download directory (default: downloads)
  -o OUTPUT, --output OUTPUT
                        Output filename (only for single URL)
  -t TIMEOUT, --timeout TIMEOUT
                        Request timeout in seconds (default: 30)
  --chunk-size CHUNK_SIZE
                        Chunk size for downloads (default: 8192)
  --user-agent USER_AGENT
                        Custom user agent string
  --no-progress         Disable progress bar
  --info                Get content information without downloading
  --version             show program's version number and exit
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e .[dev]

# Run all tests
pytest

# Run with coverage
pytest --cov=unicontentdownloader

# Run only unit tests
pytest tests/test_utils.py tests/test_downloader.py tests/test_cli.py

# Run only integration tests
pytest tests/test_integration.py
```

### Code Quality

```bash
# Lint code
flake8 unicontentdownloader/

# Type checking
mypy unicontentdownloader/

# Security scan
bandit -r unicontentdownloader/
safety check
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `pytest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 1.0.0
- Initial release
- Universal content downloader with CLI and Python API
- Support for multiple content types
- Progress tracking and custom headers
- Comprehensive test suite
- CI/CD pipeline with GitHub Actions
