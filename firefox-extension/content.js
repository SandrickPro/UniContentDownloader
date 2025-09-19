/**
 * UniContentDownloader - Content Script
 * Runs on Fansly pages to detect and extract downloadable content
 */

class FanslyContentDetector {
  constructor() {
    this.detectedContent = new Set();
    this.isScanning = false;
    this.config = {};
    this.init();
  }

  async init() {
    // Get extension configuration
    const response = await chrome.runtime.sendMessage({ type: 'GET_CONFIG' });
    if (response.success) {
      this.config = response.data;
    }

    // Add download UI elements
    this.addDownloadInterface();

    // Start content detection
    this.startContentDetection();

    // Listen for page changes (SPA navigation)
    this.observePageChanges();
  }

  addDownloadInterface() {
    // Create floating download button
    const downloadBtn = document.createElement('div');
    downloadBtn.id = 'unicd-download-btn';
    downloadBtn.innerHTML = `
      <div class="unicd-btn-icon">⬇</div>
      <div class="unicd-btn-text">Download</div>
      <div class="unicd-btn-count">0</div>
    `;
    downloadBtn.title = 'UniContentDownloader - Click to download detected content';
    downloadBtn.addEventListener('click', () => this.handleDownloadClick());
    
    document.body.appendChild(downloadBtn);

    // Create content overlay for detected items
    const overlay = document.createElement('div');
    overlay.id = 'unicd-content-overlay';
    overlay.style.display = 'none';
    document.body.appendChild(overlay);
  }

