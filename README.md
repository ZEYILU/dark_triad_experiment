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

## Key Features

- **Automated Classification**: Rule-based and LLM-as-Judge (GPT-4) classification systems
- **Statistical Analysis**: Distribution patterns, severity correlation, model comparison
- **Human Validation**: Multi-annotator agreement with Fleiss' Kappa
- **Publication-Ready Visualizations**: 300 DPI figures, charts, and heatmaps

## Supported Models

**OpenAI**:
- GPT-4
- GPT-3.5-Turbo

**Anthropic**:
- Claude 3.5 Sonnet
- Claude 3 Opus
- Claude 3 Haiku

Easily extensible to other LLM providers.

## Output

The pipeline generates:
- Raw experiment results (CSV)
- Classified responses with confidence scores
- Statistical analysis reports (JSON)
- Publication-ready visualizations (PNG, 300 DPI)

## Documentation

- **[Quick Start Guide](QUICK_START.md)**: Step-by-step usage instructions
- **[Installation Guide](docs/INSTALLATION.md)**: Environment setup
- **[Configuration Guide](docs/CONFIG_STRUCTURE.md)**: Understanding config/ and configs/ directories
- **[LLM Judge Validation](docs/LLM_JUDGE_VALIDATION.md)**: Classification methodology
- **[Multi-Annotator Guide](docs/MULTI_ANNOTATOR_GUIDE.md)**: Human validation process

## Requirements

- Python 3.8+
- OpenAI and/or Anthropic API keys

See [requirements.txt](requirements.txt) for dependencies.

## License

This project is for academic research purposes.

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
