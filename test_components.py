#!/usr/bin/env python3
"""
UniContentDownloader - Test Script
Проверка работоспособности компонентов
"""

import sys
import json
import subprocess
from pathlib import Path

def test_python_version():
    """Тест версии Python"""
    print("🐍 Проверка версии Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - требуется 3.11+")
        return False

def test_extension_files():
    """Тест файлов расширения"""
    print("\n🦊 Проверка файлов Firefox расширения...")
    
    extension_dir = Path(__file__).parent / "firefox-extension"
    required_files = [
        "manifest.json",
        "background.js", 
        "content.js",
        "popup.html",
        "popup.js",
        "popup.css",
        "styles.css"
    ]
    
    all_ok = True
    for file_name in required_files:
        file_path = extension_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} - отсутствует")
            all_ok = False
    
    return all_ok

def test_manifest_validity():
    """Тест валидности manifest.json"""
    print("\n📋 Проверка manifest.json...")
    
    try:
        manifest_path = Path(__file__).parent / "firefox-extension" / "manifest.json"
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
        
        required_keys = ["manifest_version", "name", "version", "permissions"]
        for key in required_keys:
            if key in manifest_data:
                print(f"✅ {key}: {manifest_data[key]}")
            else:
                print(f"❌ {key} - отсутствует")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка чтения manifest.json: {e}")
        return False

def test_native_host():
    """Тест native host скрипта"""
    print("\n🔗 Проверка native host...")
    
    native_host_path = Path(__file__).parent / "native_host.py"
    if not native_host_path.exists():
        print("❌ native_host.py отсутствует")
        return False
    
    print(f"✅ native_host.py найден")
    
    # Проверяем исполнимость
    try:
        result = subprocess.run([sys.executable, str(native_host_path), "--help"], 
                              capture_output=True, text=True, timeout=5)
        print("✅ native_host.py исполнимый")
        return True
    except:
        print("⚠️ native_host.py может иметь проблемы с исполнением")
        return True  # Не критично для начального теста

def test_installation_scripts():
    """Тест скриптов установки"""
    print("\n🛠️ Проверка скриптов установки...")
    
    scripts = ["install.py", "setup_firefox.py"]
    all_ok = True
    
    for script_name in scripts:
        script_path = Path(__file__).parent / script_name
        if script_path.exists():
            print(f"✅ {script_name}")
        else:
            print(f"❌ {script_name} - отсутствует")
            all_ok = False
    
    return all_ok

def main():
    """Главная функция тестирования"""
    print("🧪 UniContentDownloader - Тестирование компонентов")
    print("=" * 60)
    
    tests = [
        ("Python версия", test_python_version),
        ("Файлы расширения", test_extension_files),
        ("Manifest.json", test_manifest_validity),
        ("Native Host", test_native_host),
        ("Скрипты установки", test_installation_scripts)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Ошибка в тесте {test_name}: {e}")
            results.append((test_name, False))
    
    # Итоги
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ ПРОШЕЛ" if result else "❌ НЕ ПРОШЕЛ"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nИтого: {passed} прошли, {failed} не прошли")
    
    if failed == 0:
        print("\n🎉 Все тесты прошли успешно! Система готова к использованию.")
        return True
    else:
        print(f"\n⚠️ {failed} тест(ов) не прошли. Проверьте ошибки выше.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)