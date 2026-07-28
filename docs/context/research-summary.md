# Research Summary

## Source

- [research-paper.pdf](../reference/research-paper.pdf)

## Research Objective

The paper proposes a hybrid unsupervised User Behavior Analytics framework for continuous authentication and anomaly detection. The goal is to identify suspicious behavior without relying on labeled attack data.

## Core Model Architecture

The architecture has two parallel components:

1. Global anomaly modeling with an undercomplete AutoEncoder
2. User-level anomaly modeling with an Isolation Forest

These two signals are fused into a final anomaly score.

## Global Feature Set

The paper uses the following global/system-oriented features for the AutoEncoder:

- `unique_hosts`
- `host_entropy`
- `top_host_ratio`
- `degree_centrality`
- `hour_of_day`
- `day_of_week`

These features represent how a user behaves relative to the wider system.

## User-Level Feature Set

The paper uses the following temporal and individualized features for the Isolation Forest:

- `login_frequency`
- `avg_inter_event_time`
- `time_since_last_login`

These features represent how a user behaves relative to their own historical baseline.

## Score Fusion

The paper defines a fused anomaly score:

`Ai = alpha * s'i + (1 - alpha) * ReconErrori`

Where:

- `ReconErrori` is the AutoEncoder reconstruction error
- `s'i` is the normalized user-level anomaly score
- `alpha` balances global and local contributions

The paper indicates that `alpha = 0.5` gave a balanced outcome in the reported experiments.

## Thresholds Reported in the Paper

The paper reports these operational thresholds for the fused anomaly score:

- caution threshold: `T95 = 0.349`
- lockout threshold: `T99 = 0.463`

These should be treated as research defaults, not automatically as production-ready constants.

## Data and Validation Context

The paper describes evaluation on a LANL authentication-style dataset and positions the work as an unsupervised detection problem over historical behavior data.

Important implication:

- the model depends on feature history
- the platform must compute those features from stored events
- a single-event scoring API without history is not sufficient

## Operational Meaning

The paper supports a tiered decision model:

- low-risk behavior remains allowed
- caution-band behavior can trigger step-up checks
- high-risk behavior can trigger session termination or lockout

## Platform Implications

The platform must support:

- event persistence
- sliding-window feature computation
- score persistence
- threshold configuration
- analyst review and explainability

## Known Implementation Challenges

### Real-time feature parity

Some features are easy to compute online, but others are more expensive:

- `degree_centrality` is the hardest operational feature in the paper
- graph-derived metrics may need approximation or scheduled refresh

### Threshold transferability

The thresholds in the paper are tied to the paper's preprocessing and evaluation flow. They must be revalidated against the implemented platform pipeline.

### Model reproducibility

The training pipeline should be script-based and versioned so that the model can be retrained or audited later.

## Recommended Interpretation

Treat the paper as:

- canonical for the model concept
- canonical for the feature families
- informative for threshold starting points
- not canonical for exact production deployment choices
