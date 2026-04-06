"""
Unified Fruit Analysis Pipeline
Combines fruit classification, freshness detection, and dimension measurement
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
import tensorflow as tf
from PIL import Image
from pathlib import Path
from typing import Dict, Tuple, Optional
import json
from datetime import datetime


class UnifiedFruitAnalyzer:
    """
    Single pipeline that combines:
    1. Fruit Classification (using MobileNet)
    2. Freshness Detection (Rotten vs Fresh)
    3. Fruit Dimension Measurement (using OpenCV)
    """
    
    def __init__(
        self,
        fruit_class_model_path: str = "fruit_classification/Fruit_Classification.pth",
        freshness_model_path: str = "rottenvsfresh_classifier/rottenvsfresh_model.h5",
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        """
        Initialize the unified analyzer with all three models.
        
        Args:
            fruit_class_model_path: Path to the fruit classification model
            freshness_model_path: Path to the freshness detection model
            device: Device to run models on (cuda/cpu)
        """
        self.device = device
        self.fruit_class_model = None
        self.freshness_model = None
        self.class_names = ["apple", "banana", "orange"]  # Update based on your dataset
        
        # Image preprocessing settings
        self.img_size = 224
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(self.img_size),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        # Load models
        self._load_models(fruit_class_model_path, freshness_model_path)
    
    def _load_models(self, fruit_model_path: str, freshness_model_path: str):
        """Load both fruit classification and freshness detection models."""
        try:
            # Load fruit classification model
            if Path(fruit_model_path).exists():
                self.fruit_class_model = models.mobilenet_v2(weights='DEFAULT')
                self.fruit_class_model.classifier[1] = nn.Linear(
                    self.fruit_class_model.last_channel,
                    len(self.class_names)
                )
                self.fruit_class_model.load_state_dict(torch.load(fruit_model_path, map_location=self.device))
                self.fruit_class_model.to(self.device)
                self.fruit_class_model.eval()
                print(f"✓ Loaded fruit classification model from {fruit_model_path}")
            else:
                print(f"⚠ Fruit classification model not found at {fruit_model_path}")
        except Exception as e:
            print(f"✗ Error loading fruit classification model: {e}")
        
        try:
            # Load freshness detection model
            if Path(freshness_model_path).exists():
                self.freshness_model = tf.keras.models.load_model(freshness_model_path)
                print(f"✓ Loaded freshness detection model from {freshness_model_path}")
            else:
                print(f"⚠ Freshness detection model not found at {freshness_model_path}")
        except Exception as e:
            print(f"✗ Error loading freshness detection model: {e}")
    
    def _preprocess_for_opencv(self, image):
        """Preprocess image for OpenCV fruit dimension analysis."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        return blur
    
    def _segment_fruit(self, blur):
        """Segment the fruit from background using thresholding."""
        _, thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY_INV)
        return thresh
    
    def _get_largest_contour(self, thresh):
        """Extract the largest contour (fruit) from the binary image."""
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        if len(contours) == 0:
            return None
        
        # Filter contours by area
        contours = [c for c in contours if cv2.contourArea(c) > 1000]
        
        if len(contours) == 0:
            return None
        
        return max(contours, key=cv2.contourArea)
    
    def _measure_dimensions(self, image: np.ndarray) -> Optional[Dict]:
        """
        Measure fruit dimensions using OpenCV.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Dictionary with width and height measurements
        """
        try:
            blur = self._preprocess_for_opencv(image)
            thresh = self._segment_fruit(blur)
            contour = self._get_largest_contour(thresh)
            
            if contour is None:
                return {"width": None, "height": None, "area": None}
            
            # Get rotated bounding box
            rect = cv2.minAreaRect(contour)
            (cx, cy), (w, h), angle = rect
            
            # Ensure width > height
            if h > w:
                w, h = h, w
            
            # Calculate area
            area = float(cv2.contourArea(contour))
            
            return {
                "width": float(w),
                "height": float(h),
                "area": area,
                "angle": float(angle)
            }
        except Exception as e:
            print(f"Error measuring dimensions: {e}")
            return {"width": None, "height": None, "area": None, "angle": None}
    
    def _classify_fruit(self, image: np.ndarray) -> Optional[Dict]:
        """
        Classify the fruit type using MobileNet.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Dictionary with fruit type and confidence scores
        """
        if self.fruit_class_model is None:
            return None
        
        try:
            # Convert BGR to RGB and prepare image
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            # Apply transforms
            tensor_image = self.transform(pil_image).unsqueeze(0).to(self.device)
            
            # Get predictions
            with torch.no_grad():
                outputs = self.fruit_class_model(tensor_image)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
            
            # Create result dictionary
            result = {
                "fruit_type": self.class_names[predicted.item()],
                "confidence": float(confidence.item()),
                "all_scores": {}
            }
            
            # Add all class scores
            for idx, class_name in enumerate(self.class_names):
                result["all_scores"][class_name] = float(probabilities[0, idx].item())
            
            return result
        except Exception as e:
            print(f"Error classifying fruit: {e}")
            return None
    
    def _detect_freshness(self, image: np.ndarray) -> Optional[Dict]:
        """
        Detect if fruit is fresh or rotten using the freshness model.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Dictionary with freshness status and confidence
        """
        if self.freshness_model is None:
            return None
        
        try:
            # Prepare image for TensorFlow model (assuming 224x224 input)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            resized = cv2.resize(rgb_image, (224, 224))
            normalized = resized / 255.0
            
            # Add batch dimension
            input_data = np.expand_dims(normalized, axis=0)
            
            # Get prediction
            prediction = self.freshness_model.predict(input_data, verbose=0)
            
            # Assuming binary classification: [fresh, rotten] or similar
            if prediction.shape[1] == 2:
                is_fresh = prediction[0][0] > prediction[0][1]
                confidence = max(prediction[0])
                status = "fresh" if is_fresh else "rotten"
            else:
                # Single output
                is_fresh = prediction[0][0] > 0.5
                confidence = float(prediction[0][0])
                status = "fresh" if is_fresh else "rotten"
            
            return {
                "status": status,
                "confidence": float(confidence),
                "raw_prediction": prediction[0].tolist()
            }
        except Exception as e:
            print(f"Error detecting freshness: {e}")
            return None
    
    def analyze(self, image_path: str, visualize: bool = False) -> Dict:
        """
        Perform complete fruit analysis on a single image.
        
        Args:
            image_path: Path to the input image
            visualize: Whether to display visualization (default: False)
            
        Returns:
            Dictionary containing all analysis results
        """
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            return {"error": f"Could not load image from {image_path}"}
        
        # Get height and width for reference
        h, w = image.shape[:2]
        
        # Run all analyses
        classification = self._classify_fruit(image)
        freshness = self._detect_freshness(image)
        dimensions = self._measure_dimensions(image)
        
        # Compile results
        result = {
            "timestamp": datetime.now().isoformat(),
            "image_path": str(image_path),
            "image_dimensions": {"height": h, "width": w},
            "classification": classification,
            "freshness": freshness,
            "physical_dimensions": dimensions
        }
        
        if visualize:
            self._visualize_results(image, result)
        
        return result
    
    def analyze_batch(self, image_dir: str, visualize: bool = False) -> list:
        """
        Analyze multiple images in a directory.
        
        Args:
            image_dir: Path to directory containing images
            visualize: Whether to display visualizations
            
        Returns:
            List of analysis results
        """
        results = []
        image_dir = Path(image_dir)
        
        for image_path in image_dir.glob("*.jpg") + image_dir.glob("*.png"):
            result = self.analyze(str(image_path), visualize=visualize)
            results.append(result)
        
        return results
    
    def _visualize_results(self, image: np.ndarray, result: Dict):
        """Visualize the analysis results on the image."""
        vis = image.copy()
        
        # Add classification info
        if result.get("classification"):
            class_text = f"{result['classification']['fruit_type']} ({result['classification']['confidence']:.2f})"
            cv2.putText(vis, class_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Add freshness info
        if result.get("freshness"):
            fresh_text = f"Status: {result['freshness']['status']} ({result['freshness']['confidence']:.2f})"
            cv2.putText(vis, fresh_text, (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Add dimension info
        if result.get("physical_dimensions"):
            dims = result['physical_dimensions']
            if dims.get("width") and dims.get("height"):
                dim_text = f"Dimensions: {dims['width']:.1f} x {dims['height']:.1f}"
                cv2.putText(vis, dim_text, (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow("Unified Fruit Analysis", vis)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def get_analysis_json(self, result: Dict) -> str:
        """Convert analysis result to JSON string."""
        return json.dumps(result, indent=2)
    
    def save_results(self, results: list, output_path: str):
        """Save analysis results to a JSON file."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✓ Saved {len(results)} results to {output_path}")


# Backend Service Utility
class FruitAnalysisService:
    """
    Backend service wrapper for the unified fruit analyzer
    This class provides REST API ready methods for backend integration
    """
    
    def __init__(self, model_dir: str = "."):
        """Initialize the backend service."""
        self.analyzer = UnifiedFruitAnalyzer(
            fruit_class_model_path=f"{model_dir}/fruit_classification/Fruit_Classification.pth",
            freshness_model_path=f"{model_dir}/rottenvsfresh_classifier/rottenvsfresh_model.h5"
        )
    
    def analyze_image(self, image_path_or_bytes) -> Dict:
        """
        Analyze a single image (for backend use).
        Accepts either file path or image bytes.
        """
        if isinstance(image_path_or_bytes, bytes):
            # Convert bytes to numpy array
            import io
            nparr = np.frombuffer(image_path_or_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            image = cv2.imread(str(image_path_or_bytes))
        
        if image is None:
            return {"error": "Failed to load image"}
        
        return self.analyzer.analyze(image_path_or_bytes if isinstance(image_path_or_bytes, str) else "uploaded_image")
    
    def get_health_status(self) -> Dict:
        """Get service health status."""
        return {
            "status": "healthy",
            "fruit_classifier": self.analyzer.fruit_class_model is not None,
            "freshness_detector": self.analyzer.freshness_model is not None,
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Example usage
    analyzer = UnifiedFruitAnalyzer()
    
    # Analyze a single image
    result = analyzer.analyze("path/to/image.jpg", visualize=True)
    print(analyzer.get_analysis_json(result))
    
    # Analyze batch
    # results = analyzer.analyze_batch("path/to/image_directory")
    # analyzer.save_results(results, "analysis_results.json")
