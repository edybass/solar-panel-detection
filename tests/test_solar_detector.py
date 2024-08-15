"""
Tests for Solar Panel Detection System
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.solar_detector import SolarPanelDetector, DetectionResult
from src.analysis.geo_analyzer import GeoAnalyzer


class TestSolarDetector:
    """Test suite for solar panel detector."""

    @pytest.fixture
    def detector(self):
        """Create detector instance."""
        return SolarPanelDetector(model_name='yolov8')

    @pytest.fixture
    def sample_image(self):
        """Create sample test image."""
        # Create a synthetic image
        img = np.random.randint(0, 255, (1024, 1024, 3), dtype=np.uint8)
        return img

    def test_detector_initialization(self, detector):
        """Test detector initializes correctly."""
        assert detector is not None
        assert detector.model_name == 'yolov8'
        assert detector.device in ['cpu', 'cuda']

    def test_detection_result_structure(self):
        """Test DetectionResult dataclass."""
        result = DetectionResult(
            bbox=(100, 100, 200, 200),
            confidence=0.95,
            area_sqm=10.5,
            estimated_power_kw=3.2,
            panel_type='residential',
            efficiency_score=0.88
        )

        assert result.bbox == (100, 100, 200, 200)
        assert result.confidence == 0.95
        assert result.area_sqm == 10.5
        assert result.estimated_power_kw == 3.2
        assert result.panel_type == 'residential'
        assert result.efficiency_score == 0.88

    def test_pixels_to_sqm_conversion(self, detector):
        """Test pixel to square meter conversion."""
        pixel_area = 1000
        img_width = 1024
        img_height = 1024

        area_sqm = detector._pixels_to_sqm(pixel_area, img_width, img_height)

        assert isinstance(area_sqm, float)
        assert area_sqm > 0

    def test_panel_type_classification(self, detector):
        """Test panel type classification based on area."""
        assert detector._classify_panel_type(1.5) == 'residential'
        assert detector._classify_panel_type(3.0) == 'commercial'
        assert detector._classify_panel_type(10.0) == 'utility'

    def test_batch_processing(self, detector, tmp_path):
        """Test batch processing functionality."""
        # Create temporary test images
        for i in range(3):
            img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
            cv2.imwrite(str(tmp_path / f"test_{i}.jpg"), img)

        # Run batch processing
        results = detector.batch_process(
            str(tmp_path), 
            str(tmp_path / "output"),
            save_visualizations=False
        )

        assert isinstance(results, list)

    @pytest.mark.parametrize("model_name", ["yolov8", "efficientdet", "custom"])
    def test_different_models(self, model_name):
        """Test initialization with different models."""
        detector = SolarPanelDetector(model_name=model_name)
        assert detector.model_name == model_name


class TestGeoAnalyzer:
    """Test suite for geospatial analyzer."""

    @pytest.fixture
    def geo_analyzer(self):
        """Create geo analyzer instance."""
        return GeoAnalyzer()

    def test_geo_analyzer_initialization(self, geo_analyzer):
        """Test geo analyzer initializes correctly."""
        assert geo_analyzer is not None
        assert geo_analyzer.crs == 'EPSG:4326'

    def test_solar_potential_calculation(self, geo_analyzer):
        """Test solar potential calculation."""
        # Test tropical location
        result = geo_analyzer.calculate_solar_potential(
            latitude=10.0,
            panel_area_sqm=100,
            efficiency=0.20
        )

        assert 'daily_production_kwh' in result
        assert 'annual_production_kwh' in result
        assert 'co2_offset_kg_annual' in result
        assert result['daily_production_kwh'] > 0
        assert result['annual_production_kwh'] > result['daily_production_kwh']

    @pytest.mark.parametrize("latitude,expected_min", [
        (0, 100),    # Equator - high production
        (45, 50),    # Temperate - medium production
        (70, 20)     # Arctic - low production
    ])
    def test_solar_potential_by_latitude(self, geo_analyzer, latitude, expected_min):
        """Test solar potential varies by latitude."""
        result = geo_analyzer.calculate_solar_potential(
            latitude=latitude,
            panel_area_sqm=100,
            efficiency=0.20
        )

        assert result['daily_production_kwh'] > expected_min
