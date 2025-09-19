#!/usr/bin/env python3
"""
UniContentDownloader - Automated Installation Script
Automates the installation of fansly-downloader-ng
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import platform
from pathlib import Path

class FanslyDownloaderInstaller:
    def __init__(self):
        self.system = platform.system()
        self.base_dir = Path.home() / "UniContentDownloader"
        self.repo_url = "https://github.com/prof79/fansly-downloader-ng"
        self.download_url = f"{self.repo_url}/archive/refs/heads/main.zip"
        
    def check_python_version(self):
        """Check if Python 3.11+ is installed"""
        if sys.version_info < (3, 11):
            raise RuntimeError(f"Python 3.11+ is required. Current version: {sys.version}")
        print(f"✓ Python {sys.version.split()[0]} detected")
        
    def check_dependencies(self):
        """Check if required system dependencies are available"""
        try:
            import pip
            print("✓ pip is available")
        except ImportError:
            raise RuntimeError("pip is not available. Please install pip first.")
            
        # Check for tkinter on Linux
        if self.system == "Linux":
            try:
                import tkinter
                print("✓ tkinter is available")
            except ImportError:
                print("⚠ tkinter not found. Run: sudo apt-get install python3-tk")
                
    def create_directories(self):
        """Create necessary directories"""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {self.base_dir}")
        
    def download_fansly_downloader(self):
        """Download and extract fansly-downloader-ng"""
        print("Downloading fansly-downloader-ng...")
        
        zip_path = self.base_dir / "fansly-downloader-ng.zip"
        urllib.request.urlretrieve(self.download_url, zip_path)
        
        print("Extracting files...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.base_dir)
            
        # Move contents from extracted folder to base directory
        extracted_folder = self.base_dir / "fansly-downloader-ng-main"
        if extracted_folder.exists():
            for item in extracted_folder.iterdir():
                shutil.move(str(item), str(self.base_dir / item.name))
            extracted_folder.rmdir()
            
        zip_path.unlink()  # Remove zip file
        print(f"✓ Downloaded and extracted to: {self.base_dir}")
        
    def install_requirements(self):
        """Install Python requirements"""
        requirements_file = self.base_dir / "requirements.txt"
        if requirements_file.exists():
            print("Installing Python requirements...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            print("✓ Requirements installed successfully")
        else:
            print("⚠ requirements.txt not found")
            
    def create_launcher_scripts(self):
        """Create launcher scripts for different platforms"""
        if self.system == "Windows":
            self.create_windows_launcher()
        else:
            self.create_unix_launcher()
            
    def create_windows_launcher(self):
        """Create Windows batch launcher"""
        launcher_content = f"""@echo off
cd /d "{self.base_dir}"
python fansly_downloader_ng.py %*
pause
"""
        launcher_path = self.base_dir / "launch_fansly_downloader.bat"
        launcher_path.write_text(launcher_content, encoding='utf-8')
        print(f"✓ Created Windows launcher: {launcher_path}")
        
    def create_unix_launcher(self):
        """Create Unix shell launcher"""
        launcher_content = f"""#!/bin/bash
cd "{self.base_dir}"
python3 fansly_downloader_ng.py "$@"
"""
        launcher_path = self.base_dir / "launch_fansly_downloader.sh"
        launcher_path.write_text(launcher_content, encoding='utf-8')
        launcher_path.chmod(0o755)  # Make executable
        print(f"✓ Created Unix launcher: {launcher_path}")
        
    def create_config_template(self):
        """Create a basic config template"""
        config_content = """[TargetedCreator]
username = 

[Authorization]
authorization_token = 
user_agent = 

[Download]
download_directory = ./Downloads
separate_messages = true
separate_previews = false
show_downloads = true
"""
        config_path = self.base_dir / "config.ini"
        if not config_path.exists():
            config_path.write_text(config_content, encoding='utf-8')
            print(f"✓ Created config template: {config_path}")
        
    def install(self):
        """Run the complete installation process"""
        try:
            print("🚀 Starting UniContentDownloader installation...")
            print("=" * 50)
            
            self.check_python_version()
            self.check_dependencies()
            self.create_directories()
            self.download_fansly_downloader()
            self.install_requirements()
            self.create_launcher_scripts()
            self.create_config_template()
            
            print("=" * 50)
            print("✅ Installation completed successfully!")
            print(f"📁 Installation directory: {self.base_dir}")
            print("\n📋 Next steps:")
            print("1. Edit config.ini to add your Fansly authorization details")
            print("2. Run the launcher script to start downloading")
            
            if self.system == "Windows":
                print("   → Double-click: launch_fansly_downloader.bat")
            else:
                print("   → Run: ./launch_fansly_downloader.sh")
                
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            sys.exit(1)

def main():
    installer = FanslyDownloaderInstaller()
    installer.install()

if __name__ == "__main__":
    main()