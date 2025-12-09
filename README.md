# Dark Triad LLM Experiment

A modular framework for analyzing how Large Language Models respond to Dark Triad behavioral patterns in various contexts.

> **Research Focus**: Investigating LLM alignment and safety by evaluating responses to manipulative, narcissistic, and psychopathic prompts across different severity levels.

[中文版本](README_zh.md) | [Quick Start](QUICK_START.md)

## Features

- **Comprehensive Dataset**: 192 prompts covering Dark Triad traits (Machiavellianism, Narcissism, Psychopathy)
- **Multiple LLM Support**: OpenAI (GPT-4, GPT-3.5) and Anthropic (Claude 3 family)
- **Automated Classification**: Rule-based and LLM-as-Judge classification systems
- **Rich Analysis**: Statistical analysis, visualizations, and inter-annotator agreement metrics
- **Modular Architecture**: Clean, extensible codebase with comprehensive documentation

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys
cp .env.example .env
# Edit .env with your OpenAI/Anthropic API keys

# 3. Run experiment
python scripts/run_experiment.py

# 4. Run LLM-as-Judge classification
python scripts/run_llm_judge.py

# 5. Analyze results
python scripts/analyze.py

# 6. Multi-annotator agreement (optional)
python scripts/analyze_multi_annotators.py
```

For detailed instructions, see [QUICK_START.md](QUICK_START.md)

## Project Structure

```
dark_triad_experiment/
├── src/                    # Core modules
│   ├── config.py          # Configuration management
│   ├── llm/               # LLM clients (OpenAI, Anthropic)
│   ├── analysis/          # Classification and metrics
│   ├── data/              # Data loading utilities
│   └── utils/             # Logger and helpers
│
├── scripts/               # Executable scripts
│   ├── run_experiment.py  # Main experiment runner
│   ├── run_llm_judge.py   # LLM-as-Judge classification
│   ├── analyze.py         # Result analysis
│   ├── analyze_multi_annotators.py  # Inter-annotator agreement
│   └── ...                # Other analysis scripts
│
├── config/                # Annotation analysis config
│   └── annotation_analysis.yaml
│
├── configs/               # Main experiment configs
│   ├── models.yaml        # LLM model configurations
│   └── keywords.yaml      # Classification keywords
│
├── data/                  # Datasets
│   ├── Dark_Triad_Dataset_Merged.csv  # Main dataset (192 prompts)
│   └── samples/           # Validation & annotation samples
│
├── docs/                  # Documentation
│   ├── QUICK_START.md     # Detailed usage guide
│   ├── INSTALLATION.md    # Setup instructions
│   ├── LLM_JUDGE_VALIDATION.md
│   └── MULTI_ANNOTATOR_GUIDE.md
│
├── notebooks/             # Jupyter notebooks for analysis
│   └── run_llm_judge_analysis.ipynb
│
├── tests/                 # Unit tests
├── examples/              # Usage examples
├── legacy/                # Legacy v1.0 scripts (archived)
└── figures/               # Generated visualizations
```

## Dataset

The dataset includes **192 prompts** based on the Dark Triad framework:

- **64 scenarios** × **3 severity levels** (LOW, MEDIUM, HIGH)
- **5 contexts**: Workplace, Friendship, Romantic Relationships, Society, Family
- **3 traits**: Machiavellianism, Narcissism, Psychopathy

Dataset location: `data/Dark_Triad_Dataset_Merged.csv`

## Response Classification

Responses are classified into four categories:

1. **REFUSAL**: Model refuses to engage with the prompt
2. **REINFORCING**: Model validates or encourages the problematic behavior
3. **CORRECTIVE**: Model provides ethical guidance or alternatives
4. **MIXED**: Response contains elements of multiple categories

Classification methods:
- **Rule-based**: Keyword matching (fast, interpretable)
- **LLM-as-Judge**: GPT-4 classification (accurate, context-aware)

## Analysis Features

### Automated Classification
- **Rule-based Classifier**: Fast keyword-based classification
- **LLM-as-Judge**: GPT-4 powered classification with confidence scores
- **Hybrid Approach**: Combining both methods for robust results

### Statistical Analysis
- **Distribution Analysis**: Response patterns across models and traits
- **Severity Correlation**: How severity level affects model behavior
- **Model Comparison**: Comparing safety alignment across different LLMs
- **Inter-Annotator Agreement**: Fleiss' Kappa, Cohen's Kappa for human validation
- **Confusion Matrices**: Classifier performance evaluation

### Visualizations
- Publication-ready figures (300 DPI)
- Distribution charts, bar plots, heatmaps
- Severity analysis and trait comparisons
- Multi-annotator agreement visualizations

## Supported Models

**OpenAI**:
- GPT-4
- GPT-3.5-Turbo

**Anthropic**:
- Claude 3.5 Sonnet
- Claude 3 Opus
- Claude 3 Haiku

Easily extensible to other LLM providers.

## Workflow

### Standard Workflow
```
1. Setup Environment     → Install dependencies and configure API keys (5 min)
2. Run Experiment        → Generate LLM responses (2-3 hours)
3. LLM Judge Analysis    → Classify responses using GPT-4 (30 min)
4. Human Validation      → Multi-annotator agreement (optional)
5. Analyze Results       → Statistical analysis (5 min)
6. Generate Figures      → Publication-ready visualizations (2 min)
```

### Quick Test
```bash
# Verify setup
python tests/test_refactoring.py

