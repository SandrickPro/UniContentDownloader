/**
 * UniContentDownloader - Popup Script
 * Интерфейс управления расширением
 */

class PopupController {
    constructor() {
        this.isDownloaderActive = false;
        this.queueLength = 0;
        this.isProcessing = false;
        this.currentTab = null;
        this.init();
    }

    async init() {
        await this.loadSettings();
        await this.getCurrentTab();
        this.setupEventListeners();
        this.updateUI();
        this.startStatusUpdates();
        
        console.log('Popup инициализирован');
    }

    async getCurrentTab() {
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
        this.currentTab = tabs[0];
        this.updatePageInfo();
    }

    updatePageInfo() {
        const pageElement = document.getElementById('current-page');
        
        if (this.currentTab && this.currentTab.url.includes('fansly.com')) {
            pageElement.textContent = 'Fansly - Активна';
            pageElement.style.color = '#4CAF50';
        } else {
            pageElement.textContent = 'Не на Fansly';
            pageElement.style.color = '#f44336';
        }
    }

    setupEventListeners() {
        // Кнопка активации/деактивации
        document.getElementById('toggle-downloader').addEventListener('click', () => {
            this.toggleDownloader();
        });

        // Кнопка сканирования страницы
        document.getElementById('scan-page').addEventListener('click', () => {
            this.scanPage();
        });

        // Кнопка очистки очереди
        document.getElementById('clear-queue').addEventListener('click', () => {
            this.clearQueue();
        });

        // Настройки
        document.getElementById('auto-scan').addEventListener('change', (e) => {
            this.saveSetting('autoScan', e.target.checked);
        });

        document.getElementById('show-notifications').addEventListener('change', (e) => {
            this.saveSetting('showNotifications', e.target.checked);
        });

        document.getElementById('video-quality').addEventListener('change', (e) => {
            this.saveSetting('videoQuality', e.target.value);
        });

        // Ссылки в футере
        document.getElementById('open-settings').addEventListener('click', (e) => {
            e.preventDefault();
            this.openSettings();
        });

        document.getElementById('open-help').addEventListener('click', (e) => {
            e.preventDefault();
            this.openHelp();
        });

        document.getElementById('open-logs').addEventListener('click', (e) => {
            e.preventDefault();
            this.openLogs();
        });

        // Слушаем сообщения от background script
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            if (message.action === 'queueUpdate') {
                this.queueLength = message.queueLength;
                this.isProcessing = message.isProcessing;
                this.updateQueueStatus();
            }
        });
    }

    async toggleDownloader() {
        if (!this.currentTab || !this.currentTab.url.includes('fansly.com')) {
            this.showError('Необходимо открыть страницу Fansly');
            return;
        }

        try {
            const response = await chrome.tabs.sendMessage(this.currentTab.id, {
                action: 'toggleDownloader'
            });

            if (response.success) {
                this.isDownloaderActive = !this.isDownloaderActive;
                this.updateToggleButton();
            }
        } catch (error) {
            console.error('Ошибка переключения:', error);
            this.showError('Ошибка связи с content script');
        }
    }

    async scanPage() {
        if (!this.currentTab || !this.currentTab.url.includes('fansly.com')) {
            this.showError('Необходимо открыть страницу Fansly');
            return;
        }

        try {
            await chrome.tabs.sendMessage(this.currentTab.id, {
                action: 'scanFullPage'
            });
            
            this.showSuccess('Сканирование страницы запущено');
        } catch (error) {
            console.error('Ошибка сканирования:', error);
            this.showError('Ошибка сканирования страницы');
        }
    }

    async clearQueue() {
        try {
            await chrome.runtime.sendMessage({
                action: 'clearQueue'
            });
            
            this.queueLength = 0;
            this.updateQueueStatus();
            this.showSuccess('Очередь очищена');
        } catch (error) {
            console.error('Ошибка очистки очереди:', error);
            this.showError('Ошибка очистки очереди');
        }
    }

    updateToggleButton() {
        const button = document.getElementById('toggle-downloader');
        const text = document.getElementById('toggle-text');
        
        if (this.isDownloaderActive) {
            text.textContent = 'Деактивировать';
            button.style.background = 'linear-gradient(135deg, #f44336, #d32f2f)';
        } else {
            text.textContent = 'Активировать';
            button.style.background = 'linear-gradient(135deg, #4CAF50, #45a049)';
        }
    }

    updateQueueStatus() {
        const queueStatus = document.getElementById('queue-status');
        const statusText = this.queueLength === 0 ? 'Пуста' : `${this.queueLength} элементов`;
        
        queueStatus.textContent = statusText;
        
        if (this.isProcessing) {
            queueStatus.style.color = '#2196F3';
            queueStatus.textContent += ' (обработка...)';
        } else {
            queueStatus.style.color = '#333';
        }
        
        this.updateQueueList();
    }

    async updateQueueList() {
        const queueList = document.getElementById('queue-list');
        
        try {
            const result = await chrome.storage.local.get(['downloadHistory']);
            const history = result.downloadHistory || [];
            
            if (history.length === 0) {
                queueList.innerHTML = '<div class="queue-empty">Очередь пуста</div>';
                return;
            }
            
            const recentItems = history.slice(-5).reverse(); // Последние 5 элементов
            
            queueList.innerHTML = recentItems.map(item => `
                <div class="queue-item">
                    <div class="queue-item-info">
                        <div class="queue-item-title">${item.data.type}</div>
                        <div class="queue-item-details">${item.data.content.length} файлов</div>
                    </div>
                    <div class="queue-item-status status-${item.status}">${this.getStatusText(item.status)}</div>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Ошибка загрузки истории:', error);
        }
    }

    getStatusText(status) {
        const statusMap = {
            'pending': 'Ожидает',
            'processing': 'Обработка',
            'sent': 'Отправлено',
            'complete': 'Завершено',
            'error': 'Ошибка'
        };
        
        return statusMap[status] || status;
    }

    async updateConnectionStatus() {
        const statusElement = document.getElementById('connection-status');
        
        try {
            // Проверяем подключение к background script
            await chrome.runtime.sendMessage({ action: 'ping' });
            statusElement.textContent = 'Подключено';
            statusElement.style.color = '#4CAF50';
        } catch (error) {
            statusElement.textContent = 'Отключено';
            statusElement.style.color = '#f44336';
        }
    }

    startStatusUpdates() {
        // Обновляем статус каждые 5 секунд
        setInterval(() => {
            this.updateConnectionStatus();
            this.updateQueueList();
        }, 5000);
        
        // Первоначальное обновление
        this.updateConnectionStatus();
    }

    async loadSettings() {
        try {
            const result = await chrome.storage.sync.get({
                autoScan: true,
                showNotifications: true,
                videoQuality: 'best'
            });
            
            document.getElementById('auto-scan').checked = result.autoScan;
            document.getElementById('show-notifications').checked = result.showNotifications;
            document.getElementById('video-quality').value = result.videoQuality;
        } catch (error) {
            console.error('Ошибка загрузки настроек:', error);
        }
    }

    async saveSetting(key, value) {
        try {
            await chrome.storage.sync.set({ [key]: value });
            console.log(`Настройка ${key} сохранена:`, value);
        } catch (error) {
            console.error('Ошибка сохранения настройки:', error);
        }
    }

    updateUI() {
        this.updateToggleButton();
        this.updateQueueStatus();
    }

    openSettings() {
        chrome.tabs.create({
            url: chrome.runtime.getURL('settings.html')
        });
    }

    openHelp() {
        chrome.tabs.create({
            url: 'https://github.com/SandrickPro/UniContentDownloader/wiki'
        });
    }

    openLogs() {
        chrome.tabs.create({
            url: chrome.runtime.getURL('logs.html')
        });
    }

    showSuccess(message) {
        this.showMessage(message, 'success');
    }

    showError(message) {
        this.showMessage(message, 'error');
    }

    showMessage(message, type) {
        // Создаем временное уведомление
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 16px;
            border-radius: 6px;
            color: white;
            font-size: 13px;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        if (type === 'success') {
            notification.style.background = '#4CAF50';
        } else {
            notification.style.background = '#f44336';
        }
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
}

// Инициализируем popup при загрузке
document.addEventListener('DOMContentLoaded', () => {
    new PopupController();
});