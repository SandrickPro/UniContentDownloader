/**
 * UniContentDownloader - Background Service Worker
 * Handles communication between content scripts and the fansly-downloader-ng backend
 */

// Storage keys
const STORAGE_KEYS = {
  CONFIG: 'unicd_config',
  DOWNLOAD_QUEUE: 'unicd_download_queue',
  DOWNLOAD_HISTORY: 'unicd_download_history'
};

// Default configuration
const DEFAULT_CONFIG = {
  autoDownload: false,
  downloadPath: '',
  separateMessages: true,
  separatePreviews: false,
  showNotifications: true,
  backend_url: 'http://localhost:8080'
};

class UniContentDownloaderBackground {
  constructor() {
    this.downloadQueue = [];
    this.isProcessingQueue = false;
    this.setupEventListeners();
    this.initializeConfig();
  }

  setupEventListeners() {
    // Handle extension installation
    chrome.runtime.onInstalled.addListener((details) => {
      if (details.reason === 'install') {
        this.showWelcomeNotification();
      }
    });

    // Handle messages from content scripts
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // Keep the message channel open for async responses
    });

    // Handle download completion
    chrome.downloads.onChanged.addListener((downloadDelta) => {
      if (downloadDelta.state && downloadDelta.state.current === 'complete') {
        this.handleDownloadComplete(downloadDelta.id);
      }
    });
  }

  async initializeConfig() {
    try {
      const stored = await chrome.storage.local.get(STORAGE_KEYS.CONFIG);
      if (!stored[STORAGE_KEYS.CONFIG]) {
        await chrome.storage.local.set({
          [STORAGE_KEYS.CONFIG]: DEFAULT_CONFIG
        });
      }
    } catch (error) {
      console.error('Failed to initialize config:', error);
    }
  }

  async handleMessage(message, sender, sendResponse) {
    try {
      switch (message.type) {
        case 'CONTENT_DETECTED':
          await this.handleContentDetected(message.data, sender.tab);
          sendResponse({ success: true });
          break;

        case 'DOWNLOAD_REQUEST':
          await this.handleDownloadRequest(message.data);
          sendResponse({ success: true });
          break;

        case 'GET_CONFIG':
          const config = await this.getConfig();
          sendResponse({ success: true, data: config });
          break;

        case 'UPDATE_CONFIG':
          await this.updateConfig(message.data);
          sendResponse({ success: true });
          break;

        case 'GET_DOWNLOAD_QUEUE':
          sendResponse({ success: true, data: this.downloadQueue });
          break;

        case 'CLEAR_DOWNLOAD_HISTORY':
          await this.clearDownloadHistory();
          sendResponse({ success: true });
          break;

        default:
          sendResponse({ success: false, error: 'Unknown message type' });
      }
    } catch (error) {
      console.error('Error handling message:', error);
      sendResponse({ success: false, error: error.message });
    }
  }

  async handleContentDetected(contentData, tab) {
    const config = await this.getConfig();
    
    if (config.autoDownload) {
      await this.addToDownloadQueue(contentData, tab);
    }

    // Update badge with queue count
    await this.updateBadge();

    // Show notification if enabled
    if (config.showNotifications) {
      this.showContentDetectedNotification(contentData.count, tab.title);
    }
  }

  async handleDownloadRequest(downloadData) {
    try {
      // Send to fansly-downloader-ng backend
      const config = await this.getConfig();
      const response = await fetch(`${config.backend_url}/api/download`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(downloadData)
      });

      if (!response.ok) {
        throw new Error(`Backend request failed: ${response.status}`);
      }

      const result = await response.json();
      this.showDownloadStartedNotification(downloadData.items.length);
      
      // Store in download history
      await this.addToDownloadHistory(downloadData, result);
      
    } catch (error) {
      console.error('Download request failed:', error);
      this.showErrorNotification('Download failed', error.message);
    }
  }

  async addToDownloadQueue(contentData, tab) {
    this.downloadQueue.push({
      id: Date.now(),
      url: tab.url,
      title: tab.title,
      content: contentData,
      timestamp: new Date().toISOString(),
      status: 'pending'
    });

    await chrome.storage.local.set({
      [STORAGE_KEYS.DOWNLOAD_QUEUE]: this.downloadQueue
    });

    if (!this.isProcessingQueue) {
      this.processDownloadQueue();
    }
  }

  async processDownloadQueue() {
    if (this.isProcessingQueue || this.downloadQueue.length === 0) {
      return;
    }

    this.isProcessingQueue = true;

    try {
      const item = this.downloadQueue[0];
      item.status = 'processing';
      await this.updateBadge();

      await this.handleDownloadRequest({
        url: item.url,
        items: item.content.items,
        metadata: {
          title: item.title,
          timestamp: item.timestamp
        }
      });

      // Remove processed item
      this.downloadQueue.shift();
      await chrome.storage.local.set({
        [STORAGE_KEYS.DOWNLOAD_QUEUE]: this.downloadQueue
      });

    } catch (error) {
      console.error('Queue processing error:', error);
      if (this.downloadQueue.length > 0) {
        this.downloadQueue[0].status = 'error';
        this.downloadQueue[0].error = error.message;
      }
    }

    this.isProcessingQueue = false;
    await this.updateBadge();

    // Process next item if available
    if (this.downloadQueue.length > 0) {
      setTimeout(() => this.processDownloadQueue(), 2000);
    }
  }

  async updateBadge() {
    const queueCount = this.downloadQueue.length;
    const text = queueCount > 0 ? queueCount.toString() : '';
    const color = this.downloadQueue.some(item => item.status === 'error') ? '#ff4444' : '#4CAF50';

    await chrome.action.setBadgeText({ text });
    await chrome.action.setBadgeBackgroundColor({ color });
  }

  async getConfig() {
    const stored = await chrome.storage.local.get(STORAGE_KEYS.CONFIG);
    return { ...DEFAULT_CONFIG, ...stored[STORAGE_KEYS.CONFIG] };
  }

  async updateConfig(newConfig) {
    const currentConfig = await this.getConfig();
    const updatedConfig = { ...currentConfig, ...newConfig };
    await chrome.storage.local.set({
      [STORAGE_KEYS.CONFIG]: updatedConfig
    });
  }

  async addToDownloadHistory(downloadData, result) {
    const stored = await chrome.storage.local.get(STORAGE_KEYS.DOWNLOAD_HISTORY);
    const history = stored[STORAGE_KEYS.DOWNLOAD_HISTORY] || [];
    
    history.unshift({
      id: Date.now(),
      timestamp: new Date().toISOString(),
      url: downloadData.url,
      itemCount: downloadData.items.length,
      result: result,
      metadata: downloadData.metadata
    });

    // Keep only last 100 entries
    const trimmedHistory = history.slice(0, 100);
    
    await chrome.storage.local.set({
      [STORAGE_KEYS.DOWNLOAD_HISTORY]: trimmedHistory
    });
  }

  async clearDownloadHistory() {
    await chrome.storage.local.set({
      [STORAGE_KEYS.DOWNLOAD_HISTORY]: []
    });
  }

  showWelcomeNotification() {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'UniContentDownloader Installed',
      message: 'Extension is ready! Visit Fansly pages to start downloading content.'
    });
  }

  showContentDetectedNotification(count, pageTitle) {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'Content Detected',
      message: `Found ${count} downloadable items on ${pageTitle}`
    });
  }

  showDownloadStartedNotification(count) {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'Download Started',
      message: `Processing ${count} items...`
    });
  }

  showErrorNotification(title, message) {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: title,
      message: message
    });
  }

  handleDownloadComplete(downloadId) {
    // Optional: Handle individual file download completion
    console.log('Download completed:', downloadId);
  }
}

// Initialize the background service
new UniContentDownloaderBackground();