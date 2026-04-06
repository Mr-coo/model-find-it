"""
Flask Backend Service for Unified Fruit Analysis Pipeline
Provides REST API endpoints for fruit analysis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from pathlib import Path
import tempfile
from unified_pipeline import FruitAnalysisService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize the analysis service
try:
    service = FruitAnalysisService(model_dir=".")
    logger.info("✓ Fruit Analysis Service initialized successfully")
except Exception as e:
    logger.error(f"✗ Failed to initialize service: {e}")
    service = None


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    Returns: Service status and model availability
    """
    if service is None:
        return jsonify({"status": "error", "message": "Service not initialized"}), 500
    
    return jsonify(service.get_health_status()), 200


@app.route('/analyze', methods=['POST'])
def analyze_image():
    """
    Analyze a single fruit image
    
    Expects:
        - file: Image file upload (multipart/form-data)
        - or: url to image file
    
    Returns:
        - JSON with classification, freshness, and dimensions
    """
    if service is None:
        return jsonify({"error": "Service not initialized"}), 500
    
    try:
        # Check if image was provided
        if 'file' not in request.files and 'url' not in request.form:
            return jsonify({"error": "No image file or URL provided"}), 400
        
        image_path = None
        
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                file.save(tmp_file.name)
                image_path = tmp_file.name
        
        elif 'url' in request.form:
            # Handle URL-based images (optional extension)
            import urllib.request
            url = request.form['url']
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                urllib.request.urlretrieve(url, tmp_file.name)
                image_path = tmp_file.name
        
        # Analyze the image
        result = service.analyze_image(image_path)
        
        # Clean up temporary file
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/analyze/batch', methods=['POST'])
def analyze_batch():
    """
    Analyze multiple images
    
    Expects:
        - files: Multiple image files (multipart/form-data)
    
    Returns:
        - JSON list with results for each image
    """
    if service is None:
        return jsonify({"error": "Service not initialized"}), 500
    
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist('files')
        results = []
        
        for file in files:
            if file.filename == '':
                continue
            
            # Save temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                file.save(tmp_file.name)
                
                # Analyze
                result = service.analyze_image(tmp_file.name)
                results.append({
                    "filename": file.filename,
                    "analysis": result
                })
                
                # Clean up
                os.remove(tmp_file.name)
        
        return jsonify({
            "total_images": len(results),
            "results": results
        }), 200
    
    except Exception as e:
        logger.error(f"Error analyzing batch: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/models', methods=['GET'])
def get_models_info():
    """
    Get information about loaded models
    
    Returns: Model information and capabilities
    """
    if service is None:
        return jsonify({"error": "Service not initialized"}), 500
    
    return jsonify({
        "models": {
            "fruit_classifier": {
                "name": "MobileNetV2",
                "task": "Fruit Classification",
                "classes": ["apple", "banana", "orange"],
                "input_size": 224
            },
            "freshness_detector": {
                "name": "Custom CNN",
                "task": "Fresh vs Rotten Detection",
                "classes": ["fresh", "rotten"],
                "input_size": 224
            },
            "dimension_measurer": {
                "name": "OpenCV",
                "task": "Dimension Measurement",
                "outputs": ["width", "height", "area"]
            }
        },
        "capabilities": [
            "fruit_type_classification",
            "freshness_detection",
            "dimension_measurement",
            "batch_processing"
        ]
    }), 200


@app.route('/api/docs', methods=['GET'])
def get_documentation():
    """
    Get API documentation
    """
    return jsonify({
        "title": "Unified Fruit Analysis API",
        "version": "1.0",
        "description": "Complete fruit analysis pipeline combining classification, freshness detection, and dimension measurement",
        "endpoints": {
            "GET /health": {
                "description": "Check service health status",
                "returns": "Service status and model availability"
            },
            "POST /analyze": {
                "description": "Analyze a single fruit image",
                "params": "file (multipart) or url (form)",
                "returns": "Fruit classification, freshness status, and dimensions"
            },
            "POST /analyze/batch": {
                "description": "Analyze multiple fruit images",
                "params": "files (multipart array)",
                "returns": "List of analysis results"
            },
            "GET /api/models": {
                "description": "Get information about loaded models",
                "returns": "Model details and capabilities"
            },
            "GET /api/docs": {
                "description": "Get API documentation",
                "returns": "This documentation"
            }
        },
        "example_response": {
            "timestamp": "2024-01-15T10:30:00.000Z",
            "image_path": "image.jpg",
            "image_dimensions": {"height": 480, "width": 640},
            "classification": {
                "fruit_type": "apple",
                "confidence": 0.95,
                "all_scores": {
                    "apple": 0.95,
                    "banana": 0.03,
                    "orange": 0.02
                }
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
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
