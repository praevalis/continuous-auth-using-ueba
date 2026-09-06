# Training Pipeline

Canonical training code lives under `training/src/training`. The notebook in
`training/notebooks/model_training.ipynb` is reference-only and is no longer the
intended execution path.

## Run from the repository root

```powershell
uv run --package continuous-auth-training train-model --config training/configs/default.yaml
```

For CPU-only local runs:

```powershell
uv run --package continuous-auth-training train-model --config training/configs/default.yaml --no-gpu
```

## Configuration

The pipeline is configured with YAML files under `training/configs`.

The default experiment expects the decompressed, headerless LANL source dataset
at:

`training/artifacts/input/lanl-auth-dataset-1-00.txt`

The LANL source is already comma-delimited, so it does not need to be converted
to a `.csv` file. Pandas can also read the original `.bz2` file directly; point
`dataset_path` at that file instead if you do not want to decompress it.

Use `has_header: false` for the original LANL files, whose rows have the form
`time,user,computer` without a header row. For a processed CSV that already has
column names, set `has_header: true`. The configured `timestamp_column`,
`user_column`, and `host_column` names are assigned to headerless input and are
validated after loading.

The `baseline-v2` configuration selects two million evenly distributed rows
from `00`. It uses the first 70% of that file's time range for training, the
next 15% for validation, and reserves the final 15% as an out-of-time test set.
Uniform sampling scans the source file in chunks without loading the complete
source into memory.

Feature preparation is chronological and uses only the configured bounded
history preceding each event. The validation and test partitions therefore do
not contribute future information to earlier feature rows. Validation-derived
normalization ranges and thresholds are reused for the test metrics.

Set `sampling_strategy: head` for a quick leading-row smoke test. In that mode,
`row_limit` and `test_row_limit` are passed directly to the CSV reader.

## Outputs

Each run writes to `training/artifacts/runs/<run_name>/`:

- `autoencoder.pth`
- `global_scaler.pkl`
- `user_scaler.pkl`
- `isolation_forest.pkl`
- `metrics.json`
- `config.snapshot.yaml`

## Pipeline coverage

The script reproduces the notebook's canonical stages:

- dataset loading
- feature engineering
- scaler fitting
- AutoEncoder training
- Isolation Forest training
- anomaly-score fusion
- threshold derivation
- chronological validation and out-of-time test evaluation
