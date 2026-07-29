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

The default config expects the source dataset at:

`training/artifacts/input/lanl-auth-dataset-1-00.csv`

Adjust `dataset_path` in the YAML if your dataset lives elsewhere.

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
