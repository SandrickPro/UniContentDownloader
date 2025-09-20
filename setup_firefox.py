#!/usr/bin/env python3
"""
UniContentDownloader - Firefox Extension Setup
Автоматическая настройка Firefox расширения
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
import platform

class FirefoxExtensionSetup:
    def __init__(self):
        self.extension_dir = Path(__file__).parent / "firefox-extension"
        self.manifest_path = Path(__file__).parent / "native-messaging-manifest.json"
        self.native_host_path = Path(__file__).parent / "native_host.py"
        
    def create_extension_package(self):
        """Создаем пакет расширения для установки"""
        print("📦 Создаем пакет расширения...")
        
        try:
            package_path = Path.cwd() / "UniContentDownloader-Firefox-Extension.zip"
            
            with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Добавляем все файлы расширения
                for file_path in self.extension_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(self.extension_dir)
                        zip_file.write(file_path, arcname)
            
            print(f"✅ Пакет расширения создан: {package_path}")
            return package_path
            
        except Exception as e:
            print(f"❌ Ошибка создания пакета: {e}")
            return None
    
    def setup_native_messaging_linux(self):
        """Настройка native messaging для Linux"""
        try:
            # Создаем директорию для native messaging hosts
            nm_dir = Path.home() / ".mozilla" / "native-messaging-hosts"
            nm_dir.mkdir(parents=True, exist_ok=True)
            
            # Копируем manifest с обновленным путем
            manifest_dest = nm_dir / "com.unicontentdownloader.fansly.json"
            
            # Читаем и обновляем manifest
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            
            # Обновляем путь к native host
            manifest_data['path'] = str(self.native_host_path.absolute())
            
            # Сохраняем обновленный manifest
            with open(manifest_dest, 'w', encoding='utf-8') as f:
                json.dump(manifest_data, f, indent=2)
            
            # Делаем native host исполнимым
            os.chmod(self.native_host_path, 0o755)
            
            print(f"✅ Native messaging настроен для Linux: {manifest_dest}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка настройки native messaging для Linux: {e}")
            return False
    
    def setup_native_messaging_macos(self):
        """Настройка native messaging для macOS"""
        try:
            # Создаем директорию для native messaging hosts
            nm_dir = Path.home() / "Library" / "Application Support" / "Mozilla" / "NativeMessagingHosts"
            nm_dir.mkdir(parents=True, exist_ok=True)
            
            # Копируем manifest с обновленным путем
            manifest_dest = nm_dir / "com.unicontentdownloader.fansly.json"
            
            # Читаем и обновляем manifest
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            
            # Обновляем путь к native host
            manifest_data['path'] = str(self.native_host_path.absolute())
            
            # Сохраняем обновленный manifest
            with open(manifest_dest, 'w', encoding='utf-8') as f:
                json.dump(manifest_data, f, indent=2)
            
            # Делаем native host исполнимым
            os.chmod(self.native_host_path, 0o755)
            
            print(f"✅ Native messaging настроен для macOS: {manifest_dest}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка настройки native messaging для macOS: {e}")
            return False
    
    def setup_native_messaging_windows(self):
        """Настройка native messaging для Windows"""
        try:
            import winreg
            
            # Создаем ключ реестра
            registry_path = r"Software\Mozilla\NativeMessagingHosts\com.unicontentdownloader.fansly"
            
            # Читаем и обновляем manifest
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            
            # Обновляем путь к native host (для Windows нужен полный путь)
            manifest_data['path'] = str(self.native_host_path.absolute()).replace('\\', '\\\\')
            
            # Сохраняем обновленный manifest
            with open(self.manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest_data, f, indent=2)
            
            # Создаем ключ в реестре
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_path) as key:
                winreg.SetValue(key, "", winreg.REG_SZ, str(self.manifest_path.absolute()))
            
            print(f"✅ Native messaging настроен для Windows в реестре")
            return True
            
        except ImportError:
            print("❌ Модуль winreg недоступен. Настройте вручную:")
            print(f"   Создайте ключ: HKEY_CURRENT_USER\\Software\\Mozilla\\NativeMessagingHosts\\com.unicontentdownloader.fansly")
            print(f"   Значение: {self.manifest_path.absolute()}")
            return False
        except Exception as e:
            print(f"❌ Ошибка настройки native messaging для Windows: {e}")
            return False
    
    def setup_native_messaging(self):
        """Настройка native messaging для текущей ОС"""
        system = platform.system().lower()
        
        if system == "linux":
            return self.setup_native_messaging_linux()
        elif system == "darwin":
            return self.setup_native_messaging_macos()
        elif system == "windows":
            return self.setup_native_messaging_windows()
        else:
            print(f"❌ Неподдерживаемая ОС: {system}")
            return False
    
    def print_installation_instructions(self, package_path):
        """Выводим инструкции по установке"""
        print("\n" + "="*60)
        print("🦊 ИНСТРУКЦИИ ПО УСТАНОВКЕ FIREFOX РАСШИРЕНИЯ")
        print("="*60)
        print()
        print("1. ВРЕМЕННАЯ УСТАНОВКА (для разработки):")
        print("   - Откройте Firefox")
        print("   - Введите в адресной строке: about:debugging")
        print("   - Перейдите на вкладку 'This Firefox'")
        print("   - Нажмите 'Load Temporary Add-on'")
        print(f"   - Выберите файл: {self.extension_dir / 'manifest.json'}")
        print()
        print("2. ПОСТОЯННАЯ УСТАНОВКА:")
        print(f"   - Используйте пакет: {package_path}")
        print("   - Подпишите расширение для публикации")
        print("   - Или установите Firefox Developer Edition для unsigned extensions")
        print()
        print("3. ПРОВЕРКА РАБОТЫ:")
        print("   - Откройте fansly.com")
        print("   - Нажмите на иконку UniContentDownloader")
        print("   - Активируйте загрузчик")
        print("   - Кнопки скачивания должны появиться на контенте")
        print()
        print("4. УСТРАНЕНИЕ ПРОБЛЕМ:")
        print("   - Проверьте консоль браузера (F12)")
        print("   - Убедитесь, что native_host.py исполнимый")
        print("   - Проверьте пути в native messaging manifest")
        print()
        print("📖 Подробная документация: README.md")
        print("🐛 Сообщить об ошибке: GitHub Issues")
    
    def setup(self):
        """Выполняем полную настройку"""
        print("🦊 UniContentDownloader - Настройка Firefox расширения")
        print("="*60)
        
        # Проверяем наличие файлов
        if not self.extension_dir.exists():
            print("❌ Директория расширения не найдена")
            return False
        
        if not self.native_host_path.exists():
            print("❌ Native host скрипт не найден")
            return False
        
        # Создаем пакет расширения
        package_path = self.create_extension_package()
        if not package_path:
            return False
        
        # Настраиваем native messaging
        if not self.setup_native_messaging():
            print("⚠️ Native messaging не настроен. Расширение будет работать в ограниченном режиме.")
        
        # Выводим инструкции
        self.print_installation_instructions(package_path)
        
        print("\n✅ Настройка завершена!")
        return True

def main():
    """Главная функция"""
    setup = FirefoxExtensionSetup()
    
    try:
        success = setup.setup()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Настройка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()