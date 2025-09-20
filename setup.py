from setuptools import setup, find_packages

setup(
    name="unicontentdownloader",
    version="1.0.0",
    description="Universal Content Downloader - Download content from various sources",
    author="SandrickPro",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "urllib3>=1.26.0", 
        "beautifulsoup4>=4.11.0",
        "tqdm>=4.64.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "responses>=0.22.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "unicontentdownloader=unicontentdownloader.cli:main",
        ],
    },
    python_requires=">=3.7",
)