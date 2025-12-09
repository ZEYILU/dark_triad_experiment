# Annotation Analysis Configuration (config/)

This directory contains configuration for the inter-annotator agreement validation study.

## Files

### `annotation_analysis.yaml`
Settings for multi-annotator analysis:
- Paths to annotator files
- Fleiss' Kappa interpretation thresholds
- Visualization parameters (colors, DPI, figure sizes)
- Output directory settings

Used by: `scripts/analysis/multi_annotator_analysis.py`

## Usage
```python
from src.config import AnnotationAnalysisConfig

config = AnnotationAnalysisConfig()
categories = config.get_categories()
output_dir = config.get_path('output_dir')
```