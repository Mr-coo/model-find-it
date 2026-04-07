# Unified Fruit Analysis Pipeline

A complete production-ready pipeline that combines **fruit classification**, **freshness detection**, and **dimension measurement** into a single unified model/service.

## 🎯 Overview

This unified pipeline processes fruit images and returns comprehensive analysis including:

| Feature | Model | Output |
|---------|-------|--------|
| **Fruit Classification** | MobileNetV2 (PyTorch) | Fruit type + confidence |
| **Freshness Detection** | Custom CNN (TensorFlow) | Fresh/Rotten status |
| **Dimension Measurement** | OpenCV (Image Processing) | Width, height, area |

### Input
```
Single fruit image (JPG, PNG)
```

### Output
```json
{
    "timestamp": "2024-01-15T10:30:00Z",
    "classification": {
        "fruit_type": "apple",
        "confidence": 0.95,
        "all_scores": {"apple": 0.95, "banana": 0.03, "orange": 0.02}
    },
    "freshness": {
        "status": "fresh",
        "confidence": 0.92
    },
    "physical_dimensions": {
        "width": 85.5,
        "height": 82.3,
        "area": 6500
    }
}
```

## 📦 Project Structure

```
model-find-it/
├── unified_pipeline.py          # Main unified analyzer class
├── backend_service.py            # Flask REST API service
├── UNIFIED_PIPELINE_DEMO.ipynb   # Demonstration notebook
├── UNIFIED_PIPELINE_README.md    # This file
│
├── fruit_classification/
│   ├── Fruit_Classification.pth  # PyTorch model (MobileNetV2)
│   ├── MobileNet_FruitClassificaiton.ipynb
│   └── data_explore_clean.ipynb
│
├── rottenvsfresh_classifier/
│   ├── rottenvsfresh_model.h5    # TensorFlow model
│   └── RottenvsFresh_Classifier.ipynb
│
├── fruit_dimension/
│   ├── fruit-dimension.ipynb
│   └── sample/                   # Test images
│
└── main/
    └── main.ipynb
```

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to project directory
cd model-find-it

# Install dependencies
pip install torch torchvision tensorflow opencv-python pillow numpy matplotlib flask flask-cors

# For GPU support (optional)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. Basic Usage - Python

```python
from unified_pipeline import UnifiedFruitAnalyzer

# Initialize
analyzer = UnifiedFruitAnalyzer(
    fruit_class_model_path="fruit_classification/Fruit_Classification.pth",
    freshness_model_path="rottenvsfresh_classifier/rottenvsfresh_model.h5"
)

# Analyze single image
result = analyzer.analyze("path/to/fruit.jpg", visualize=True)
print(result)

# Analyze multiple images
results = analyzer.analyze_batch("path/to/image/directory")

# Save results
analyzer.save_results(results, "output.json")
```

### 3. Backend Service - REST API

```bash
# Start Flask server
python backend_service.py
```

Server runs at `http://localhost:5000`

#### API Examples

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Analyze Single Image:**
```bash
curl -X POST -F "file=@fruit.jpg" http://localhost:5000/analyze
```

**Batch Analysis:**
```bash
curl -X POST -F "files=@fruit1.jpg" -F "files=@fruit2.jpg" http://localhost:5000/analyze/batch
```

**Get Documentation:**
```bash
curl http://localhost:5000/api/docs
```

### 4. Jupyter Notebook

```bash
jupyter notebook UNIFIED_PIPELINE_DEMO.ipynb
```

The notebook includes:
- Model initialization
- Single image analysis
- Batch processing
- Result visualization
- Statistics and metrics
- Backend service integration

## 🔧 API Reference

### UnifiedFruitAnalyzer Class

#### Methods

**`__init__(fruit_class_model_path, freshness_model_path, device="cuda")`**
- Initializes analyzer with model paths
- `device`: "cuda" for GPU or "cpu"

**`analyze(image_path, visualize=False)`**
- Analyzes single image
- Returns: Dictionary with complete analysis
- `visualize`: Display results on image

**`analyze_batch(image_dir, visualize=False)`**
- Analyzes all images in directory
- Returns: List of analysis results

**`save_results(results, output_path)`**
- Saves results to JSON file
- `output_path`: Path to output JSON file

**`get_analysis_json(result)`**
- Converts result to JSON string

### FruitAnalysisService Class (Backend)

