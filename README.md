# Robust-Slicer-Pipeline

A modular Python-based tool designed to transform 3D STL/OBJ meshes into 2D manifold polygons using a Cura-inspired bucketing approach and even-odd topology logic.

## Prerequisites

- **Python Version:** 3.10.11
- **Main libraries** trimesh, shapely 

## Installation

It is highly recommended to use a virtual environment to manage dependencies and avoid conflicts with system-wide packages.

### 1. Create a Virtual Environment
Navigate to your project folder and run:
```bash
# Create the environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Install all requirements - 
pip install -r requirements.txt
