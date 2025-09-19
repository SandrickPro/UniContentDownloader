/**
 * UniContentDownloader - Popup Script
 * Handles the extension popup interface
 */

class UniContentDownloaderPopup {
  constructor() {
    this.config = {};
    this.downloadQueue = [];
    this.downloadHistory = [];
    this.init();
  }

  async init() {
    await this.loadConfig();
    await this.loadData();
    this.setupEventListeners();
    this.updateUI();
  }

  async loadConfig() {
    try {
      const response = await chrome.runtime.sendMessage({ type: 'GET_CONFIG' });
      if (response.success) {
        this.config = response.data;
        this.populateConfigUI();
      }
    } catch (error) {
      console.error('Failed to load config:', error);
    }
  }

  async loadData() {
    try {
      // Load download queue
      const queueResponse = await chrome.runtime.sendMessage({ type: 'GET_DOWNLOAD_QUEUE' });
      if (queueResponse.success) {
        this.downloadQueue = queueResponse.data;
      }

      // Load download history
      const historyData = await chrome.storage.local.get('unicd_download_history');
      this.downloadHistory = historyData.unicd_download_history || [];

    } catch (error) {
      console.error('Failed to load data:', error);
    }
  }

  setupEventListeners() {
    // Scan button
    document.getElementById('scan-btn').addEventListener('click', () => {
      this.triggerContentScan();
    });

    // Download button
    document.getElementById('download-btn').addEventListener('click', () => {
      this.triggerDownload();
    });

    // Clear history button
    document.getElementById('clear-history-btn').addEventListener('click', () => {
      this.clearHistory();
    });

    // Configuration checkboxes
    const configCheckboxes = [
      'auto-download',
      'separate-messages', 
      'separate-previews',
      'show-notifications'
    ];

    configCheckboxes.forEach(id => {
      document.getElementById(id).addEventListener('change', (e) => {
        this.updateConfigSetting(id.replace('-', '_'), e.target.checked);
      });
    });

    // Backend URL input
    document.getElementById('backend-url').addEventListener('change', (e) => {
      this.updateConfigSetting('backend_url', e.target.value);
    });

    // Help and settings links
    document.getElementById('help-link').addEventListener('click', (e) => {
      e.preventDefault();
      this.openHelpPage();
    });

    document.getElementById('settings-link').addEventListener('click', (e) => {
      e.preventDefault();
      this.openSettingsPage();
    });
  }

  populateConfigUI() {
    // Populate checkboxes
    const checkboxMappings = {
      'auto-download': 'autoDownload',
      'separate-messages': 'separateMessages',
      'separate-previews': 'separatePreviews',
      'show-notifications': 'showNotifications'
    };

    Object.entries(checkboxMappings).forEach(([id, configKey]) => {
      const checkbox = document.getElementById(id);
      if (checkbox) {
        checkbox.checked = this.config[configKey] || false;
      }
    });

    // Populate backend URL
    const backendUrlInput = document.getElementById('backend-url');
    if (backendUrlInput) {
      backendUrlInput.value = this.config.backend_url || 'http://localhost:8080';
    }
  }

  updateUI() {
    this.updateStatus();
    this.updateDownloadButton();
    this.populateDownloadHistory();
    this.populateDownloadQueue();
  }

  async updateStatus() {
    // Get current tab content info
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (tab && tab.url.includes('fansly.com')) {
        // Query content script for detected items count
        try {
          const response = await chrome.tabs.sendMessage(tab.id, { type: 'GET_DETECTED_COUNT' });
          if (response && response.count !== undefined) {
            document.getElementById('detected-count').textContent = response.count;
          }
        } catch (error) {
          // Content script might not be loaded yet
          document.getElementById('detected-count').textContent = '0';
        }
      } else {
        document.getElementById('detected-count').textContent = 'N/A';
      }
    } catch (error) {
      document.getElementById('detected-count').textContent = '0';
    }

    // Update queue count
    document.getElementById('queue-count').textContent = this.downloadQueue.length;