**`__init__(model_dir=".")`**
- Initializes backend service

**`analyze_image(image_path_or_bytes)`**
- Analyzes image (file path or bytes)
- Returns: Analysis dictionary

**`get_health_status()`**
- Returns service health status

## 📊 API Endpoints

### Health Check
```
GET /health
Response: {status, fruit_classifier, freshness_detector, timestamp}
```

### Analyze Single Image
```
POST /analyze
Input: form-data with 'file' (multipart) or 'url'
Response: Complete analysis JSON
```

### Batch Analysis
```
POST /analyze/batch
Input: form-data with 'files' (multipart array)
Response: {total_images, results: [analysis1, analysis2, ...]}
```

### Model Information
```
GET /api/models
Response: Model details, capabilities, input sizes
```

### Documentation
```
GET /api/docs
Response: Full API documentation with examples
```

## 🎓 Example Workflows

### Workflow 1: Single Image Analysis

```python
from unified_pipeline import UnifiedFruitAnalyzer

analyzer = UnifiedFruitAnalyzer()
result = analyzer.analyze("apple.jpg")

print(f"Fruit: {result['classification']['fruit_type']}")
print(f"Status: {result['freshness']['status']}")
print(f"Size: {result['physical_dimensions']['width']:.0f}×{result['physical_dimensions']['height']:.0f}")
```

### Workflow 2: Batch Processing with Export

```python
# Analyze all images in directory
results = analyzer.analyze_batch("fruits_directory/")

# Export to JSON for data pipeline
analyzer.save_results(results, "analysis_output.json")

# Further processing
import json
with open("analysis_output.json") as f:
    data = json.load(f)
    
for item in data:
    print(f"{item['image_path']}: {item['classification']['fruit_type']}")
```

### Workflow 3: Backend Service Integration

```python
from backend_service import app

# Run Flask server
app.run(host='0.0.0.0', port=5000, debug=False)
```

Client:
```python
import requests

with open('fruit.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/analyze',
        files={'file': f}
    )
    result = response.json()
```

### Workflow 4: Real-time Camera Feed

```python
import cv2
from unified_pipeline import UnifiedFruitAnalyzer

analyzer = UnifiedFruitAnalyzer()
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    
    # Save frame temporarily
    cv2.imwrite('temp.jpg', frame)
    
    # Analyze
    result = analyzer.analyze('temp.jpg')
    
    # Display
    text = f"{result['classification']['fruit_type']} - {result['freshness']['status']}"
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow('Fruit Analysis', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## 📈 Performance Metrics

| Component | Model | Input Size | Output |
|-----------|-------|-----------|--------|
| Classification | MobileNetV2 | 224×224 | 3 classes |
| Freshness | Custom CNN | 224×224 | 2 classes |
| Dimension | OpenCV | Variable | Pixel measurements |

### Typical Processing Times
- Single image: ~100-500ms (CPU), ~50-200ms (GPU)
- Batch (10 images): ~1-5s (CPU), ~0.5-2s (GPU)

## 🐛 Troubleshooting

### Models Not Loading
```
⚠ Check model file paths
⚠ Verify file integrity: ls -lh model_path
⚠ Check dependencies: pip list | grep torch tensorflow
```

### CUDA/GPU Issues
```python
# Use CPU instead
analyzer = UnifiedFruitAnalyzer(device="cpu")

# List available devices
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name())
```

### Memory Issues
```python
# Process images one at a time instead of batch
# Reduce batch size in service calls
```

## 🔐 Deployment Notes

### Production Deployment
1. Use gunicorn instead of Flask development server:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 backend_service:app
   ```

2. Use environment variables:
   ```bash
   export MODEL_DIR=/path/to/models
   export DEVICE=cuda
   ```

3. Add input validation and rate limiting
4. Implement proper error logging
5. Use HTTPS in production

## 📝 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📧 Contact & Support

For issues or questions, please contact [your contact info]

---

## Key Features Summary

✅ **Unified Pipeline** - Single interface for all fruit analysis
✅ **High Accuracy** - Combined models for comprehensive analysis
✅ **Production Ready** - REST API with proper error handling
✅ **Scalable** - Batch processing and multi-threading support
✅ **Well Documented** - Complete API docs and examples
✅ **Easy Integration** - Both Python module and REST API
✅ **Flexible Deployment** - CLI, web service, or embedded
