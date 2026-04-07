# 🎯 Unified Fruit Analysis Pipeline - Setup & Usage Guide

This guide will help you get started with the unified fruit analysis pipeline.

## 📦 What's Included

Your unified pipeline package includes:

| File | Purpose |
|------|---------|
| `unified_pipeline.py` | Core pipeline implementation |
| `backend_service.py` | Flask REST API backend |
| `cli.py` | Command-line interface |
| `UNIFIED_PIPELINE_DEMO.ipynb` | Jupyter notebook with examples |
| `config.json` | Configuration file |
| `requirements.txt` | Python dependencies |
| `UNIFIED_PIPELINE_README.md` | Detailed documentation |

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
cd model-find-it
pip install -r requirements.txt
```

### Step 2: Analyze an Image

```bash
python cli.py analyze path/to/fruit.jpg
```

Output:
```
📸 Analyzing: path/to/fruit.jpg
------------------------------------------------------------

📍 CLASSIFICATION
   Type: apple
   Confidence: 95.2%

🍎 FRESHNESS: ✅ FRESH
   Confidence: 92.1%

📏 DIMENSIONS
   Width: 85.50 px
   Height: 82.30 px
   Area: 6500.00 px²
```

### Step 3: Start the Backend API

```bash
python backend_service.py
```

Service starts at: `http://localhost:5000`

## 📚 Usage Methods

### Method 1: Python Module (Direct Integration)

```python
from unified_pipeline import UnifiedFruitAnalyzer

# Initialize
analyzer = UnifiedFruitAnalyzer()

# Analyze single image
result = analyzer.analyze("fruit.jpg")
print(result)

# Analyze multiple images
results = analyzer.analyze_batch("fruits_directory/")

# Save results
analyzer.save_results(results, "output.json")
```

### Method 2: Command-Line Interface

```bash
# Analyze single image
python cli.py analyze fruit.jpg -o result.json

# Analyze batch
python cli.py batch fruits_directory/ -o results.json

# Check service health
python cli.py health

# Start server
python cli.py server --port 8000
```

### Method 3: REST API Service

```bash
# Start server
python backend_service.py

# Analyze via curl
curl -X POST -F "file=@fruit.jpg" http://localhost:5000/analyze

# Check health
curl http://localhost:5000/health

# Get API docs
curl http://localhost:5000/api/docs
```

### Method 4: Jupyter Notebook

```bash
jupyter notebook UNIFIED_PIPELINE_DEMO.ipynb
```

## 📊 Output Format Reference

All analyses return a standardized JSON format:

```json
{
    "timestamp": "2024-01-15T10:30:00Z",
    "image_path": "fruit.jpg",
    "classification": {
        "fruit_type": "apple",
        "confidence": 0.952,
        "all_scores": {
            "apple": 0.952,
            "banana": 0.032,
            "orange": 0.016
        }
    },
    "freshness": {
        "status": "fresh",
        "confidence": 0.921
    },
    "physical_dimensions": {
        "width": 85.5,
        "height": 82.3,
        "area": 6500.0
    }
}
```

## 🔧 Common Tasks

### Task 1: Process Single Image

```python
from unified_pipeline import UnifiedFruitAnalyzer

analyzer = UnifiedFruitAnalyzer()
result = analyzer.analyze("apple.jpg")

print(f"Type: {result['classification']['fruit_type']}")
print(f"Fresh: {result['freshness']['status']}")
print(f"Size: {result['physical_dimensions']['width']:.0f}x{result['physical_dimensions']['height']:.0f}")
```

### Task 2: Batch Process with Export

```python
results = analyzer.analyze_batch("fruits_folder/")
analyzer.save_results(results, "fruit_data.json")

# Load for further processing
import json
with open("fruit_data.json") as f:
    data = json.load(f)
```

### Task 3: Real-time Camera Processing

