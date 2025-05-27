"""Evaluation metrics and visualization for solar panel detection"""
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
