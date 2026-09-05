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

The default config expects the decompressed, headerless LANL source dataset at:

`training/artifacts/input/lanl-auth-dataset-1-00.txt`

The LANL source is already comma-delimited, so it does not need to be converted
to a `.csv` file. Pandas can also read the original `.bz2` file directly; point
`dataset_path` at that file instead if you do not want to decompress it.

Use `has_header: false` for the original LANL file, whose rows have the form
`time,user,computer` without a header row. For a processed CSV that already has
column names, set `has_header: true`. The configured `timestamp_column`,
`user_column`, and `host_column` names are assigned to headerless input and are
validated after loading.

`row_limit` is passed to the CSV reader so local training runs do not parse the
entire source file before selecting the configured sample.

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