    // Update status
    const statusElement = document.getElementById('download-status');
    if (this.downloadQueue.length > 0) {
      const processing = this.downloadQueue.find(item => item.status === 'processing');
      if (processing) {
        statusElement.textContent = 'Downloading...';
        statusElement.style.color = '#2ed573';
      } else {
        statusElement.textContent = 'Queued';
        statusElement.style.color = '#ff9800';
      }
    } else {
      statusElement.textContent = 'Ready';
      statusElement.style.color = '#333';
    }
  }

  updateDownloadButton() {
    const downloadBtn = document.getElementById('download-btn');
    const detectedCount = parseInt(document.getElementById('detected-count').textContent) || 0;
    
    downloadBtn.disabled = detectedCount === 0;
    downloadBtn.innerHTML = `
      <span class="btn-icon">⬇</span>
      Download ${detectedCount > 0 ? `(${detectedCount})` : 'All'}
    `;
  }

  populateDownloadHistory() {
    const historyContainer = document.getElementById('download-history');
    
    if (this.downloadHistory.length === 0) {
      historyContainer.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">📂</div>
          <div>No downloads yet</div>
        </div>
      `;
      return;
    }

    historyContainer.innerHTML = this.downloadHistory
      .slice(0, 5) // Show only last 5 items
      .map(item => this.createHistoryItemHTML(item))
      .join('');
  }

  populateDownloadQueue() {
    const queueContainer = document.getElementById('download-queue');
    
    if (this.downloadQueue.length === 0) {
      queueContainer.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">📥</div>
          <div>Queue is empty</div>
        </div>
      `;
      return;
    }

    queueContainer.innerHTML = this.downloadQueue
      .map(item => this.createQueueItemHTML(item))
      .join('');
  }

  createHistoryItemHTML(item) {
    const date = new Date(item.timestamp).toLocaleDateString();
    const time = new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    return `
      <div class="history-item">
        <div class="item-icon">📁</div>
        <div class="item-info">
          <div class="item-title">${this.truncateText(item.metadata?.title || 'Unknown', 30)}</div>
          <div class="item-details">${item.itemCount} items • ${date} ${time}</div>
        </div>
        <div class="item-status success">✓</div>
      </div>
    `;
  }

  createQueueItemHTML(item) {
    const statusClass = item.status || 'pending';
    const statusText = {
      pending: '⏳',
      processing: '⚡',
      error: '❌',
      completed: '✅'
    }[statusClass] || '⏳';

    return `
      <div class="queue-item">
        <div class="item-icon">📄</div>
        <div class="item-info">
          <div class="item-title">${this.truncateText(item.title || 'Unknown', 30)}</div>
          <div class="item-details">${item.content?.items?.length || 0} items</div>
        </div>
        <div class="item-status ${statusClass}">${statusText}</div>
      </div>
    `;
  }

  async triggerContentScan() {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (!tab || !tab.url.includes('fansly.com')) {
        this.showError('Please navigate to a Fansly page first');
        return;
      }

      // Send message to content script to trigger scan
      await chrome.tabs.sendMessage(tab.id, { type: 'TRIGGER_SCAN' });
      
      // Update UI after a short delay
      setTimeout(() => {
        this.updateStatus();
        this.updateDownloadButton();
      }, 1000);

    } catch (error) {
      console.error('Failed to trigger scan:', error);
      this.showError('Failed to scan page. Make sure the page is fully loaded.');
    }
  }

  async triggerDownload() {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (!tab || !tab.url.includes('fansly.com')) {
        this.showError('Please navigate to a Fansly page first');
        return;
      }

      // Send message to content script to trigger download
      await chrome.tabs.sendMessage(tab.id, { type: 'TRIGGER_DOWNLOAD' });
      
      // Update UI
      setTimeout(() => {
        this.loadData().then(() => this.updateUI());
      }, 500);

    } catch (error) {
      console.error('Failed to trigger download:', error);
      this.showError('Failed to start download');
    }
  }

  async updateConfigSetting(key, value) {
    this.config[key] = value;
    
    try {
      await chrome.runtime.sendMessage({
        type: 'UPDATE_CONFIG',
        data: { [key]: value }
      });
    } catch (error) {
      console.error('Failed to update config:', error);
    }
  }

  async clearHistory() {
    try {
      await chrome.runtime.sendMessage({ type: 'CLEAR_DOWNLOAD_HISTORY' });
      this.downloadHistory = [];
      this.populateDownloadHistory();
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
  }

  openHelpPage() {
    chrome.tabs.create({
      url: 'https://github.com/prof79/fansly-downloader-ng/wiki'
    });
  }

  openSettingsPage() {
    chrome.tabs.create({
      url: chrome.runtime.getURL('options.html')
    });
  }

  showError(message) {
    // Create temporary error notification in popup
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
      position: fixed;
      top: 10px;
      left: 10px;
      right: 10px;
      background: #ff4757;
      color: white;
      padding: 10px;
      border-radius: 4px;
      font-size: 12px;
      z-index: 1000;
    `;
    errorDiv.textContent = message;
    
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
      if (errorDiv.parentNode) {
        errorDiv.parentNode.removeChild(errorDiv);
      }
    }, 3000);
  }

  truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
  }
}

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new UniContentDownloaderPopup();
});