  startContentDetection() {
    // Initial scan
    this.scanForContent();

    // Periodic scans for dynamically loaded content
    setInterval(() => {
      if (!this.isScanning) {
        this.scanForContent();
      }
    }, 3000);

    // Scan on scroll (for infinite scroll)
    let scrollTimeout;
    window.addEventListener('scroll', () => {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        if (!this.isScanning) {
          this.scanForContent();
        }
      }, 1000);
    });
  }

  observePageChanges() {
    // Observe DOM changes for SPA navigation
    const observer = new MutationObserver((mutations) => {
      let shouldRescan = false;
      
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
          // Check if new content nodes were added
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
              if (this.isContentNode(node)) {
                shouldRescan = true;
              }
            }
          });
        }
      });

      if (shouldRescan && !this.isScanning) {
        setTimeout(() => this.scanForContent(), 500);
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  async scanForContent() {
    this.isScanning = true;
    
    try {
      const newContent = await this.detectDownloadableContent();
      
      if (newContent.length > 0) {
        // Add new content to detected set
        newContent.forEach(item => {
          this.detectedContent.add(JSON.stringify(item));
        });

        // Update UI
        this.updateDownloadButton();
        this.highlightDetectedContent();

        // Notify background script
        chrome.runtime.sendMessage({
          type: 'CONTENT_DETECTED',
          data: {
            count: this.detectedContent.size,
            items: Array.from(this.detectedContent).map(item => JSON.parse(item)),
            url: window.location.href
          }
        });
      }
    } catch (error) {
      console.error('Content scanning error:', error);
    }

    this.isScanning = false;
  }

  async detectDownloadableContent() {
    const content = [];

    // Detect images
    const images = this.detectImages();
    content.push(...images);

    // Detect videos
    const videos = this.detectVideos();
    content.push(...videos);

    // Detect audio
    const audio = this.detectAudio();
    content.push(...audio);

    return content;
  }

  detectImages() {
    const images = [];
    const imageSelectors = [
      'img[src*="fansly.com"]',
      'img[src*="cloudfront.net"]',
      '.post-image img',
      '.message-image img',
      '.gallery-image img',
      'img[data-src]'
    ];

    imageSelectors.forEach(selector => {
      document.querySelectorAll(selector).forEach(img => {
        const src = img.src || img.dataset.src;
        if (src && this.isValidMediaUrl(src, 'image')) {
          images.push({
            type: 'image',
            url: src,
            filename: this.extractFilename(src),
            element: this.getElementPath(img),
            metadata: this.extractImageMetadata(img)
          });
        }
      });
    });

    return images;
  }

  detectVideos() {
    const videos = [];
    const videoSelectors = [
      'video source',
      'video[src]',
      '.video-player source',
      '[data-video-url]'
    ];

    videoSelectors.forEach(selector => {
      document.querySelectorAll(selector).forEach(element => {
        let src = element.src || element.dataset.videoUrl;
        
        if (!src && element.tagName === 'SOURCE') {
          src = element.src;
        }

        if (src && this.isValidMediaUrl(src, 'video')) {
          videos.push({
            type: 'video',
            url: src,
            filename: this.extractFilename(src),
            element: this.getElementPath(element),
            metadata: this.extractVideoMetadata(element)
          });
        }
      });
    });

    return videos;
  }

  detectAudio() {
    const audio = [];
    const audioSelectors = [
      'audio source',
      'audio[src]',
      '.audio-player source',
      '[data-audio-url]'
    ];

    audioSelectors.forEach(selector => {
      document.querySelectorAll(selector).forEach(element => {
        let src = element.src || element.dataset.audioUrl;
        
        if (!src && element.tagName === 'SOURCE') {
          src = element.src;
        }

        if (src && this.isValidMediaUrl(src, 'audio')) {
          audio.push({
            type: 'audio',
            url: src,
            filename: this.extractFilename(src),
            element: this.getElementPath(element),
            metadata: this.extractAudioMetadata(element)
          });
        }
      });
    });

    return audio;
  }

  isValidMediaUrl(url, type) {
    if (!url || url.startsWith('data:') || url.startsWith('blob:')) {
      return false;
    }

    const extensions = {
      image: ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'],
      video: ['.mp4', '.webm', '.avi', '.mov', '.wmv', '.flv', '.m3u8'],
      audio: ['.mp3', '.wav', '.ogg', '.aac', '.flac', '.m4a']
    };

    if (type && extensions[type]) {
      const hasValidExtension = extensions[type].some(ext => 
        url.toLowerCase().includes(ext)
      );
      if (hasValidExtension) return true;
    }

    // Check for Fansly CDN URLs
    const fanslyDomains = [
      'fansly.com',
      'cloudfront.net',
      'amazonaws.com'
    ];

    return fanslyDomains.some(domain => url.includes(domain));
  }

  extractFilename(url) {
    try {
      const urlObj = new URL(url);
      const pathname = urlObj.pathname;
      const filename = pathname.split('/').pop();
      return filename || `download_${Date.now()}`;
    } catch {
      return `download_${Date.now()}`;
    }
  }

  extractImageMetadata(img) {
    return {
      alt: img.alt || '',
      width: img.naturalWidth || img.width,
      height: img.naturalHeight || img.height,
      loading: img.loading || '',
      post_id: this.findPostId(img)
    };
  }

  extractVideoMetadata(video) {
    const videoElement = video.tagName === 'VIDEO' ? video : video.closest('video');
    return {
      duration: videoElement?.duration || 0,
      width: videoElement?.videoWidth || 0,
      height: videoElement?.videoHeight || 0,
      post_id: this.findPostId(video)
    };
  }

  extractAudioMetadata(audio) {
    const audioElement = audio.tagName === 'AUDIO' ? audio : audio.closest('audio');
    return {
      duration: audioElement?.duration || 0,
      post_id: this.findPostId(audio)
    };
  }

  findPostId(element) {
    // Try to find post ID from element or its parents
    let current = element;
    while (current && current !== document.body) {
      if (current.dataset?.postId) {
        return current.dataset.postId;
      }
      
      // Look for ID in class names or data attributes
      const classes = current.className || '';
      const postMatch = classes.match(/post-(\d+)/);
      if (postMatch) {
        return postMatch[1];
      }
      
      current = current.parentElement;
    }
    
    return null;
  }

  getElementPath(element) {
    const path = [];
    let current = element;
    
    while (current && current !== document.body) {
      let selector = current.tagName.toLowerCase();
      
      if (current.id) {
        selector += `#${current.id}`;
      } else if (current.className) {
        const classes = current.className.split(' ').filter(c => c.trim());
        if (classes.length > 0) {
          selector += `.${classes.join('.')}`;
        }
      }
      
      path.unshift(selector);
      current = current.parentElement;
    }
    
    return path.join(' > ');
  }

  isContentNode(node) {
    const contentSelectors = [
      'img', 'video', 'audio', 'source',
      '.post', '.message', '.gallery',
      '[data-video-url]', '[data-audio-url]'
    ];

    return contentSelectors.some(selector => {
      try {
        return node.matches && node.matches(selector) || 
               node.querySelector && node.querySelector(selector);
      } catch {
        return false;
      }
    });
  }

  updateDownloadButton() {
    const btn = document.getElementById('unicd-download-btn');
    const countElement = btn?.querySelector('.unicd-btn-count');
    
    if (countElement) {
      countElement.textContent = this.detectedContent.size;
      btn.style.display = this.detectedContent.size > 0 ? 'block' : 'none';
    }
  }

  highlightDetectedContent() {
    // Remove previous highlights
    document.querySelectorAll('.unicd-highlight').forEach(el => {
      el.classList.remove('unicd-highlight');
    });

    // Add highlights to new content
    Array.from(this.detectedContent).forEach(itemStr => {
      try {
        const item = JSON.parse(itemStr);
        const elements = document.querySelectorAll(item.element);
        elements.forEach(el => el.classList.add('unicd-highlight'));
      } catch (error) {
        console.warn('Failed to highlight element:', error);
      }
    });
  }

  async handleDownloadClick() {
    if (this.detectedContent.size === 0) {
      return;
    }

    const items = Array.from(this.detectedContent).map(item => JSON.parse(item));
    
    try {
      const response = await chrome.runtime.sendMessage({
        type: 'DOWNLOAD_REQUEST',
        data: {
          url: window.location.href,
          items: items,
          metadata: {
            title: document.title,
            timestamp: new Date().toISOString(),
            page_type: this.detectPageType()
          }
        }
      });

      if (response.success) {
        this.showDownloadStatus('Download started!', 'success');
      } else {
        this.showDownloadStatus('Download failed: ' + response.error, 'error');
      }
    } catch (error) {
      this.showDownloadStatus('Download failed: ' + error.message, 'error');
    }
  }

  detectPageType() {
    const url = window.location.href;
    if (url.includes('/posts/')) return 'post';
    if (url.includes('/messages/')) return 'messages';
    if (url.includes('/collections/')) return 'collection';
    return 'timeline';
  }

  showDownloadStatus(message, type) {
    // Create or update status notification
    let statusEl = document.getElementById('unicd-status');
    
    if (!statusEl) {
      statusEl = document.createElement('div');
      statusEl.id = 'unicd-status';
      document.body.appendChild(statusEl);
    }
    
    statusEl.textContent = message;
    statusEl.className = `unicd-status ${type}`;
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
      if (statusEl.parentNode) {
        statusEl.parentNode.removeChild(statusEl);
      }
    }, 3000);
  }
}

// Initialize content detector when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new FanslyContentDetector();
  });
} else {
  new FanslyContentDetector();
}