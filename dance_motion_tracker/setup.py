"""
Setup configuration for Dance Motion Tracker
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="dance-motion-tracker",
    version="1.0.0",
    author="Dance Motion Tracker Team",
    author_email="contact@dancemotiontracker.com",
    description="AI-powered dance motion tracking and 3D animation pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dance-motion-tracker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video :: Capture",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "gpu": [
            "torch>=2.2.0",
            "torchvision>=0.17.0",
            "torchaudio>=2.2.0",
            "cupy-cuda11x>=12.0.0",
            "nvidia-ml-py>=12.0.0",
        ],
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
            "pre-commit>=2.15.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "dance-motion-tracker=run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "dance_motion_tracker": [
            "app/templates/*.html",
            "app/static/css/*.css",
            "app/static/js/*.js",
            "config/*.py",
            "docs/*.md",
            "examples/*",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/dance-motion-tracker/issues",
        "Source": "https://github.com/yourusername/dance-motion-tracker",
        "Documentation": "https://github.com/yourusername/dance-motion-tracker/docs",
    },
    keywords="dance motion tracking mediapipe opencv blender 3d animation ai computer-vision",
)