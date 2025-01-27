"""Utility functions for solar panel detection pipeline"""
import json
import pandas as pd
from pathlib import Path

def load_lebanon_config():
    """Load Lebanon-specific configuration"""
    with open('configs/lebanon_config.json', 'r') as f:
        return json.load(f)

def generate_detection_report(detections, output_path):
    """Generate CSV report of solar panel detections"""
    df = pd.DataFrame(detections)
    df.to_csv(output_path, index=False)
    return df

def filter_by_municipality(detections, municipality):
    """Filter detections by Lebanese municipality"""
    # Implementation for geographic filtering
    return [d for d in detections if d.get('municipality') == municipality]

def calculate_solar_potential(detections):
    """Calculate total solar potential in kWh for Lebanon"""
    total_area = sum(d.get('area_m2', 0) for d in detections)
    # Assume 150W/m2 average solar panel efficiency
    potential_kwh = total_area * 0.15 * 5.5  # 5.5 hours average sun in Lebanon
    return potential_kwh
