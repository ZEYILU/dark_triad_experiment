# Multi-Annotator Agreement Analysis Guide

## Overview

This guide explains how to use the refactored annotation analysis system. The code has been modularized for better maintainability, reusability, and ease of use.

## 📁 Project Structure

```
dark_triad_experiment/
├── config/
│   └── annotation_analysis.yaml          # Configuration file
├── src/
│   ├── config.py                         # Configuration manager
│   ├── data/
│   │   └── annotation_loader.py          # Data loading utilities
│   ├── analysis/
│   │   └── agreement_metrics.py          # Agreement calculation
│   ├── visualization/
│   │   └── agreement_plots.py            # Plotting functions
│   └── reports/
│       └── agreement_report.py           # Report generation
├── notebooks/
│   └── 02_annotation_validation.ipynb    # Main analysis notebook
├── scripts/
│   └── analyze_multi_annotators.py       # Original script (legacy)
└── requirements.txt                      # Dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Your Analysis

Edit `config/annotation_analysis.yaml` to customize:
- File patterns for your data
- Output directory
- Visualization settings
- Categories and thresholds

Example configuration:
```yaml
paths:
  base_dir: "."
  annotator_pattern: "annotator*_llm_validation_samples_stratified_*.csv"
  ground_truth_pattern: "llm_validation_samples_stratified_*_ground_truth.csv"
  output_dir: "results/multi_annotator_analysis"

analysis:
  categories:
    - REFUSAL
    - REINFORCING
    - CORRECTIVE
    - MIXED
```

### 3. Run the Analysis

**Option A: Using Jupyter Notebook (Recommended)**

1. Start Jupyter:
   ```bash
   jupyter notebook
   ```

2. Open `notebooks/02_annotation_validation.ipynb`

3. Run cells sequentially to:
   - Load data
   - Calculate agreement metrics
   - Generate visualizations
   - Export reports

**Option B: Using Python Script**

Create a simple script:
```python
from pathlib import Path
from src.config import AnnotationAnalysisConfig
from src.data.annotation_loader import AnnotationDataLoader
from src.analysis.agreement_metrics import AgreementAnalyzer
from src.visualization.agreement_plots import AgreementVisualizer
from src.reports.agreement_report import AgreementReportGenerator

# Load configuration
config = AnnotationAnalysisConfig()

# Load data
loader = AnnotationDataLoader(base_dir=Path('.'))
dataset = loader.load_all(
    gt_pattern=config.get_pattern('ground_truth_pattern'),
    annotator_pattern=config.get_pattern('annotator_pattern')
)

# Analyze agreement
analyzer = AgreementAnalyzer(categories=config.get_categories())
inter_results = analyzer.analyze_inter_annotator_agreement(
    df=dataset.merged,
    annotator_cols=[f'{name}_Classification' for name in dataset.annotator_names],
    interpret_fn=config.interpret_kappa
)

# Generate reports
report_gen = AgreementReportGenerator(config=config)
output_dir = config.ensure_output_dir()
# ... (continue with report generation)
```

## 📊 Output Files

After running the analysis, you'll find:

```
results/multi_annotator_analysis/
├── inter_annotator_agreement_report.txt  # Text summary
├── pairwise_agreement.csv                # Pairwise Cohen's Kappa
├── annotator_vs_llm_agreement.csv        # Accuracy and Kappa
├── per_category_agreement.csv            # Agreement by category
├── per_category_agreement.png            # Visualization
├── disagreements_detailed.csv            # Disagreement samples
├── confusion_matrix_Annotator1.png       # Per-annotator confusion matrices
├── confusion_matrix_Annotator2.png
├── confusion_matrix_Annotator3.png
├── agreement_distribution.png            # Agreement pattern pie chart
└── merged_annotations.csv                # Complete dataset
```

## 🔧 Customization

### Modifying Configuration

Edit `config/annotation_analysis.yaml`:

```yaml
# Change categories
analysis:
  categories:
    - YOUR_CATEGORY_1
    - YOUR_CATEGORY_2

# Adjust visualization
visualization:
  dpi: 300
  figsize: [12, 8]
  colors:
    - "#2E86AB"
    - "#A23B72"
```

### Extending Functionality

#### Add New Metrics

1. Edit `src/analysis/agreement_metrics.py`
2. Add method to `AgreementAnalyzer` class:

```python
def calculate_custom_metric(self, df: pd.DataFrame, cols: List[str]) -> float:
    # Your implementation
    pass
```

#### Add New Visualizations

1. Edit `src/visualization/agreement_plots.py`
2. Add method to `AgreementVisualizer` class:

```python
def plot_custom_chart(self, data: Dict, output_path: Path):
    # Your implementation
    pass
