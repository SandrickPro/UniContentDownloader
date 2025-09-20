#!/usr/bin/env python3
"""
UniContentDownloader - Native Messaging Host
Мост между Firefox расширением и Python downloader
"""

import json
import struct
import sys
import os
import subprocess
import threading
import queue
import time
from pathlib import Path


class NativeMessagingHost:
    def __init__(self):
        self.downloader_path = self.find_downloader_path()
        self.download_queue = queue.Queue()
        self.processing_thread = None
        self.is_running = True
        
    def find_downloader_path(self):
        """Ищем путь к установленному downloader"""
        current_dir = Path(__file__).parent
        
        # Проверяем в текущей директории
        downloader_path = current_dir / "fansly-downloader-ng" / "fansly_downloader_ng.py"
        if downloader_path.exists():
            return downloader_path
            
        # Проверяем в родительской директории
        downloader_path = current_dir.parent / "fansly-downloader-ng" / "fansly_downloader_ng.py"
        if downloader_path.exists():
            return downloader_path
            
        # Ищем в системе
        possible_paths = [
            Path.home() / "UniContentDownloader" / "fansly-downloader-ng" / "fansly_downloader_ng.py",
            Path.cwd() / "fansly-downloader-ng" / "fansly_downloader_ng.py"
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
                
        return None
    
    def read_message(self):
        """Читаем сообщение от расширения"""
        try:
            # Читаем длину сообщения (4 байта)
            raw_length = sys.stdin.buffer.read(4)
            if not raw_length:
                return None
                
            message_length = struct.unpack('=I', raw_length)[0]
            
            # Читаем само сообщение
            message = sys.stdin.buffer.read(message_length).decode('utf-8')
            return json.loads(message)
            
        except (EOFError, json.JSONDecodeError, struct.error):
            return None
    
    def send_message(self, message):
        """Отправляем сообщение в расширение"""
        try:
            encoded_message = json.dumps(message).encode('utf-8')
            message_length = len(encoded_message)
            
            # Отправляем длину сообщения
            sys.stdout.buffer.write(struct.pack('=I', message_length))
            
            # Отправляем само сообщение
            sys.stdout.buffer.write(encoded_message)
            sys.stdout.buffer.flush()
            
        except Exception as e:
            self.log_error(f"Ошибка отправки сообщения: {e}")
    
    def log_error(self, message):
        """Логирование ошибок"""
        log_file = Path(__file__).parent / "native_host.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    
    def handle_download_request(self, data):
        """Обрабатываем запрос на скачивание"""
        if not self.downloader_path:
            return {
                'type': 'download_error',
                'data': {
                    'error': 'Fansly Downloader не найден. Запустите install.py для установки.'
                }
            }
        
        # Добавляем в очередь
        self.download_queue.put(data)
        
        # Запускаем поток обработки, если не запущен
        if not self.processing_thread or not self.processing_thread.is_alive():
            self.processing_thread = threading.Thread(target=self.process_downloads)
            self.processing_thread.daemon = True
            self.processing_thread.start()
        
        return {
            'type': 'download_queued',
            'data': {
                'message': 'Добавлено в очередь загрузки'
            }
        }
    
    def process_downloads(self):
        """Обрабатываем очередь загрузок"""
        while self.is_running:
            try:
                # Получаем задачу из очереди (с таймаутом)
                data = self.download_queue.get(timeout=1)
                
                self.send_message({
                    'type': 'status_update',
                    'data': {
                        'message': 'Начинается загрузка...'
                    }
                })
                
                # Создаем временный config файл
                config_data = self.create_config_from_data(data)
                config_file = self.save_temp_config(config_data)
                
                # Запускаем downloader
                result = self.run_downloader(config_file)
                
                if result['success']:
                    self.send_message({
                        'type': 'download_complete',
                        'data': {
                            'message': 'Загрузка завершена успешно',
                            'files': result.get('files', [])
                        }
                    })
                else:
                    self.send_message({
                        'type': 'download_error',
                        'data': {
                            'error': result.get('error', 'Неизвестная ошибка')
                        }
                    })
                
                # Удаляем временный файл
                if config_file.exists():
                    config_file.unlink()
                
                self.download_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.log_error(f"Ошибка обработки загрузки: {e}")
                self.send_message({
                    'type': 'download_error',
                    'data': {
                        'error': str(e)
                    }
                })
    
    def create_config_from_data(self, data):
        """Создаем конфиг на основе данных от расширения"""
        # Извлекаем имя пользователя из URL
        username = self.extract_username_from_url(data.get('url', ''))
        
        config = {
            'username': username,
            'download_mode': self.determine_download_mode(data),
            'download_path': str(Path.home() / "Downloads" / "UniContentDownloader"),
            'separate_messages': True,
            'separate_previews': False,
            'download_previews': True,
            'mark_downloaded': True,
            'auto_choice': True
        }
        
        # Если это единичный пост, добавляем post_id
        if data.get('type') == 'post' and data.get('metadata', {}).get('postId'):
            config['post_id'] = data['metadata']['postId']
            config['download_mode'] = 'single'
        
        return config
    
    def extract_username_from_url(self, url):
        """Извлекаем имя пользователя из URL"""
        try:
            # Пример: https://fansly.com/username/posts
            parts = url.split('/')
            if 'fansly.com' in url and len(parts) > 3:
                return parts[3]
        except:
            pass
        return ''
    
    def determine_download_mode(self, data):
        """Определяем режим загрузки"""
        data_type = data.get('type', '')
        
        if data_type == 'post':
            return 'single'
        elif data_type == 'message':
            return 'messages'
        elif data_type == 'collection':
            return 'collection'
        else:
            return 'normal'
    
    def save_temp_config(self, config_data):
        """Сохраняем временный config файл"""
        temp_dir = Path.home() / ".unicontentdownloader"
        temp_dir.mkdir(exist_ok=True)
        
        config_file = temp_dir / f"temp_config_{int(time.time())}.ini"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write("[Targeted Creator]\n")
            f.write(f"username = {config_data.get('username', '')}\n\n")
            
            f.write("[Download Options]\n")
            f.write(f"download_mode = {config_data.get('download_mode', 'normal')}\n")
            f.write(f"download_path = {config_data.get('download_path', '')}\n")
            f.write(f"separate_messages = {config_data.get('separate_messages', 'true')}\n")
            f.write(f"separate_previews = {config_data.get('separate_previews', 'false')}\n")
            f.write(f"download_previews = {config_data.get('download_previews', 'true')}\n")
            f.write(f"mark_downloaded = {config_data.get('mark_downloaded', 'true')}\n")
            
            if 'post_id' in config_data:
                f.write(f"post_id = {config_data['post_id']}\n")
        
        return config_file
    
    def run_downloader(self, config_file):
        """Запускаем downloader с конфигом"""
        try:
            cmd = [
                sys.executable,
                str(self.downloader_path),
                '--config', str(config_file),
                '--non-interactive',
                '--no-prompt-on-exit'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 минут максимум
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output': result.stdout
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr or result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Таймаут загрузки (превышено 5 минут)'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run(self):
        """Основной цикл работы"""
        self.log_error("Native messaging host запущен")
        
        while True:
            message = self.read_message()
            
            if message is None:
                break
                
            response = None
            
            try:
                if message.get('type') == 'download_request':
                    response = self.handle_download_request(message.get('data'))
                elif message.get('type') == 'ping':
                    response = {'type': 'pong', 'data': {'status': 'ok'}}
                elif message.get('type') == 'get_status':
                    response = {
                        'type': 'status',
                        'data': {
                            'downloader_available': self.downloader_path is not None,
                            'queue_size': self.download_queue.qsize()
                        }
                    }
                
                if response:
                    self.send_message(response)
                    
            except Exception as e:
                self.log_error(f"Ошибка обработки сообщения: {e}")
                self.send_message({
                    'type': 'error',
                    'data': {'error': str(e)}
                })
        
        self.is_running = False
        self.log_error("Native messaging host завершен")


def main():
    """Главная функция"""
    host = NativeMessagingHost()
    
    try:
        host.run()
    except Exception as e:
        host.log_error(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()