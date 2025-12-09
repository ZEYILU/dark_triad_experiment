# Main Experiment Configuration (configs/)

This directory contains configuration files for the main LLM response analysis experiments.

## Files

### `keywords.yaml`
Classification keywords for categorizing LLM responses:
- REFUSAL keywords: "I cannot", "I'm unable to", etc.
- CORRECTIVE keywords: "Consider", "Instead", "It's important", etc.
- REINFORCING keywords: "That's understandable", "It's normal", etc.
- MIXED keywords: Detection of contradictory signals

Used by: `src.analysis.classifier.ResponseClassifier`

### `models.yaml`
LLM model configurations:
- Model names (gpt-4, claude-3-opus, etc.)
- API parameters (temperature, max_tokens, etc.)
- Provider-specific settings

Used by: `src.llm.openai_client`, `src.llm.anthropic_client`

## Usage
```pythonfrom src.config import Configconfig = Config()
keywords = config.get_keywords("refusal")
models = config.get_models("openai")```