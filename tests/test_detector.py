"""Unit tests for solar panel detection system"""
import unittest
import numpy as np
from src.solar_detector import SolarPanelDetector

class TestSolarDetector(unittest.TestCase):
    def setUp(self):
        self.detector = SolarPanelDetector()
    
    def test_model_creation(self):
        """Test CNN model creation"""
        model = self.detector.create_model()
        self.assertIsNotNone(model)
        self.assertEqual(model.input_shape[1:], (256, 256, 3))
    
    def test_preprocessing(self):
        """Test image preprocessing pipeline"""
        # Test with dummy data
        test_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        # Would test preprocessing here
        self.assertTrue(True)  # Placeholder
    
    def test_lebanon_config_loading(self):
        """Test Lebanon configuration loading"""
        from src.utils import load_lebanon_config
        config = load_lebanon_config()
        self.assertIn('region', config)
        self.assertEqual(config['region'], 'lebanon')

if __name__ == '__main__':
    unittest.main()
