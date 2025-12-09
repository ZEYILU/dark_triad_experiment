# 🚀 Quick Start Guide - Multi-Annotator Analysis

## 📋 Prerequisites

- Python 3.8+
- Your annotation files (following the naming pattern)

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Check Your Files

Ensure your files follow this naming pattern:
```
annotator1_llm_validation_samples_stratified_YYYYMMDD_HHMMSS.csv
annotator2_llm_validation_samples_stratified_YYYYMMDD_HHMMSS.csv
annotator3_llm_validation_samples_stratified_YYYYMMDD_HHMMSS.csv
llm_validation_samples_stratified_YYYYMMDD_HHMMSS_ground_truth.csv
```

If your files have different patterns, edit `config/annotation_analysis.yaml`:
```yaml
paths:
  annotator_pattern: "YOUR_PATTERN*.csv"
  ground_truth_pattern: "YOUR_GROUND_TRUTH_PATTERN*.csv"
```

### Step 3: Run the Analysis

**Option A: Jupyter Notebook (Recommended)**

```bash
# Start Jupyter
jupyter notebook

# Open the notebook
# Navigate to: notebooks/02_annotation_validation.ipynb

# Run all cells
# Shift + Enter to run each cell
```

**Option B: Python Script**

Create `run_analysis.py`:
```python
from pathlib import Path
from src.config import AnnotationAnalysisConfig
from src.data.annotation_loader import AnnotationDataLoader
from src.analysis.agreement_metrics import AgreementAnalyzer
from src.reports.agreement_report import AgreementReportGenerator

# 1. Load configuration
config = AnnotationAnalysisConfig()

# 2. Load data
loader = AnnotationDataLoader(base_dir=Path('.'))
dataset = loader.load_all(
    gt_pattern=config.get_pattern('ground_truth_pattern'),
    annotator_pattern=config.get_pattern('annotator_pattern')
)

print(f"Loaded {dataset.n_samples} samples from {dataset.n_annotators} annotators")

# 3. Calculate agreement
analyzer = AgreementAnalyzer(categories=config.get_categories())
annotator_cols = [f'{name}_Classification' for name in dataset.annotator_names]
llm_col = loader.get_llm_column_name(dataset.merged)

inter_results = analyzer.analyze_inter_annotator_agreement(
    df=dataset.merged,
    annotator_cols=annotator_cols,
    interpret_fn=config.interpret_kappa
)

vs_llm_results = analyzer.analyze_all_vs_llm(
    df=dataset.merged,
    annotator_cols=annotator_cols,
    llm_col=llm_col
)

# 4. Generate reports
report_gen = AgreementReportGenerator(config=config)
output_dir = config.ensure_output_dir()

report_gen.generate_full_report(
    inter_results=inter_results,
    vs_llm_results=vs_llm_results,
    dataset=dataset,
    annotator_cols=annotator_cols,
    llm_col=llm_col,
    output_dir=output_dir
)

print(f"\n✅ Analysis complete! Results saved to: {output_dir}")
```

Run it:
```bash
python run_analysis.py
```

## 📊 Check Your Results

After running, check `results/multi_annotator_analysis/`:

```
results/multi_annotator_analysis/
├── inter_annotator_agreement_report.txt    # Main report
├── pairwise_agreement.csv                  # Pairwise Cohen's Kappa
├── annotator_vs_llm_agreement.csv          # Accuracy metrics
├── per_category_agreement.csv              # Per-category breakdown
├── per_category_agreement.png              # Visualization
├── confusion_matrix_Annotator1.png         # Confusion matrices
├── confusion_matrix_Annotator2.png
├── confusion_matrix_Annotator3.png
├── disagreements_detailed.csv              # Disagreement samples
└── merged_annotations.csv                  # Full dataset
```

## 🎯 What to Look For

### 1. Overall Agreement (Fleiss' Kappa)

Open `inter_annotator_agreement_report.txt`:
```
Fleiss' Kappa: 0.723
Interpretation: Substantial agreement
```

**Interpretation Guide:**
- **< 0.20**: Slight agreement (⚠️ concerning)
- **0.20-0.40**: Fair agreement (⚠️ needs improvement)
- **0.40-0.60**: Moderate agreement (✓ acceptable)
- **0.60-0.80**: Substantial agreement (✅ good)
- **> 0.80**: Almost perfect agreement (🌟 excellent)

### 2. LLM Agreement

Check `annotator_vs_llm_agreement.csv`:
```csv
Annotator,Accuracy,Cohen_Kappa,N_Samples
Annotator1,0.8500,0.7823,100
Annotator2,0.8200,0.7456,100
Annotator3,0.8700,0.8123,100
```

