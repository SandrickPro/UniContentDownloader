# UniContentDownloader

**UniContentDownloader** is an automated solution for downloading content from Fansly.com. It combines the powerful [fansly-downloader-ng](https://github.com/prof79/fansly-downloader-ng) backend with a custom Firefox browser extension for seamless content detection and downloading directly from web pages.

## Features

- 🚀 **Automated Installation** - One-click setup of fansly-downloader-ng
- 🌐 **Firefox Extension** - Detect and download content directly from Fansly pages
- 📥 **Smart Content Detection** - Automatically finds images, videos, and audio
- 🔄 **Queue Management** - Background processing of download requests
- ⚙️ **Configurable Settings** - Customize download behavior and preferences
- 📊 **Download History** - Track completed downloads and manage queue
- 🎯 **Real-time Highlighting** - Visual indicators for detected downloadable content

## Installation

### 1. Automated Setup

Run the installation script to automatically download and configure fansly-downloader-ng:

```bash
python install.py
```

This will:
- Download the latest fansly-downloader-ng
- Install Python dependencies
- Create launcher scripts
- Set up basic configuration

### 2. Firefox Extension Installation

1. Open Firefox and navigate to `about:debugging`
2. Click "This Firefox" in the left sidebar
3. Click "Load Temporary Add-on"
4. Navigate to the `firefox-extension` folder and select `manifest.json`

### 3. Backend Bridge Setup

Start the backend bridge to connect the browser extension with fansly-downloader-ng:

```bash
python backend_bridge.py
```

The backend will run on `http://localhost:8080` by default.

## Usage

### Getting Started

1. **Configure Authentication**
   - Edit `config.ini` to add your Fansly authorization token and user agent
   - You can get these from your browser's developer tools

2. **Start the Backend**
   ```bash
   python backend_bridge.py
   ```

3. **Use the Browser Extension**
   - Navigate to any Fansly page
   - The extension will automatically detect downloadable content
   - Click the floating download button to start downloading

### Extension Features

- **Content Detection**: Automatically scans pages for images, videos, and audio
- **Visual Highlighting**: Detected content is highlighted with download indicators
- **Download Queue**: Manage multiple download requests
- **Settings Panel**: Configure auto-download, folder organization, notifications
- **Download History**: View recent downloads and their status

### Configuration Options

The extension can be configured through its popup interface:

- **Auto-download**: Automatically download detected content
- **Separate Messages**: Organize downloads into separate folders
- **Download Previews**: Include preview images in downloads
- **Show Notifications**: Display download status notifications
- **Backend URL**: Configure the backend server endpoint

## File Structure

```
UniContentDownloader/
├── install.py                 # Automated installation script
├── backend_bridge.py          # Backend API bridge
├── firefox-extension/         # Browser extension files
│   ├── manifest.json         # Extension manifest
│   ├── background.js         # Service worker
│   ├── content.js           # Content script for Fansly pages
│   ├── content.css          # Content script styles
│   ├── popup.html           # Extension popup interface
│   ├── popup.js             # Popup functionality
│   ├── popup.css            # Popup styles
│   └── icons/               # Extension icons
├── config.ini               # Fansly downloader configuration
└── README.md               # This file
```

## Technical Details

### Backend Bridge

The backend bridge (`backend_bridge.py`) provides a REST API that:
- Receives download requests from the browser extension
- Manages a download queue with background processing
- Executes fansly-downloader-ng with appropriate configurations
- Tracks download progress and history

**API Endpoints:**
- `GET /api/status` - Backend status and version
- `GET /api/downloads` - List all downloads (queued, active, completed)
- `POST /api/download` - Queue a new download request

### Browser Extension

The Firefox extension consists of:
- **Content Script**: Runs on Fansly pages to detect downloadable content
- **Background Service Worker**: Manages communication and download queue
- **Popup Interface**: Provides user controls and configuration
- **Style Injection**: Adds visual indicators to detected content

### Content Detection

The extension detects downloadable content by:
- Scanning for image, video, and audio elements
- Identifying Fansly CDN URLs and media patterns
- Extracting metadata like file types, dimensions, and post IDs
- Monitoring page changes for dynamically loaded content

## Requirements

- Python 3.11+
- Firefox Browser
- Internet connection for downloading fansly-downloader-ng
- Valid Fansly account and authorization credentials

## Platform Support

- ✅ Windows 10/11
- ✅ macOS (with Python 3.11+)
- ✅ Linux (with Python 3.11+ and tkinter)

## Troubleshooting

### Common Issues

1. **Extension not detecting content**
   - Ensure you're on a Fansly page with media content
   - Check that the page has fully loaded
   - Try refreshing the page

2. **Backend connection errors**
   - Verify the backend bridge is running (`python backend_bridge.py`)
   - Check the backend URL in extension settings
   - Ensure no firewall is blocking localhost connections

3. **Download failures**
   - Verify your Fansly authorization token is valid
   - Check that fansly-downloader-ng is properly installed
   - Review backend logs for error details

### Getting Help

If you encounter issues:
1. Check the browser console for error messages
2. Review backend logs for detailed error information
3. Ensure all dependencies are properly installed
4. Verify your Fansly credentials are correctly configured

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational purposes only. Users are responsible for complying with Fansly's terms of service and applicable laws. The developers are not responsible for any misuse of this software.