# Run a small test
python scripts/run_experiment.py --test-mode
```

## Experiment Modes

| Mode | Duration | Cost | Use Case |
|------|----------|------|----------|
| Test | 5 min | $0.10 | Environment verification |
| Quick | 30 min | $1-2 | Initial exploration |
| Standard | 2-3 hours | $15-20 | Presentation data |
| Full | 3-4 hours | $18-25 | Publication data |

## Output

After running experiments, you'll get:

- **Raw Results**: `results/results_MODEL_*.csv`
- **Analyzed Data**: `results/*_analyzed.csv`
- **Statistical Reports**: `results/analysis_report_*.json`
- **Visualizations**: `figures/fig1-4_*.png`

## Documentation

- **[Quick Start Guide](QUICK_START.md)**: Comprehensive usage instructions
- **[Installation Guide](docs/INSTALLATION.md)**: Environment setup
- **[Project Summary](docs/PROJECT_SUMMARY.md)**: Feature overview
- **[LLM Judge Validation](docs/LLM_JUDGE_VALIDATION.md)**: Classification methodology
- **[Multi-Annotator Guide](docs/MULTI_ANNOTATOR_GUIDE.md)**: Human validation process
- **[Visualization Guide](docs/VISUALIZATION_GUIDE.md)**: Generating publication figures

## Requirements

- Python 3.8+
- OpenAI API key (optional)
- Anthropic API key (optional)

Dependencies: see `requirements.txt`

## Configuration

Edit `configs/models.yaml` to configure:
- Model selection
- Temperature and parameters
- Token limits
- Cost tracking

Edit `configs/keywords.yaml` to customize:
- Classification keywords
- Category definitions
- Matching rules

## Development

```bash
# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Check configuration
python tests/test_refactoring.py
```

## Citation

If you use this framework in your research, please cite:

```bibtex
@inproceedings{dark-triad-llm-2025,
  title={Analyzing LLM Responses to Dark Triad Behavioral Patterns},
  author={[Your Name]},
  booktitle={Proceedings of ACL 2026},
  year={2026}
}
```

## License

This project is for academic research purposes.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Troubleshooting

**Environment Issues**: Run `python tests/test_refactoring.py` to verify setup

**API Errors**: Check your `.env` file for valid API keys

**Classification Issues**: Review `configs/keywords.yaml` settings

For more help, see [QUICK_START.md](QUICK_START.md)

## Status

- ✅ Core functionality complete
- ✅ LLM-as-Judge validated
- ✅ Multi-annotator agreement analysis
- ✅ Publication-ready visualizations
- ✅ Comprehensive documentation

**Version**: 2.0  
**Status**: Ready for research use  
**Target**: ACL 2026 Submission

---

**Contact**: zeyi.lu@study.thws.de
**Institution**: Technische Hochschule Würzburg-Schweinfurt
