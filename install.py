#!/usr/bin/env python3
"""
UniContentDownloader - Automated Installation Script
Автоматическая установка fansly-downloader-ng
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path

class FanslyDownloaderInstaller:
    def __init__(self):
        self.repo_url = "https://github.com/prof79/fansly-downloader-ng"
        self.archive_url = f"{self.repo_url}/archive/refs/heads/main.zip"
        self.install_dir = Path.cwd() / "fansly-downloader-ng"
        self.temp_dir = Path.cwd() / "temp_download"
        
    def check_python_version(self):
        """Проверяем версию Python (требуется 3.11+)"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 11):
            print("❌ Ошибка: Требуется Python 3.11 или выше")
            print(f"   Текущая версия: {version.major}.{version.minor}.{version.micro}")
            print("   Скачайте Python с https://www.python.org/downloads/")
            return False
        print(f"✅ Python версия {version.major}.{version.minor}.{version.micro} подходит")
        return True
        
    def download_repository(self):
        """Скачиваем репозиторий fansly-downloader-ng"""
        print("📥 Скачиваем fansly-downloader-ng...")
        
        try:
            # Создаем временную директорию
            self.temp_dir.mkdir(exist_ok=True)
            
            # Скачиваем архив
            zip_path = self.temp_dir / "fansly-downloader-ng.zip"
            urllib.request.urlretrieve(self.archive_url, zip_path)
            
            # Извлекаем архив
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            # Перемещаем извлеченные файлы в целевую директорию
            extracted_dir = self.temp_dir / "fansly-downloader-ng-main"
            if self.install_dir.exists():
                shutil.rmtree(self.install_dir)
            shutil.move(str(extracted_dir), str(self.install_dir))
            
            # Удаляем временные файлы
            shutil.rmtree(self.temp_dir)
            
            print(f"✅ Репозиторий скачан в {self.install_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при скачивании: {e}")
            return False
    
    def install_dependencies(self):
        """Устанавливаем зависимости Python"""
        print("📦 Устанавливаем зависимости...")
        
        requirements_file = self.install_dir / "requirements.txt"
        if not requirements_file.exists():
            print("❌ Файл requirements.txt не найден")
            return False
        
        try:
            # Проверяем наличие системных зависимостей для plyvel
            self.check_system_dependencies()
            
            # Устанавливаем зависимости
            cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.install_dir)
            
            if result.returncode == 0:
                print("✅ Зависимости установлены успешно")
                return True
            else:
                print(f"❌ Ошибка установки зависимостей: {result.stderr}")
                print("\n🔧 Попытка установки без plyvel-ci...")
                return self.install_dependencies_fallback()
                
        except Exception as e:
            print(f"❌ Ошибка при установке зависимостей: {e}")
            return self.install_dependencies_fallback()
    
    def check_system_dependencies(self):
        """Проверяем системные зависимости"""
        if os.name != 'nt':  # Не Windows
            print("ℹ️ Для полной функциональности может потребоваться установка системных библиотек:")
            print("   Ubuntu/Debian: sudo apt-get install libleveldb-dev")
            print("   CentOS/RHEL: sudo yum install leveldb-devel")
            print("   macOS: brew install leveldb")
    
    def install_dependencies_fallback(self):
        """Устанавливаем зависимости без проблемных пакетов"""
        try:
            # Создаем упрощенный requirements.txt без plyvel-ci
            requirements_file = self.install_dir / "requirements.txt"
            fallback_requirements = []
            
            with open(requirements_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and 'plyvel' not in line:
                        fallback_requirements.append(line)
            
            # Устанавливаем упрощенный набор
            for requirement in fallback_requirements:
                cmd = [sys.executable, "-m", "pip", "install", requirement]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"⚠️ Не удалось установить {requirement}")
            
            print("✅ Основные зависимости установлены (некоторые функции могут быть ограничены)")
            print("ℹ️ Для полной функциональности установите system dependencies и повторите установку")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка fallback установки: {e}")
            return False
    
    def create_launcher_scripts(self):
        """Создаем скрипты запуска"""
        print("🚀 Создаем скрипты запуска...")
        
        # Скрипт для Windows
        bat_content = f"""@echo off
cd /d "{self.install_dir}"
python fansly_downloader_ng.py %*
pause
"""
        bat_file = Path.cwd() / "FanslyDownloader.bat"
        with open(bat_file, 'w', encoding='utf-8') as f:
            f.write(bat_content)
        
        # Скрипт для Linux/macOS
        sh_content = f"""#!/bin/bash
cd "{self.install_dir}"
python3 fansly_downloader_ng.py "$@"
read -p "Нажмите Enter для выхода..."
"""
        sh_file = Path.cwd() / "FanslyDownloader.sh"
        with open(sh_file, 'w', encoding='utf-8') as f:
            f.write(sh_content)
        
        # Делаем shell скрипт исполнимым на Unix-подобных системах
        if os.name != 'nt':
            os.chmod(sh_file, 0o755)
        
        print("✅ Скрипты запуска созданы:")
        print(f"   Windows: {bat_file}")
        print(f"   Linux/macOS: {sh_file}")
        
        return True
    
    def setup_firefox_extension(self):
        """Настраиваем Firefox расширение и native messaging"""
        print("🦊 Настраиваем интеграцию с Firefox...")
        
        try:
            # Обновляем native messaging manifest с правильным путем
            native_host_path = Path.cwd() / "native_host.py"
            manifest_path = Path.cwd() / "native-messaging-manifest.json"
            
            # Читаем и обновляем manifest
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = f.read()
            
            # Заменяем placeholder на реальный путь
            if os.name == 'nt':
                # Windows
                manifest = manifest.replace('PLACEHOLDER_PATH', str(native_host_path).replace('\\', '\\\\'))
            else:
                # Linux/macOS
                manifest = manifest.replace('PLACEHOLDER_PATH', str(native_host_path))
            
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(manifest)
            
            # Создаем инструкции для установки расширения
            instructions_path = Path.cwd() / "Firefox_Extension_Setup.txt"
            instructions = f"""
ИНСТРУКЦИЯ ПО УСТАНОВКЕ FIREFOX РАСШИРЕНИЯ
==========================================

1. УСТАНОВКА NATIVE MESSAGING HOST:
   
   Для Linux/macOS:
   - Скопируйте файл native-messaging-manifest.json в:
     ~/.mozilla/native-messaging-hosts/com.unicontentdownloader.fansly.json
   
   Для Windows:
   - Создайте ключ в реестре:
     HKEY_CURRENT_USER\\Software\\Mozilla\\NativeMessagingHosts\\com.unicontentdownloader.fansly
   - Установите значение по умолчанию на путь к native-messaging-manifest.json

2. УСТАНОВКА РАСШИРЕНИЯ В FIREFOX:
   
   - Откройте Firefox
   - Введите в адресной строке: about:debugging
   - Нажмите "This Firefox" (Этот Firefox)
   - Нажмите "Load Temporary Add-on" (Загрузить временное дополнение)
   - Выберите файл: {Path.cwd() / "firefox-extension" / "manifest.json"}

3. АВТОМАТИЧЕСКАЯ НАСТРОЙКА (рекомендуется):
   
   Запустите скрипт: python setup_firefox.py
   
   Этот скрипт автоматически:
   - Установит native messaging host
   - Создаст пакет расширения
   - Даст инструкции по финальной установке

4. ИСПОЛЬЗОВАНИЕ:
   
   - Откройте сайт fansly.com в Firefox
   - Нажмите на иконку UniContentDownloader в панели расширений
   - Активируйте загрузчик
   - Кнопки скачивания появятся на контенте

ПОДДЕРЖКА:
- GitHub: https://github.com/SandrickPro/UniContentDownloader
- Документация: {Path.cwd() / "README.md"}
"""
            
            with open(instructions_path, 'w', encoding='utf-8') as f:
                f.write(instructions)
            
            print("✅ Firefox интеграция настроена")
            print(f"📖 Инструкции сохранены в: {instructions_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка настройки Firefox интеграции: {e}")
            return False
    
    def install(self):
        """Выполняем полную установку"""
        print("🎯 UniContentDownloader - Автоматическая установка")
        print("=" * 50)
        
        if not self.check_python_version():
            return False
        
        if not self.download_repository():
            return False
        
        if not self.install_dependencies():
            return False
        
        if not self.create_launcher_scripts():
            return False
        
        if not self.setup_firefox_extension():
            return False
        
        print("\n🎉 Установка завершена успешно!")
        print(f"📁 Fansly Downloader установлен в: {self.install_dir}")
        print("\n📋 Для запуска используйте:")
        print("   Windows: FanslyDownloader.bat")
        print("   Linux/macOS: ./FanslyDownloader.sh")
        print("\n🦊 Firefox расширение:")
        print("   Следуйте инструкциям в Firefox_Extension_Setup.txt")
        print("   Или запустите: python setup_firefox.py")
        print("\n📖 Документация: https://github.com/prof79/fansly-downloader-ng/wiki")
        
        return True

def main():
    """Главная функция"""
    installer = FanslyDownloaderInstaller()
    
    try:
        success = installer.install()
        if success:
            input("\nНажмите Enter для выхода...")
        else:
            input("\nУстановка не удалась. Нажмите Enter для выхода...")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Установка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()