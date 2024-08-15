"""
Solar Panel Detection System - Main Module
High-accuracy detection of solar panels in aerial and satellite imagery
"""

import cv2
import numpy as np
import torch
from pathlib import Path
import json
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    """Container for detection results."""
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    confidence: float
    area_sqm: float
    estimated_power_kw: float
    panel_type: str
    efficiency_score: float


class SolarPanelDetector:
    """Main class for solar panel detection in imagery."""

    # Average panel specifications
    PANEL_SPECS = {
        'residential': {
            'avg_size_sqm': 1.65,
            'watts_per_sqm': 200,
            'efficiency': 0.20
        },
        'commercial': {
            'avg_size_sqm': 2.0,
            'watts_per_sqm': 250,
            'efficiency': 0.22
        },
        'utility': {
            'avg_size_sqm': 2.5,
            'watts_per_sqm': 300,
            'efficiency': 0.24
        }
    }

    def __init__(self, model_name: str = 'yolov8', device: str = 'auto'):
        """
        Initialize the solar panel detector.

        Args:
            model_name: Model to use ('yolov8', 'efficientdet', 'custom')
            device: Device to run on ('cpu', 'cuda', 'auto')
        """
        self.model_name = model_name
        self.device = self._get_device(device)
        self.model = None
        self.load_model()

    def _get_device(self, device: str) -> str:
        """Determine the best device to use."""
        if device == 'auto':
            return 'cuda' if torch.cuda.is_available() else 'cpu'
        return device

    def load_model(self):
        """Load the pre-trained model."""
        model_path = Path(f"data/models/solar_{self.model_name}.pt")

        if self.model_name == 'yolov8':
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            logger.info(f"Loaded YOLOv8 model from {model_path}")
        elif self.model_name == 'efficientdet':
            # Load EfficientDet model
            pass
        else:
            # Load custom model
            pass

    def detect(self, image_path: str, confidence_threshold: float = 0.5) -> Dict:
        """
        Detect solar panels in an image.

        Args:
            image_path: Path to the input image
            confidence_threshold: Minimum confidence for detections

        Returns:
            Dictionary containing detection results
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")

        height, width = image.shape[:2]

        # Run detection
        if self.model_name == 'yolov8':
            results = self.model(image, conf=confidence_threshold)
            detections = self._process_yolo_results(results, width, height)
        else:
            # Process other models
            detections = []

        # Analyze results
        analysis = self._analyze_detections(detections, image)

        return {
            'image_path': image_path,
            'image_size': (width, height),
            'detections': detections,
            'panel_count': len(detections),
            'total_area_sqm': analysis['total_area'],
            'estimated_kwh': analysis['estimated_power'],
            'coverage_percentage': analysis['coverage_percentage'],
            'panel_distribution': analysis['distribution'],
            'timestamp': datetime.now().isoformat()
        }

    def _process_yolo_results(self, results, img_width: int, img_height: int) -> List[DetectionResult]:
        """Process YOLO detection results."""
        detections = []

        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    # Get coordinates
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = box.conf[0].item()

                    # Calculate area (assuming overhead view)
                    pixel_area = (x2 - x1) * (y2 - y1)
                    # Convert to square meters (example conversion)
                    area_sqm = self._pixels_to_sqm(pixel_area, img_width, img_height)

                    # Determine panel type based on size
                    panel_type = self._classify_panel_type(area_sqm)

                    # Estimate power generation
                    specs = self.PANEL_SPECS[panel_type]
                    power_kw = (area_sqm * specs['watts_per_sqm'] * specs['efficiency']) / 1000

                    detection = DetectionResult(
                        bbox=(int(x1), int(y1), int(x2), int(y2)),
                        confidence=confidence,
                        area_sqm=area_sqm,
                        estimated_power_kw=power_kw,
                        panel_type=panel_type,
                        efficiency_score=self._estimate_efficiency(box, area_sqm)
                    )
                    detections.append(detection)

        return detections

    def _pixels_to_sqm(self, pixel_area: float, img_width: int, img_height: int) -> float:
        """Convert pixel area to square meters (simplified)."""
        # This would use actual GSD (Ground Sample Distance) in production
        # Example: assuming 0.3m per pixel resolution
        pixels_per_meter = 3.33  # 1 meter = 3.33 pixels at 0.3m GSD
        return pixel_area / (pixels_per_meter ** 2)

    def _classify_panel_type(self, area_sqm: float) -> str:
        """Classify panel type based on area."""
        if area_sqm < 2.0:
            return 'residential'
        elif area_sqm < 5.0:
            return 'commercial'
        else:
            return 'utility'

    def _estimate_efficiency(self, detection, area_sqm: float) -> float:
        """Estimate panel efficiency based on detection quality."""
        # Simplified efficiency estimation
        base_efficiency = 0.85

        # Adjust based on confidence
        confidence_factor = detection.conf[0].item()

        # Adjust based on shape regularity (panels should be rectangular)
        # In production, this would analyze the actual shape
        shape_factor = 0.95

        return base_efficiency * confidence_factor * shape_factor

    def _analyze_detections(self, detections: List[DetectionResult], image: np.ndarray) -> Dict:
        """Analyze detection results for insights."""
        if not detections:
            return {
                'total_area': 0,
                'estimated_power': 0,
                'coverage_percentage': 0,
                'distribution': {}
            }

        total_area = sum(d.area_sqm for d in detections)
        total_power = sum(d.estimated_power_kw for d in detections)

        # Calculate coverage
        image_area_pixels = image.shape[0] * image.shape[1]
        detected_area_pixels = sum((d.bbox[2] - d.bbox[0]) * (d.bbox[3] - d.bbox[1]) 
                                  for d in detections)
        coverage = (detected_area_pixels / image_area_pixels) * 100

        # Panel type distribution
        distribution = {}
        for d in detections:
            distribution[d.panel_type] = distribution.get(d.panel_type, 0) + 1

        return {
            'total_area': total_area,
            'estimated_power': total_power,
            'coverage_percentage': coverage,
            'distribution': distribution
        }

    def visualize_results(self, results: Dict, save_path: Optional[str] = None) -> np.ndarray:
        """Visualize detection results on the image."""
        image = cv2.imread(results['image_path'])

        # Define colors for different panel types
        colors = {
            'residential': (0, 255, 0),    # Green
            'commercial': (255, 255, 0),    # Yellow
            'utility': (0, 0, 255)          # Red
        }

        # Draw detections
        for detection in results['detections']:
            x1, y1, x2, y2 = detection.bbox
            color = colors.get(detection.panel_type, (255, 0, 255))

            # Draw bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

            # Add label
            label = f"{detection.panel_type}: {detection.confidence:.2f}"
            power_label = f"{detection.estimated_power_kw:.1f}kW"

            cv2.putText(image, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv2.putText(image, power_label, (x1, y1 - 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Add summary
        summary = f"Total Panels: {results['panel_count']} | "                  f"Total Power: {results['estimated_kwh']:.1f}kWh | "                  f"Coverage: {results['coverage_percentage']:.1f}%"

        cv2.putText(image, summary, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        if save_path:
            cv2.imwrite(save_path, image)
            logger.info(f"Saved visualization to {save_path}")

        return image

    def batch_process(self, input_dir: str, output_dir: str, 
                     save_visualizations: bool = True) -> List[Dict]:
        """Process multiple images in batch."""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        results = []
        image_extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}

        for image_file in input_path.iterdir():
            if image_file.suffix.lower() in image_extensions:
                logger.info(f"Processing {image_file.name}...")

                try:
                    result = self.detect(str(image_file))
                    results.append(result)

                    if save_visualizations:
                        viz_path = output_path / f"{image_file.stem}_detected.jpg"
                        self.visualize_results(result, str(viz_path))

                except Exception as e:
                    logger.error(f"Error processing {image_file.name}: {e}")

        # Save batch results
        with open(output_path / 'batch_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Processed {len(results)} images")
        return results


# Example usage
if __name__ == "__main__":
    # Initialize detector
    detector = SolarPanelDetector(model='yolov8')

    # Detect panels in a sample image
    results = detector.detect('examples/satellite_images/sample.jpg')

    # Print results
    print(f"Detected {results['panel_count']} solar panels")
    print(f"Total estimated power: {results['estimated_kwh']:.2f} kWh")
    print(f"Coverage: {results['coverage_percentage']:.2f}%")

    # Visualize
    detector.visualize_results(results, 'output/sample_detected.jpg')
