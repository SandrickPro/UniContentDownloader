#!/bin/bash
# Quick start script for UniContentDownloader

echo "🚀 UniContentDownloader Quick Start"
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [ "$(echo "$python_version >= 3.11" | bc)" -eq 0 ]; then
    echo "❌ Python 3.11+ is required. Current version: $python_version"
    exit 1
fi

echo "✓ Python $python_version detected"

# Run installation
echo ""
echo "📦 Starting automated installation..."
python3 install.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Install the Firefox extension from the 'firefox-extension' folder"
    echo "2. Edit config.ini to add your Fansly credentials"
    echo "3. Start the backend: python3 backend_bridge.py"
    echo "4. Visit Fansly pages to start downloading content"
    echo ""
    echo "📖 For detailed instructions, see README.md"
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi