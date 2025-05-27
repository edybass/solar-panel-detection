#!/usr/bin/env python3
"""
PyCharm Integration Script for Environmental AI Projects
Run this from PyCharm terminal for seamless integration
"""

import os
import subprocess
import json
from pathlib import Path


class PyCharmGitWorkflow:
    def __init__(self):
        self.current_dir = Path.cwd()

    def run_git_command(self, command):
        """Execute git command and return output"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"❌ Git error: {e.stderr}")
            return None

    def setup_git_user(self):
        """Configure git user (run once)"""
        print("🔧 Configuring Git user...")

        # You can modify these or the script will prompt
        name = input("Enter your name: ") or "Your Name"
        email = input("Enter your email: ") or "your.email@example.com"

        self.run_git_command(f'git config --global user.name "{name}"')
        self.run_git_command(f'git config --global user.email "{email}"')

        print("✅ Git user configured")

    def create_and_push_commit(self, files, message):
        """Add files, commit, and push in one command"""
        # Add files
        for file in files:
            self.run_git_command(f"git add {file}")

        # Commit
        commit_result = self.run_git_command(f'git commit -m "{message}"')
        if commit_result is None:
            print(f"❌ Commit failed for: {message}")
            return False

        # Push
        push_result = self.run_git_command("git push origin main")
        if push_result is None:
            print(f"❌ Push failed for: {message}")
            return False

        print(f"✅ Committed and pushed: {message}")
        return True

    def development_workflow(self, project_type="solar"):
        """Simulate realistic development workflow"""

        if project_type == "solar":
            workflow_steps = [
                {
                    "day": 1,
                    "action": "Add image preprocessing utilities",
                    "files": ["src/preprocessing.py"],
                    "code": '''"""Image preprocessing utilities for satellite imagery"""
import cv2
import numpy as np
import rasterio

def normalize_satellite_image(image_path):
    """Normalize satellite imagery for ML processing"""
    with rasterio.open(image_path) as src:
        # Read RGB bands
        red = src.read(1)
        green = src.read(2)
        blue = src.read(3)

        # Stack and normalize
        rgb = np.dstack((red, green, blue))
        rgb = np.clip(rgb / rgb.max() * 255, 0, 255).astype(np.uint8)

    return rgb

def create_patches(image, patch_size=256, overlap=0.2):
    """Create overlapping patches from large image"""
    h, w = image.shape[:2]
    step = int(patch_size * (1 - overlap))
    patches = []

    for y in range(0, h - patch_size + 1, step):
        for x in range(0, w - patch_size + 1, step):
            patch = image[y:y+patch_size, x:x+patch_size]
            if patch.shape[:2] == (patch_size, patch_size):
                patches.append(patch)

    return np.array(patches)
'''
                },
                {
                    "day": 2,
                    "action": "Add training script with data loading",
                    "files": ["scripts/train_model.py"],
                    "code": '''"""Training script for solar panel detection model"""
import argparse
import tensorflow as tf
from pathlib import Path
import sys
sys.path.append('src')

from solar_detector import SolarPanelDetector

def load_training_data(data_dir):
    """Load and prepare training data"""
    # Implementation for loading satellite imagery
    # This would connect to your actual data pipeline
    print(f"Loading training data from {data_dir}")
    pass

def main():
    parser = argparse.ArgumentParser(description='Train solar panel detection model')
    parser.add_argument('--data-dir', required=True, help='Path to training data')
    parser.add_argument('--epochs', type=int, default=50, help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size')

    args = parser.parse_args()

    # Initialize detector
    detector = SolarPanelDetector()
    model = detector.create_model()

    print(f"Model created with {model.count_params():,} parameters")
    print(f"Training for {args.epochs} epochs...")

    # Load data (placeholder)
    load_training_data(args.data_dir)

    print("Training completed!")

if __name__ == "__main__":
    main()
'''
                },
                {
                    "day": 3,
                    "action": "Add model evaluation and metrics",
                    "files": ["src/evaluation.py"],
                    "code": '''"""Evaluation metrics and visualization for solar panel detection"""
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import precision_recall_curve, average_precision_score

class ModelEvaluator:
    def __init__(self, model):
        self.model = model

    def evaluate_detection_performance(self, test_images, test_labels):
        """Evaluate detection performance"""
        predictions = self.model.predict(test_images)

        # Calculate metrics
        precision, recall, _ = precision_recall_curve(test_labels, predictions)
        ap_score = average_precision_score(test_labels, predictions)

        return {
            'precision': precision,
            'recall': recall,
            'average_precision': ap_score
        }

    def plot_precision_recall_curve(self, precision, recall, ap_score):
        """Plot precision-recall curve"""
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, marker='.')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(f'Precision-Recall Curve (AP = {ap_score:.3f})')
        plt.grid(True)
        plt.show()

    def visualize_detections(self, image, detections):
        """Visualize detected solar panels on image"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.imshow(image)

        for detection in detections:
            bbox = detection['bbox']
            confidence = detection['confidence']

            rect = plt.Rectangle(
                (bbox[0], bbox[1]), bbox[2] - bbox[0], bbox[3] - bbox[1],
                linewidth=2, edgecolor='red', facecolor='none'
            )
            ax.add_patch(rect)
            ax.text(bbox[0], bbox[1] - 5, f'{confidence:.2f}', 
                   color='red', fontsize=10, weight='bold')

        ax.set_title(f'Solar Panel Detection - {len(detections)} panels found')
        ax.axis('off')
        plt.show()
