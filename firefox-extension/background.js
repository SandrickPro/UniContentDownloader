/**
 * UniContentDownloader - Background Script
 * Фоновый скрипт для управления загрузками
 */

class DownloadManager {
    constructor() {
        this.downloadQueue = [];
        this.isProcessing = false;
        this.nativePort = null;
        this.init();
    }

    init() {
        this.setupMessageListeners();
        this.setupContextMenus();
        this.setupNativeMessaging();
        console.log('UniContentDownloader Background: Инициализирован');
    }

    setupMessageListeners() {
        // Слушаем сообщения от content scripts
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            switch (message.action) {
                case 'downloadContent':
                    this.addToQueue(message.data);
                    sendResponse({ success: true });
                    break;
                
                case 'getQueueStatus':
                    sendResponse({
                        queueLength: this.downloadQueue.length,
                        isProcessing: this.isProcessing
                    });
                    break;
                
                case 'clearQueue':
                    this.clearQueue();
                    sendResponse({ success: true });
                    break;
            }
        });
    }

    setupContextMenus() {
        // Создаем контекстные меню
        chrome.contextMenus.create({
            id: 'uni-download-page',
            title: 'Скачать всё содержимое страницы',
            contexts: ['page'],
            documentUrlPatterns: ['https://fansly.com/*']
        });

        chrome.contextMenus.create({
            id: 'uni-download-image',
            title: 'Скачать через UniContentDownloader',
            contexts: ['image'],
            documentUrlPatterns: ['https://fansly.com/*']
        });

        chrome.contextMenus.create({
            id: 'uni-download-video',
            title: 'Скачать через UniContentDownloader',
            contexts: ['video'],
            documentUrlPatterns: ['https://fansly.com/*']
        });

        // Обработчик кликов по контекстному меню
        chrome.contextMenus.onClicked.addListener((info, tab) => {
            switch (info.menuItemId) {
                case 'uni-download-page':
                    this.downloadPage(tab);
                    break;
                
                case 'uni-download-image':
                case 'uni-download-video':
                    this.downloadMedia(info, tab);
                    break;
            }
        });
    }

    setupNativeMessaging() {
        // Попытка подключения к нативному приложению
        try {
            this.connectNative();
        } catch (error) {
            console.log('Нативное приложение не подключено:', error);
        }
    }

    connectNative() {
        if (this.nativePort) {
            this.nativePort.disconnect();
        }

        this.nativePort = chrome.runtime.connectNative('com.unicontentdownloader.fansly');
        
        this.nativePort.onMessage.addListener((message) => {
            console.log('Сообщение от нативного приложения:', message);
            this.handleNativeMessage(message);
        });

        this.nativePort.onDisconnect.addListener(() => {
            console.log('Нативное приложение отключено');
            this.nativePort = null;
            
            // Повторное подключение через 5 секунд
            setTimeout(() => {
                this.connectNative();
            }, 5000);
        });
    }

    handleNativeMessage(message) {
        switch (message.type) {
            case 'download_complete':
                this.onDownloadComplete(message.data);
                break;
            
            case 'download_error':
                this.onDownloadError(message.data);
                break;
            
            case 'status_update':
                this.onStatusUpdate(message.data);
                break;
        }
    }

    addToQueue(contentData) {
        this.downloadQueue.push({
            id: Date.now() + Math.random(),
            data: contentData,
            status: 'pending',
            addedAt: new Date().toISOString()
        });

        console.log('Добавлено в очередь:', contentData);
        
        // Начинаем обработку, если не активна
        if (!this.isProcessing) {
            this.processQueue();
        }
        
        // Уведомляем popup об изменениях
        this.notifyPopup();
    }

    async processQueue() {
        if (this.isProcessing || this.downloadQueue.length === 0) {
            return;
        }

        this.isProcessing = true;

        while (this.downloadQueue.length > 0) {
            const item = this.downloadQueue.shift();
            
            try {
                await this.processDownloadItem(item);
            } catch (error) {
                console.error('Ошибка обработки элемента очереди:', error);
                item.status = 'error';
                item.error = error.message;
            }
        }

        this.isProcessing = false;
        this.notifyPopup();
    }

    async processDownloadItem(item) {
        item.status = 'processing';
        
        if (this.nativePort) {
            // Отправляем в нативное приложение
            this.nativePort.postMessage({
                type: 'download_request',
                data: item.data
            });
        } else {
            // Fallback: сохраняем в локальное хранилище для ручной обработки
            await this.saveToLocalStorage(item);
        }
        
        item.status = 'sent';
    }

    async saveToLocalStorage(item) {
        const result = await chrome.storage.local.get(['downloadHistory']);
        const history = result.downloadHistory || [];
        
        history.push(item);
        
        // Ограничиваем историю последними 100 элементами
        if (history.length > 100) {
            history.splice(0, history.length - 100);
        }
        
        await chrome.storage.local.set({ downloadHistory: history });
    }

    downloadPage(tab) {
        // Отправляем сообщение в content script для сканирования всей страницы
        chrome.tabs.sendMessage(tab.id, {
            action: 'scanFullPage'
        });
    }

    downloadMedia(info, tab) {
        const mediaData = {
            type: 'single_media',
            url: tab.url,
            timestamp: Date.now(),
            content: [{
                tag: info.mediaType === 'image' ? 'img' : 'video',
                src: info.srcUrl,
                pageUrl: info.pageUrl
            }]
        };

        this.addToQueue(mediaData);
    }

    clearQueue() {
        this.downloadQueue = [];
        this.notifyPopup();
    }

    onDownloadComplete(data) {
        console.log('Загрузка завершена:', data);
        this.showNotification('Загрузка завершена', data.filename);
    }

    onDownloadError(data) {
        console.error('Ошибка загрузки:', data);
        this.showNotification('Ошибка загрузки', data.error, 'error');
    }

    onStatusUpdate(data) {
        console.log('Обновление статуса:', data);
    }

    showNotification(title, message, type = 'basic') {
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon48.png',
            title: title,
            message: message
        });
    }

    notifyPopup() {
        // Отправляем обновление статуса в popup, если он открыт
        chrome.runtime.sendMessage({
            action: 'queueUpdate',
            queueLength: this.downloadQueue.length,
            isProcessing: this.isProcessing
        }).catch(() => {
            // Popup может быть закрыт, игнорируем ошибку
        });
    }
}

// Инициализируем менеджер загрузок
const downloadManager = new DownloadManager();

// Обработка установки расширения
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('UniContentDownloader установлен');
        
        // Открываем страницу настройки
        chrome.tabs.create({
            url: chrome.runtime.getURL('popup.html')
        });
    }
});

// Обработка обновления расширения
chrome.runtime.onStartup.addListener(() => {
    console.log('UniContentDownloader запущен');
});