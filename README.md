# Dark Triad LLM Experiment

A modular framework for analyzing how Large Language Models respond to Dark Triad behavioral patterns in various contexts.

> **Research Focus**: Investigating LLM alignment and safety by evaluating responses to manipulative, narcissistic, and psychopathic prompts across different severity levels.

[中文版本](README_zh.md) | [Quick Start](QUICK_START.md)

## Features

- **Comprehensive Dataset**: 126 prompts covering Dark Triad traits (Machiavellianism, Narcissism, Psychopathy)
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

# 4. Analyze results
python scripts/analyze.py
```

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
│   ├── analyze.py         # Result analysis
│   └── run_llm_judge.py   # LLM-as-Judge classification
│
├── config/                # Annotation analysis config
│   └── annotation_analysis.yaml
│
├── configs/               # Main experiment configs
│   ├── models.yaml        # LLM model configurations
│   └── keywords.yaml      # Classification keywords
│
├── data/                  # Datasets
│   └── samples/           # Validation samples
│
├── docs/                  # Documentation
│   ├── QUICK_START.md     # Detailed usage guide
│   ├── INSTALLATION.md    # Setup instructions
│   └── ...
│
├── notebooks/             # Jupyter notebooks for analysis
├── tests/                 # Unit tests
├── examples/              # Usage examples
└── figures/               # Generated visualizations
```

## Dataset

The dataset includes **126 prompts** based on the Dark Triad framework:

- **42 scenarios** × **3 severity levels** (LOW, MEDIUM, HIGH)
- **5 contexts**: Workplace, Friendship, Romantic Relationships, Society, Family
- **3 traits**: Machiavellianism, Narcissism, Psychopathy

Dataset location: `data/Dark_Triad_Dataset_FINAL.csv`

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

- **Distribution Analysis**: Response patterns across models and traits
- **Severity Correlation**: How severity level affects model behavior
- **Model Comparison**: Comparing safety alignment across different LLMs
- **Inter-Annotator Agreement**: Fleiss' Kappa for human validation
- **Visualizations**: Publication-ready figures (300 DPI)

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

```
Setup Environment → Run Experiment → Classify Responses → Analyze Results → Generate Figures
    (1 min)            (2-3 hours)        (30 min)           (5 min)          (2 min)
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
- **[Installation Guide](INSTALLATION.md)**: Environment setup
- **[Project Summary](docs/PROJECT_SUMMARY.md)**: Feature overview
- **[LLM Judge Validation](docs/LLM_JUDGE_VALIDATION.md)**: Classification methodology
- **[Multi-Annotator Guide](docs/MULTI_ANNOTATOR_GUIDE.md)**: Human validation process

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

**Contact**: [Your Email]  
**Institution**: [Your Institution]
