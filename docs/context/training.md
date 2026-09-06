# Training and Experimentation

## Ownership and entrypoint

The `training` package owns canonical model-input preparation, model training,
evaluation, and artifact generation. Scripted runs under
`training/src/training` are the source of truth; notebooks are exploratory and
must not become the only place where a reproducible step exists.

The supported command and configuration reference live in the
[training README](../../training/README.md). This document describes the design
constraints that make training results comparable and usable by the runtime.

## Source data

The default experiment uses the LANL authentication `00` source file. The
original data is headerless and comma-delimited, so the pipeline accepts it as
either decompressed `.txt` data or the original `.bz2` file. A conversion to
`.csv` is not required. Processed files with headers remain supported through
configuration.

Raw datasets are local inputs under `training/artifacts/input` and are not
versioned. A run records its effective configuration and dataset row counts so
the experiment can be reconstructed without committing the source dataset.

## Sampling and temporal partitions

The `baseline-v2` experiment selects two million rows distributed uniformly
across `00`. Uniform sampling scans the file in chunks so the full source does
not need to be loaded into memory and avoids limiting the experiment to only
the earliest activity.

Partitions are chronological rather than randomly shuffled:

- the first 70% of the observed time range is used for training
- the next 15% is used for validation
- the final 15% is reserved for out-of-time testing

An external test dataset may be configured instead, but it must begin after
the development dataset ends. Internal and external test strategies cannot be
enabled in the same run.

## Causal feature engineering

Feature rows are built in event-time order. Each row may use only events in the
configured bounded history preceding that event; later validation and test
activity cannot affect an earlier row. The current default history window is
30 days.

The global AutoEncoder receives host-interaction and cyclical time features:

- unique hosts
- host entropy
- top-host ratio
- degree centrality approximation
- hour-of-day sine and cosine
- day-of-week sine and cosine

The user-level Isolation Forest receives:

- login frequency
- average inter-event time
- time since the last login

Scalers are fitted only on the training partition. Validation and test data are
transformed with those fitted scalers.

## Hybrid model and evaluation

The AutoEncoder learns a reconstruction baseline for global behavior. The
Isolation Forest supplies a complementary user-level anomaly signal. Their
normalized scores are combined using the configured fusion alpha, which is
`0.5` for `baseline-v2`.

Normalization ranges and percentile thresholds are derived from validation
scores. The out-of-time test partition reuses those validation-derived values;
it does not refit scalers, normalization ranges, or thresholds. Test reporting
includes component-score summaries, fused-score summaries, and threshold
exceedance rates.

The LANL authentication input used here has no experiment-level anomaly labels.
Consequently, loss curves and percentile exceedance rates measure stability
and distribution shift, not detection precision, recall, or production
effectiveness. A model change should be compared with the existing baseline on
the same sample, split, seed, and evaluation procedure before any improvement
claim is made.

## Artifact contract

Each run is written to `training/artifacts/runs/<run_name>` and contains:

- `autoencoder.pth`
- `global_scaler.pkl`
- `user_scaler.pkl`
- `isolation_forest.pkl`
- `metrics.json`
- `artifact_metadata.json`
- `config.snapshot.yaml`

Metadata records the model and feature-engineering versions, AutoEncoder
dimensions, ordered feature lists, fusion alpha, normalization strategy and
ranges, derived thresholds, random seed, history window, sampling strategy,
and validation/test strategies. Runtime preparation selects inputs in the
metadata-declared order and reconstructs the declared model architecture,
preserving the training/serving contract across artifact versions.

Run names are immutable experiment identifiers. Do not overwrite an existing
run when changing data selection, feature engineering, architecture, or model
hyperparameters; create a new run name and retain the configuration snapshot
with its metrics.

The `baseline-v3` experiment kept the `baseline-v2` data, temporal split,
random seed, user-level model, and fusion settings fixed. It widened the
AutoEncoder from `8 -> 4 -> 2 -> 4 -> 8` to `8 -> 6 -> 3 -> 6 -> 8` and selected
the checkpoint with the lowest validation loss. It reduced reconstruction
loss, but raw min-max normalization allowed rare reconstruction errors to
compress the fused-score distribution.

The `baseline-v4` experiment kept the v3 model and training setup fixed while
testing robust score normalization. Component ranges use validation p1 and p99
instead of raw extrema, and normalized validation and test values are clipped
to `[0, 1]`. Its out-of-time p95 and p99 exceedance rates were 4.42% and 0.83%,
respectively, closer to the expected 5% and 1% validation rates than the prior
runs. It is the model currently selected by the worker's default artifact
configuration.

## Threshold promotion

Validation percentiles in artifact metadata are model outputs, while tenant
threshold profiles are explicit platform policy settings. Promoting a trained
threshold therefore requires a deliberate configuration change; loading a new
artifact must not silently alter tenant policy.

For `baseline-v4`, validation p95 (`0.5389387382637367`) is rounded to `0.539`
for the demonstration caution default, and validation p99
(`0.6630803731722841`) is rounded to `0.663` for the demonstration lockout
default. These values apply to new and seeded threshold profiles. Existing
tenant profiles remain unchanged unless they are explicitly replaced or
migrated. The defaults are research-derived demonstration settings, not
production-calibrated constants.
