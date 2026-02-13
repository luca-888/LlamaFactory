# Data Engineering Pipelines

This folder now has **split pipelines**:

- `build_behavior_dataset.py`: behavior-only label task.
- `build_tri_dataset.py`: tri-label task (dynamic + static + behavior).

## Prompt Version Control

Prompts are versioned by task:

- `prompts/behavior/v1.json`
- `prompts/behavior/v2.json` (default)
- `prompts/behavior/v3.json`
- `prompts/tri/v1.json` (default)

Each prompt file contains:

- `name`: stable version id
- `system`: instruction policy
- `user`: user message template

## Usage

Behavior-only (focus task):

```bash
python scripts/data_engineering/build_behavior_dataset.py \
  --input data/raw_data/train_17216_v2.json \
  --output data/processed_data/driving_behavioronly_train_17216_sft_v2.json \
  --report data/processed_data/driving_behavioronly_train_17216_sft_v2.report.json \
  --prompt-version v2
```

Tri-label:

```bash
python scripts/data_engineering/build_tri_dataset.py \
  --input data/raw_data/train_17216_v2.json \
  --output data/processed_data/driving_multilabel_train_17216_sft_v3.json \
  --report data/processed_data/driving_multilabel_train_17216_sft_v3.report.json \
  --prompt-version v1
```

List available prompt versions:

```bash
python scripts/data_engineering/build_behavior_dataset.py --list-prompt-versions
python scripts/data_engineering/build_tri_dataset.py --list-prompt-versions
```
