/**
 * UniContentDownloader - Content Script
 * Скрипт для интеграции с Fansly страницами
 */

class UniContentDownloader {
    constructor() {
        this.isActive = false;
        this.downloadButtons = new Map();
        this.init();
    }

    init() {
        this.createDownloadInterface();
        this.observePageChanges();
        this.setupMessageListener();
        console.log('UniContentDownloader: Инициализирован на', window.location.href);
    }

    createDownloadInterface() {
        // Создаем кнопку управления загрузчиком
        const controlPanel = document.createElement('div');
        controlPanel.id = 'uni-downloader-panel';
        controlPanel.innerHTML = `
            <div class="uni-panel-header">
                <img src="${chrome.runtime.getURL('icons/icon32.png')}" alt="UniContentDownloader">
                <span>UniContentDownloader</span>
                <button id="uni-toggle-btn" class="uni-toggle-btn">Активировать</button>
            </div>
            <div class="uni-panel-status">
                <span id="uni-status">Неактивен</span>
            </div>
        `;
        
        document.body.appendChild(controlPanel);
        
        // Обработчик кнопки активации
        document.getElementById('uni-toggle-btn').addEventListener('click', () => {
            this.toggleDownloader();
        });
    }

    toggleDownloader() {
        this.isActive = !this.isActive;
        const toggleBtn = document.getElementById('uni-toggle-btn');
        const status = document.getElementById('uni-status');
        
        if (this.isActive) {
            toggleBtn.textContent = 'Деактивировать';
            toggleBtn.classList.add('active');
            status.textContent = 'Активен - сканирование контента';
            this.scanForContent();
        } else {
            toggleBtn.textContent = 'Активировать';
            toggleBtn.classList.remove('active');
            status.textContent = 'Неактивен';
            this.removeDownloadButtons();
        }
    }

    scanForContent() {
        if (!this.isActive) return;

        // Сканируем посты
        this.scanPosts();
        
        // Сканируем медиа в сообщениях
        this.scanMessages();
        
        // Сканируем коллекции
        this.scanCollections();
    }

    scanPosts() {
        // Ищем посты на странице
        const posts = document.querySelectorAll('[data-testid="post"], .post, article[role="article"]');
        
        posts.forEach(post => {
            if (!this.downloadButtons.has(post)) {
                this.addDownloadButton(post, 'post');
            }
        });
    }

    scanMessages() {
        // Ищем сообщения с медиа
        const messages = document.querySelectorAll('[data-testid="message"], .message, .chat-message');
        
        messages.forEach(message => {
            const hasMedia = message.querySelector('img, video, audio');
            if (hasMedia && !this.downloadButtons.has(message)) {
                this.addDownloadButton(message, 'message');
            }
        });
    }

    scanCollections() {
        // Ищем коллекции медиа
        const collections = document.querySelectorAll('[data-testid="collection"], .collection, .media-gallery');
        
        collections.forEach(collection => {
            if (!this.downloadButtons.has(collection)) {
                this.addDownloadButton(collection, 'collection');
            }
        });
    }

    addDownloadButton(element, type) {
        const downloadBtn = document.createElement('button');
        downloadBtn.className = 'uni-download-btn';
        downloadBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7,10 12,15 17,10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            <span>Скачать</span>
        `;
        
        downloadBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.downloadContent(element, type);
        });

        // Позиционируем кнопку
        element.style.position = 'relative';
        downloadBtn.style.position = 'absolute';
        downloadBtn.style.top = '10px';
        downloadBtn.style.right = '10px';
        downloadBtn.style.zIndex = '1000';
        
        element.appendChild(downloadBtn);
        this.downloadButtons.set(element, downloadBtn);
    }

    downloadContent(element, type) {
        const contentData = this.extractContentData(element, type);
        
        if (contentData) {
            // Отправляем данные в background script
            chrome.runtime.sendMessage({
                action: 'downloadContent',
                data: contentData
            });
            
            this.showNotification(`Контент отправлен в очередь загрузки (${type})`);
        } else {
            this.showNotification('Не удалось извлечь данные контента', 'error');
        }
    }

    extractContentData(element, type) {
        const data = {
            type: type,
            url: window.location.href,
            timestamp: Date.now(),
            content: []
        };

        // Извлекаем медиа URL-ы
        const mediaElements = element.querySelectorAll('img, video, audio');
        
        mediaElements.forEach(media => {
            const item = {
                tag: media.tagName.toLowerCase(),
                src: media.src || media.currentSrc,
                alt: media.alt || '',
                title: media.title || ''
            };
            
            // Дополнительные атрибуты для видео
            if (media.tagName === 'VIDEO') {
                item.poster = media.poster;
                item.duration = media.duration;
            }
            
            if (item.src && item.src.startsWith('http')) {
                data.content.push(item);
            }
        });

        // Извлекаем метаданные поста
        if (type === 'post') {
            const userElement = element.querySelector('[data-testid="username"], .username, .author');
            const timeElement = element.querySelector('time, [data-testid="timestamp"]');
            const textElement = element.querySelector('[data-testid="post-text"], .post-text, .content');
            
            data.metadata = {
                username: userElement?.textContent?.trim() || '',
                timestamp: timeElement?.getAttribute('datetime') || timeElement?.textContent || '',
                text: textElement?.textContent?.trim() || '',
                postId: this.extractPostId(element)
            };
        }

        return data.content.length > 0 ? data : null;
    }

    extractPostId(element) {
        // Пытаемся извлечь ID поста из различных атрибутов
        const postId = element.getAttribute('data-post-id') 
                   || element.getAttribute('data-id')
                   || element.id;
        
        if (postId) return postId;
        
        // Пытаемся извлечь из URL ссылок
        const links = element.querySelectorAll('a[href*="/post/"]');
        if (links.length > 0) {
            const match = links[0].href.match(/\/post\/(\d+)/);
            if (match) return match[1];
        }
        
        return null;
    }

    removeDownloadButtons() {
        this.downloadButtons.forEach((button, element) => {
            if (button.parentNode) {
                button.parentNode.removeChild(button);
            }
        });
        this.downloadButtons.clear();
    }

    observePageChanges() {
        // Наблюдаем за изменениями в DOM для SPA
        const observer = new MutationObserver((mutations) => {
            if (this.isActive) {
                let shouldScan = false;
                
                mutations.forEach(mutation => {
                    if (mutation.type === 'childList') {
                        shouldScan = true;
                    }
                });
                
                if (shouldScan) {
                    setTimeout(() => this.scanForContent(), 500);
                }
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    setupMessageListener() {
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            switch (message.action) {
                case 'getPageInfo':
                    sendResponse({
                        url: window.location.href,
                        title: document.title,
                        isActive: this.isActive
                    });
                    break;
                
                case 'toggleDownloader':
                    this.toggleDownloader();
                    sendResponse({ success: true });
                    break;
            }
        });
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `uni-notification uni-notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Автоматически удаляем уведомление через 3 секунды
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
}

// Инициализируем расширение после загрузки страницы
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new UniContentDownloader();
    });
} else {
    new UniContentDownloader();
}