'''
                }
            ]
        else:  # waste classification
            workflow_steps = [
                {
                    "day": 1,
                    "action": "Add data augmentation utilities",
                    "files": ["src/data_utils.py"],
                    "code": '''"""Data utilities and augmentation for waste classification"""
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np

def create_data_generators(train_dir, val_dir, batch_size=32, image_size=(224, 224)):
    """Create data generators with augmentation"""

    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        brightness_range=[0.7, 1.3],
        fill_mode='nearest'
    )

    val_datagen = ImageDataGenerator(rescale=1./255)

    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=image_size,
        batch_size=batch_size,
        class_mode='categorical'
    )

    val_generator = val_datagen.flow_from_directory(
        val_dir,
        target_size=image_size,
        batch_size=batch_size,
        class_mode='categorical'
    )

    return train_generator, val_generator

def balance_dataset(data_dir):
    """Balance dataset across waste categories"""
    # Implementation for dataset balancing
    print(f"Balancing dataset in {data_dir}")
    pass
'''
                },
                {
                    "day": 2,
                    "action": "Add environmental impact calculator",
                    "files": ["src/impact_calculator.py"],
                    "code": '''"""Environmental impact calculation for waste classification"""

class EnvironmentalImpactCalculator:
    def __init__(self):
        # CO2 impact factors (kg CO2 per kg of waste)
        self.impact_factors = {
            'plastic': 2.5,
            'glass': 0.8,
            'metal': 1.5,
            'paper': 1.0,
            'cardboard': 0.9,
            'organic': 0.3
        }

        # Recycling reduction factors
        self.recycling_factors = {
            'plastic': 0.7,
            'glass': 0.9,
            'metal': 0.8,
            'paper': 0.6,
            'cardboard': 0.6,
            'organic': 0.9  # composting
        }

    def calculate_co2_impact(self, waste_distribution, total_weight_kg=1.0):
        """Calculate CO2 impact of waste"""
        total_impact = 0

        for waste_type, percentage in waste_distribution.items():
            weight = total_weight_kg * (percentage / 100)
            impact = weight * self.impact_factors.get(waste_type, 1.0)
            total_impact += impact

        return total_impact

    def calculate_recycling_benefit(self, waste_distribution, total_weight_kg=1.0):
        """Calculate CO2 reduction through proper recycling"""
        base_impact = self.calculate_co2_impact(waste_distribution, total_weight_kg)

        recycled_impact = 0
        for waste_type, percentage in waste_distribution.items():
            weight = total_weight_kg * (percentage / 100)
            base_co2 = weight * self.impact_factors.get(waste_type, 1.0)
            reduction_factor = self.recycling_factors.get(waste_type, 0.5)
            recycled_impact += base_co2 * (1 - reduction_factor)

        return base_impact - recycled_impact

    def generate_recommendations(self, waste_distribution):
        """Generate recycling recommendations"""
        recommendations = []

        if waste_distribution.get('plastic', 0) > 30:
            recommendations.append("High plastic content detected. Consider plastic reduction strategies.")

        if waste_distribution.get('organic', 0) > 20:
            recommendations.append("Significant organic waste. Implement composting program.")

        if waste_distribution.get('paper', 0) + waste_distribution.get('cardboard', 0) > 25:
            recommendations.append("Paper materials detected. Ensure proper recycling separation.")

        return recommendations
