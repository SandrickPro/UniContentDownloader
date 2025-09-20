# UniContentDownloader

**Автоматическая установка и улучшенный функционал для fansly-downloader-ng с Firefox расширением**

UniContentDownloader - это комплексное решение для автоматического скачивания контента с Fansly, включающее:

1. **Автоматическую установку** оригинального [fansly-downloader-ng](https://github.com/prof79/fansly-downloader-ng)
2. **Firefox расширение** для скачивания контента прямо со страниц сайта
3. **Мост между браузером и загрузчиком** через native messaging

## ✨ Особенности

- 🤖 **Автоматическая установка** - один скрипт устанавливает все необходимые компоненты
- 🦊 **Firefox интеграция** - кнопки скачивания прямо на страницах Fansly
- 📥 **Умное сканирование** - автоматическое обнаружение контента на странице
- 🔄 **Очередь загрузок** - управление множественными загрузками
- ⚙️ **Гибкие настройки** - качество видео, пути загрузки и многое другое
- 🔒 **Безопасность** - все данные обрабатываются локально

## 🚀 Быстрый старт

### 1. Установка

```bash
# Клонируйте репозиторий
git clone https://github.com/SandrickPro/UniContentDownloader.git
cd UniContentDownloader

# Запустите автоматическую установку
python install.py
```

### 2. Настройка Firefox расширения

```bash
# Настройте Firefox интеграцию
python setup_firefox.py
```

### 3. Использование

1. Откройте Firefox и установите расширение (следуйте инструкциям из setup_firefox.py)
2. Перейдите на fansly.com
3. Нажмите на иконку UniContentDownloader в панели расширений
4. Активируйте загрузчик
5. Кнопки скачивания появятся на контенте

## 📋 Требования

- **Python 3.11+**
- **Firefox браузер**
- **Аккаунт Fansly** с активной сессией

### Поддерживаемые ОС:
- ✅ Windows 10/11
- ✅ Linux (Ubuntu, Debian, и др.)
- ✅ macOS

## 🛠️ Установка по шагам

### Шаг 1: Подготовка

```bash
# Убедитесь, что Python 3.11+ установлен
python --version

# Клонируйте репозиторий
git clone https://github.com/SandrickPro/UniContentDownloader.git
cd UniContentDownloader
```

### Шаг 2: Автоматическая установка

```bash
# Запустите установщик
python install.py
```

Установщик автоматически:
- Скачает fansly-downloader-ng
- Установит все Python зависимости
- Создаст скрипты запуска
- Настроит Firefox интеграцию

### Шаг 3: Настройка Firefox

```bash
# Настройте расширение для Firefox
python setup_firefox.py
```

Следуйте инструкциям для установки расширения в Firefox.

## 🦊 Использование Firefox расширения

### Активация
1. Откройте страницу на fansly.com
2. Нажмите на иконку UniContentDownloader в панели расширений
3. Нажмите "Активировать" в popup окне

### Скачивание контента
- **Автоматическое сканирование**: кнопки появятся на всех найденных медиа
- **Ручное сканирование**: нажмите "Сканировать страницу" в popup
- **Контекстное меню**: правый клик на изображении/видео → "Скачать через UniContentDownloader"

### Управление очередью
- Просмотр очереди загрузок в popup
- Очистка очереди
- Статус обработки в реальном времени

## ⚙️ Настройки

### В Firefox расширении:
- **Автоматическое сканирование** - сканирует страницу при изменениях
- **Уведомления** - показывает статус загрузок
- **Качество видео** - выбор качества для загрузки

### В fansly-downloader-ng:
Редактируйте `fansly-downloader-ng/config.ini`:
- Путь загрузки
- Режимы скачивания
- Организация файлов
- И многое другое

## 📁 Структура проекта

```
UniContentDownloader/
├── install.py                     # Основной установщик
├── setup_firefox.py              # Настройка Firefox расширения
├── native_host.py                 # Мост браузер-загрузчик
├── native-messaging-manifest.json # Конфиг native messaging
├── firefox-extension/             # Файлы Firefox расширения
│   ├── manifest.json
│   ├── background.js
│   ├── content.js
│   ├── popup.html
│   ├── popup.js
│   ├── popup.css
│   ├── styles.css
│   └── icons/
├── fansly-downloader-ng/         # Автоматически скачивается
└── FanslyDownloader.bat|.sh     # Скрипты запуска
```

## 🔧 Продвинутое использование

### Автоматизация через командную строку

```bash
# Прямой вызов загрузчика
cd fansly-downloader-ng
python fansly_downloader_ng.py --user "username" --mode timeline

# Неинтерактивный режим
python fansly_downloader_ng.py --non-interactive --no-prompt-on-exit
```

### Настройка quality profiles

Создайте предустановки в `config.ini`:
```ini
[Download Options]
video_quality = best
download_previews = true
separate_messages = true
```

### Интеграция с планировщиком

Windows (Task Scheduler):
```batch
schtasks /create /tn "FanslyDownloader" /sc daily /st 02:00 /tr "C:\path\to\FanslyDownloader.bat"
```

Linux (cron):
```bash
0 2 * * * /path/to/FanslyDownloader.sh
```

## 🛠️ Разработка

### Сборка расширения

```bash
cd firefox-extension
zip -r ../UniContentDownloader-Extension.zip *
```

### Отладка

```bash
# Логи native host
tail -f native_host.log

# Логи загрузчика  
tail -f fansly-downloader-ng/fansly_downloader_ng.log

# Консоль браузера (F12)
```

## 🆘 Устранение неполадок

### Расширение не работает
1. Проверьте, что native messaging настроен: `python setup_firefox.py`
2. Убедитесь, что `native_host.py` исполнимый
3. Проверьте консоль браузера (F12) на ошибки

### Загрузки не начинаются
1. Проверьте настройки Fansly аккаунта
2. Обновите токены в `config.ini`
3. Запустите загрузчик вручную для диагностики

### Ошибки Python
1. Проверьте версию Python (3.11+)
2. Переустановите зависимости: `pip install -r requirements.txt`
3. Проверьте пути в конфигурации

## 📝 Лицензия

Этот проект лицензирован под GPL-3.0 License - см. файл [LICENSE](LICENSE).

## 🤝 Содействие

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📞 Поддержка

- 🐛 **Ошибки**: [GitHub Issues](https://github.com/SandrickPro/UniContentDownloader/issues)
- 💬 **Обсуждение**: [GitHub Discussions](https://github.com/SandrickPro/UniContentDownloader/discussions)
- 📖 **Документация**: [Wiki](https://github.com/SandrickPro/UniContentDownloader/wiki)

## ⚠️ Дисклеймер

Этот проект создан исключительно в образовательных целях. Пользователи несут полную ответственность за соблюдение условий использования Fansly и применимого законодательства. Разработчики не несут ответственности за любое неправомерное использование данного программного обеспечения.

## 🙏 Благодарности

- [prof79](https://github.com/prof79) за оригинальный [fansly-downloader-ng](https://github.com/prof79/fansly-downloader-ng)
- [Avnsx](https://github.com/Avnsx) за изначальный Fansly Downloader
- Сообществу разработчиков за вклад и обратную связь