```

## 📝 Key Features

### 1. Configuration Management
- Centralized settings in YAML
- Easy to modify without code changes
- Version-controllable configuration

### 2. Modular Design
- Each component has a single responsibility
- Easy to test and debug
- Reusable across projects

### 3. Comprehensive Metrics
- Fleiss' Kappa (multi-annotator)
- Cohen's Kappa (pairwise)
- Per-category agreement
- Confusion matrices
- Agreement statistics

### 4. Rich Visualizations
- Confusion matrix heatmaps
- Per-category bar charts
- Agreement distribution
- Pairwise Kappa heatmaps

### 5. Detailed Reporting
- Text reports
- CSV exports
- Disagreement analysis

## 🔍 Understanding the Output

### Fleiss' Kappa Interpretation

| Kappa Value | Interpretation |
|-------------|----------------|
| < 0.00      | Poor agreement (worse than random) |
| 0.00-0.20   | Slight agreement |
| 0.21-0.40   | Fair agreement |
| 0.41-0.60   | Moderate agreement |
| 0.61-0.80   | Substantial agreement |
| 0.81-1.00   | Almost perfect agreement |

### Cohen's Kappa

Same interpretation as Fleiss' Kappa, but for pairwise comparisons.

### Accuracy vs Kappa

- **Accuracy**: Simple agreement rate (can be misleading with imbalanced data)
- **Kappa**: Agreement adjusted for chance (more robust)

## 🐛 Troubleshooting

### Issue: "No annotator files found"

**Solution**: Check your file naming pattern in `config/annotation_analysis.yaml`:
```yaml
paths:
  annotator_pattern: "annotator*_llm_validation_samples_stratified_*.csv"
```

Ensure your files match this pattern.

### Issue: "No LLM classification column found"

**Solution**: The system looks for:
- `LLM_Judge_Classification`
- `Response_Classification`

Rename your column to match one of these.

### Issue: Module import errors

**Solution**:
1. Ensure you're in the project root directory
2. Install all dependencies: `pip install -r requirements.txt`
3. In Jupyter, add project root to path:
   ```python
   import sys
   sys.path.insert(0, str(Path.cwd().parent))
   ```

## 📚 For ACL Paper

### Essential Results to Report

1. **Inter-Annotator Reliability**
   - Fleiss' Kappa value
   - Interpretation
   - Agreement percentage

2. **LLM-as-Judge Validation**
   - Average accuracy across annotators
   - Average Cohen's Kappa
   - Per-annotator agreement

3. **Per-Category Performance**
   - Best and worst performing categories
   - Category-specific Kappa values

### Recommended Figures

1. **Confusion Matrix** (one per annotator)
   - Shows classification patterns
   - Highlights common errors

2. **Per-Category Agreement Chart**
   - Bar chart comparing categories
   - Easy to see problematic categories

3. **Pairwise Kappa Heatmap**
   - Shows inter-annotator consistency
   - Identifies outlier annotators

### Writing Tips

- Report Fleiss' Kappa with confidence intervals (if sample size permits)
- Discuss both strengths and limitations
- Compare your Kappa values to similar studies
- Acknowledge disagreement patterns

## 🔄 Migration from Old Script

### Before (Old Script)

```bash
python scripts/analyze_multi_annotators.py
```

### After (New System)

**Interactive Analysis:**
```bash
jupyter notebook notebooks/02_annotation_validation.ipynb
```

**Automated Analysis:**
```python
# Create a new script using the modules
from src.config import AnnotationAnalysisConfig
from src.data.annotation_loader import AnnotationDataLoader
# ... use the modules
```

### Key Differences

1. **Configuration**: Now in YAML file instead of hardcoded
2. **Modularity**: Functions split into logical modules
3. **Reusability**: Can import and use in other scripts
4. **Testing**: Each module can be tested independently
5. **Documentation**: Better docstrings and type hints

## 📈 Best Practices

1. **Version Control Your Config**
   - Commit `config/annotation_analysis.yaml`
   - Document changes in git commits

2. **Keep Raw Data Separate**
   - Don't modify original annotation files
   - Use `merged_annotations.csv` for analysis

3. **Document Your Analysis**
   - Add markdown cells in Jupyter notebook
   - Explain unexpected results

4. **Save Intermediate Results**
   - Export key metrics as CSV
   - Easy to regenerate visualizations

5. **Review Disagreements**
   - Examine `disagreements_detailed.csv`
   - Identify systematic errors

## 🤝 Contributing

To extend the system:

1. Follow the existing code structure
2. Add docstrings to all functions
3. Use type hints
4. Write tests for new features
5. Update this guide

## 📧 Support

For questions or issues:
1. Check this guide first
2. Review the docstrings in the code
3. Examine the example notebook
4. Contact the development team

---

**Last Updated**: 2025-01-20
**Version**: 1.0