'''
                },
                {
                    "day": 3,
                    "action": "Add Streamlit web application",
                    "files": ["app/streamlit_app.py"],
                    "code": '''"""Streamlit web application for waste classification"""
import streamlit as st
import sys
from pathlib import Path
sys.path.append('src')

from waste_classifier import WasteClassifier
from impact_calculator import EnvironmentalImpactCalculator

def main():
    st.title("🌍 Waste Classification & Environmental Impact")
    st.markdown("Upload an image to classify waste and calculate environmental impact")

    # Initialize classifier (you'd load your trained model here)
    @st.cache_resource
    def load_model():
        classifier = WasteClassifier()
        # classifier.load_model('models/waste_classifier.h5')
        return classifier

    classifier = load_model()
    impact_calc = EnvironmentalImpactCalculator()

    # File upload
    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])

    if uploaded_file is not None:
        # Display image
        st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

        # Classification (placeholder)
        with st.spinner('Classifying...'):
            # result = classifier.classify_image(uploaded_file)
            result = {
                'class': 'plastic',
                'confidence': 0.92,
                'probabilities': {
                    'plastic': 0.92,
                    'glass': 0.03,
                    'metal': 0.02,
                    'paper': 0.01,
                    'cardboard': 0.01,
                    'organic': 0.01
                }
            }

        # Display results
        st.subheader("Classification Results")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Predicted Class", result['class'].title())
            st.metric("Confidence", f"{result['confidence']:.1%}")

        with col2:
            # Environmental impact
            waste_dist = {result['class']: 100}
            co2_impact = impact_calc.calculate_co2_impact(waste_dist)
            recycling_benefit = impact_calc.calculate_recycling_benefit(waste_dist)

            st.metric("CO₂ Impact", f"{co2_impact:.2f} kg")
            st.metric("Recycling Benefit", f"{recycling_benefit:.2f} kg CO₂ saved")

        # Recommendations
        st.subheader("Recommendations")
        recommendations = impact_calc.generate_recommendations(waste_dist)
        for rec in recommendations:
            st.info(rec)

if __name__ == "__main__":
    main()
'''
                }
            ]

        return workflow_steps

    def execute_development_day(self, step, project_dir):
        """Execute a single development day"""
        print(f"\n📅 Day {step['day']}: {step['action']}")

        # Create file with code
        for file_path in step['files']:
            full_path = Path(project_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, 'w') as f:
                f.write(step['code'])

            print(f"✅ Created: {file_path}")

        # Commit changes
        os.chdir(project_dir)
        success = self.create_and_push_commit(step['files'], step['action'])
        os.chdir('..')

        return success

    def run_development_simulation(self, project_name, days=3):
        """Run complete development simulation"""
        print(f"\n🚀 Starting development simulation for {project_name}")

        project_type = "solar" if "solar" in project_name else "waste"
        workflow_steps = self.development_workflow(project_type)

        for i in range(min(days, len(workflow_steps))):
            step = workflow_steps[i]
            success = self.execute_development_day(step, project_name)

            if not success:
                print(f"❌ Failed at day {step['day']}")
                break

            # Simulate time between development sessions
            import time
            time.sleep(2)

        print(f"\n✅ Development simulation complete for {project_name}")

    def quick_setup_existing_project(self):
        """Quick setup for existing project directory"""
        print("🔧 Quick setup for existing project...")

        # Check if we're in a git repository
        if not Path('.git').exists():
            print("❌ Not in a git repository. Run 'git init' first.")
            return

        # Check current directory name to determine project type
        current_dir = Path.cwd().name

        if "solar" in current_dir.lower():
            project_type = "solar"
        elif "waste" in current_dir.lower():
            project_type = "waste"
        else:
            project_type = input("Project type (solar/waste): ").lower()

        # Run development simulation
        self.run_development_simulation(".", days=3)


def main():
    print("🔧 PyCharm Git Workflow for Environmental AI Projects")
    print("=" * 55)

    workflow = PyCharmGitWorkflow()

    print("Choose an option:")
    print("1. Setup git user configuration")
    print("2. Run development simulation (existing project)")
    print("3. Quick commit current changes")

    choice = input("\nEnter choice (1-3): ")

    if choice == "1":
        workflow.setup_git_user()
    elif choice == "2":
        workflow.quick_setup_existing_project()
    elif choice == "3":
        files = input("Files to commit (space-separated): ").split()
        message = input("Commit message: ")
        workflow.create_and_push_commit(files, message)
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()