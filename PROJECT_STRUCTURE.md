# Project Structure

This document describes the organized structure of the model-find-it project.

## Directory Organization

```
model-find-it/
├── core/                              # Main Python scripts and modules
│   ├── __init__.py                   # Package initialization
│   ├── __main__.py                   # CLI entry point for module execution
│   ├── cli.py                        # Command-line interface
│   ├── backend_service.py            # Flask backend service
│   └── unified_pipeline.py           # Main fruit analysis pipeline
│
├── fruit_classification/             # Fruit type classification models and data
│   ├── Fruit_Classification.pth      # Pre-trained MobileNetV2 model
│   ├── MobileNet_FruitClassificaiton.ipynb  # Model training notebook
│   ├── data_explore_clean.ipynb      # Data exploration and cleaning
│   ├── try_random_data.ipynb         # Model testing notebook
│   └── sample/                       # Sample test images
│
├── rottenvsfresh_classifier/         # Freshness detection (Rotten vs Fresh)
│   ├── rottenvsfresh_model.h5        # TensorFlow model for freshness detection
│   └── RottenvsFresh_Classifier.ipynb # Model training notebook
│
├── fruit_dimension/                  # Fruit dimension measurement
│   ├── fruit-dimension.ipynb         # Dimension measurement notebook
│   └── sample/                       # Sample test data
│
├── notebooks/                        # Jupyter notebooks for analysis and demo
│   └── UNIFIED_PIPELINE_DEMO.ipynb   # Complete pipeline demonstration
│
├── config/                           # Configuration and dependencies
│   ├── config.json                   # Configuration settings
│   └── requirements.txt              # Python package dependencies
│
├── docs/                             # Documentation files
│   ├── 00_START_HERE.md             # Quick start guide
│   ├── README.md                     # Main README
│   ├── SETUP_GUIDE.md               # Setup instructions
│   ├── ARCHITECTURE.md              # System architecture
│   ├── INDEX.md                      # Documentation index
│   ├── COMPLETE_PACKAGE_SUMMARY.md  # Full project summary
│   └── UNIFIED_PIPELINE_README.md   # Pipeline-specific documentation
│
└── .git/                            # Git repository

```

## How to Run

### Using the CLI

From the workspace root directory:

```bash
# Analyze a single image
python -m core.cli analyze "path/to/image.jpg"

# Analyze a batch of images
python -m core.cli batch "path/to/image/directory"

# Check service health
python -m core.cli health

# Start the backend service
python -m core.cli server
```

### Direct Python Execution

```bash
# From workspace root
cd core
python cli.py analyze "path/to/image.jpg"
```

### Backend Service

```bash
python -m core.backend_service
```

This starts a Flask server for REST API access.

## Key Modules

- **unified_pipeline.py**: Core analysis pipeline combining classification, freshness detection, and dimension measurement
- **cli.py**: Command-line interface for running analyses
- **backend_service.py**: Flask-based REST API backend

## Model Paths

The models are automatically located relative to the project structure:
- Fruit Classification: `fruit_classification/Fruit_Classification.pth`
- Freshness Detection: `rottenvsfresh_classifier/rottenvsfresh_model.h5`

## Recent Changes

### Fixed Issues
- ✅ Model loading error: Updated classifier structure to match saved model format
- ✅ Path resolution: Models now load correctly from any execution location

### Organization Improvements
- ✅ Moved core Python scripts to `core/` directory
- ✅ Moved documentation to `docs/` directory
- ✅ Moved configuration files to `config/` directory
- ✅ Moved notebooks to `notebooks/` directory
- ✅ Preserved all data model folders (`fruit_classification/`, `rottenvsfresh_classifier/`, `fruit_dimension/`)