```python
import cv2
from unified_pipeline import UnifiedFruitAnalyzer

analyzer = UnifiedFruitAnalyzer()
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    cv2.imwrite('temp.jpg', frame)
    
    result = analyzer.analyze('temp.jpg')
    text = f"{result['classification']['fruit_type']} - {result['freshness']['status']}"
    
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.imshow('Fruit Analysis', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Task 4: Web Integration

```python
import requests

# Upload and analyze
with open('fruit.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/analyze',
        files={'file': f}
    )
    result = response.json()
```

## 🐛 Troubleshooting

### Issue: "Model not found"

```bash
# Check file paths
ls -la fruit_classification/Fruit_Classification.pth
ls -la rottenvsfresh_classifier/rottenvsfresh_model.h5

# Update paths in code if needed
analyzer = UnifiedFruitAnalyzer(
    fruit_class_model_path="/full/path/to/model.pth",
    freshness_model_path="/full/path/to/model.h5"
)
```

### Issue: CUDA out of memory

```python
# Use CPU instead
analyzer = UnifiedFruitAnalyzer(device="cpu")
```

### Issue: Slow processing

```python
# Try GPU acceleration
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name())

# Use batch processing for multiple images
results = analyzer.analyze_batch("directory/")  # More efficient than loop
```

## 📝 Example Workflows

### Workflow A: Single Fruit Store Quality Check

```bash
# Check quality of one fruit
python cli.py analyze store_fruit.jpg -o quality_report.json

# Check result
python -c "import json; d=json.load(open('quality_report.json')); print(d['freshness']['status'])"
```

### Workflow B: Bulk Processing for Dataset

```python
from unified_pipeline import UnifiedFruitAnalyzer
import json

analyzer = UnifiedFruitAnalyzer()
results = analyzer.analyze_batch("inventory/")
analyzer.save_results(results, "inventory_analysis.json")

# Generate report
fresh_count = sum(1 for r in results if r['freshness']['status'] == 'fresh')
print(f"Fresh: {fresh_count}/{len(results)}")
```

### Workflow C: Production API Service

```bash
# Install for production
pip install gunicorn

# Run with auto-restart
gunicorn -w 4 -b 0.0.0.0:5000 --reload backend_service:app

# Or with systemd for Linux
sudo systemctl start fruit-analysis-api
```

## 🎓 API Documentation

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check service status |
| `/analyze` | POST | Analyze single image |
| `/analyze/batch` | POST | Batch analyze |
| `/api/models` | GET | Model information |
| `/api/docs` | GET | API documentation |

## 💡 Tips & Best Practices

1. **Image Quality**: Use clear, well-lit images for best results
2. **Batch Processing**: Use batch mode for multiple images (~10x faster)
3. **GPU Acceleration**: Enable CUDA for 3-5x speedup
4. **Error Handling**: Always check for error keys in responses
5. **Caching**: Cache model loads for repeated analyses

## 🔒 Production Deployment

### Using Docker (Optional)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend_service:app"]
```

### Using systemd (Linux)

```ini
[Unit]
Description=Fruit Analysis API
After=network.target

[Service]
Type=notify
User=service
WorkingDirectory=/path/to/model-find-it
ExecStart=/usr/bin/python3 backend_service.py

[Install]
WantedBy=multi-user.target
```

## 📞 Support & Documentation

- **Full README**: `UNIFIED_PIPELINE_README.md`
- **Demo Notebook**: `UNIFIED_PIPELINE_DEMO.ipynb`
- **API Docs**: `http://localhost:5000/api/docs` (when running)

## ✅ Verification Checklist

- [ ] Dependencies installed (`pip list | grep torch`)
- [ ] Models present (`ls fruit_classification/Fruit_Classification.pth`)
- [ ] CLI works (`python cli.py health`)
- [ ] API starts (`python backend_service.py`)
- [ ] Sample image analyzed successfully

---

**Ready to use!** Choose your preferred method above and start analyzing fruits. 🍎🍌🍊
