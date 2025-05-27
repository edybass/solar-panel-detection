# Installation Guide

## System Requirements
- Python 3.8 or higher
- GDAL/OGR (for rasterio)
- 8GB+ RAM recommended
- CUDA-compatible GPU (optional, for training)

## Quick Installation
```bash
git clone https://github.com/edybass/solar-panel-detection.git
cd solar-panel-detection
pip install -r requirements.txt
```

## Docker Installation
```bash
docker build -t solar-detection .
docker run -v $(pwd)/data:/app/data solar-detection
```

## Verify Installation
```bash
python -c "import src.solar_detector; print('Installation successful!')"
pytest tests/ -v
```