**Target:** Kappa > 0.60 (substantial agreement)

### 3. Per-Category Performance

Open `per_category_agreement.png` or `per_category_agreement.csv`:

Look for:
- Categories with low agreement (< 60%) → Need clarification in annotation guidelines
- Categories with high agreement (> 80%) → Well-defined categories

### 4. Disagreements

Review `disagreements_detailed.csv` to:
- Identify systematic errors
- Find ambiguous cases
- Improve annotation guidelines

## 🔧 Common Issues & Solutions

### Issue 1: "No annotator files found"

**Cause:** File naming doesn't match the pattern

**Solution:**
1. Check your file names
2. Update `config/annotation_analysis.yaml`:
   ```yaml
   paths:
     annotator_pattern: "YOUR_ACTUAL_PATTERN*.csv"
   ```

### Issue 2: "No LLM classification column found"

**Cause:** Column name doesn't match expected names

**Solution:**
The system looks for:
- `LLM_Judge_Classification`
- `Response_Classification`

Rename your column or modify the code in `src/data/annotation_loader.py`:
```python
def get_llm_column_name(self, df: pd.DataFrame) -> str:
    possible_names = [
        'LLM_Judge_Classification',
        'Response_Classification',
        'YOUR_COLUMN_NAME'  # Add your column name
    ]
```

### Issue 3: Module not found errors

**Cause:** Python can't find the `src` module

**Solution:**
Ensure you're running from the project root directory:
```bash
cd /path/to/dark_triad_experiment
python run_analysis.py
```

Or in Jupyter notebook:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent))
```

## 📈 Interpreting Results for Your Paper

### What to Report

1. **Inter-Annotator Reliability**
   ```
   "Three independent annotators achieved substantial agreement
   (Fleiss' κ = 0.72), with 68% of samples receiving identical
   classifications from all annotators."
   ```

2. **LLM-as-Judge Validation**
   ```
   "The LLM judge demonstrated strong agreement with human annotators
   (mean Cohen's κ = 0.78, range: 0.75-0.81), with an average accuracy
   of 85% (SD = 2.5%)."
   ```

3. **Per-Category Analysis**
   ```
   "Agreement was highest for REFUSAL (92%) and lowest for MIXED (67%),
   suggesting the need for clearer guidelines for ambiguous cases."
   ```

### Recommended Figures

1. **Confusion Matrix** - Shows classification patterns
2. **Per-Category Agreement** - Highlights strengths/weaknesses
3. **Pairwise Kappa Heatmap** - Demonstrates inter-annotator consistency

All generated automatically in `results/multi_annotator_analysis/`!

## 🎓 Next Steps

### For Paper Writing
1. Copy figures to your paper directory
2. Cite the Fleiss' Kappa method (Fleiss, 1971)
3. Discuss both agreements and disagreements
4. Include sample disagreements in appendix

### For Further Analysis
1. Examine `disagreements_detailed.csv`
2. Run sensitivity analyses with different subsets
3. Calculate confidence intervals (bootstrap)
4. Analyze disagreement patterns

### For Code Improvement
1. Add unit tests (`tests/`)
2. Create custom visualizations
3. Extend metrics (Krippendorff's α, etc.)
4. Add statistical significance tests

## 📚 More Information

- **Detailed Guide**: `docs/ANNOTATION_ANALYSIS_GUIDE.md`
- **Refactoring Details**: `REFACTORING_SUMMARY.md`
- **Legacy Script**: `scripts/analyze_multi_annotators.py` (still works!)

## ✅ Checklist

Before running:
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Files in correct location (project root)
- [ ] File naming matches pattern
- [ ] Configuration checked (`config/annotation_analysis.yaml`)

After running:
- [ ] Check Fleiss' Kappa value
- [ ] Review confusion matrices
- [ ] Examine disagreements
- [ ] Generate paper figures
- [ ] Document findings

## 🆘 Need Help?

1. Check `docs/ANNOTATION_ANALYSIS_GUIDE.md` (comprehensive guide)
2. Review docstrings in the code
3. Examine the example notebook
4. Check the troubleshooting section above

---

## 🎉 You're Ready!

**Estimated Time:**
- Setup: 5 minutes
- Running analysis: 1-2 minutes
- Reviewing results: 10-15 minutes
- **Total: ~20 minutes** from zero to complete analysis!

Perfect for your ACL paper deadline! 🚀

---

**Good luck with your paper!** 📝✨
