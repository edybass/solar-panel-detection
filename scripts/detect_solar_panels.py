"""Demo script for solar panel detection"""
import argparse
import sys
from pathlib import Path
sys.path.append('src')

from solar_detector import SolarPanelDetector
from evaluation import ModelEvaluator

def main():
    parser = argparse.ArgumentParser(description='Detect solar panels in satellite imagery')
    parser.add_argument('--image', required=True, help='Path to satellite image')
    parser.add_argument('--model', default='models/solar_detector.h5', help='Path to trained model')
    parser.add_argument('--confidence', type=float, default=0.7, help='Confidence threshold')
    
    args = parser.parse_args()
    
    print(f"🛰️ Solar Panel Detection for Lebanon Environmental Monitoring")
    print(f"Processing: {args.image}")
    
    # Initialize detector
    detector = SolarPanelDetector()
    
    # Load model (placeholder)
    print("📡 Loading trained model...")
    # detector.load_model(args.model)
    
    # Run detection
    print("🔍 Detecting solar panels...")
    detections = detector.detect_solar_panels(args.image, args.confidence)
    
    print(f"✅ Found {len(detections)} potential solar installations")
    print("🌱 Contributing to Lebanon's renewable energy mapping!")

if __name__ == "__main__":
    main()
