# Model, Data, and Policy

## Canonical event data

The worker converts source-specific payloads into a canonical authentication
event. The persisted event includes occurrence time, event type, outcome,
anonymized user and account references, session/device/host references, source
network prefix, authentication method, failure reason, and coarse location
fields.

The event also records hash-key and payload-schema versions. These fields make
the anonymization and contract assumptions explicit for auditing and
reprocessing.

## Privacy boundary

Sensitive identifiers are transformed in memory before the normal event
processing path writes to PostgreSQL. Persisted records use tenant-scoped
hashes and redacted payload metadata. Raw source payloads are not treated as
ordinary dashboard data.

This design preserves the relational signals needed for behavior analysis while
avoiding direct storage of user identifiers in the standard event model.

## Feature families

The scoring context contains two complementary feature families.

### User-level behavior

- Login frequency
- Average inter-event time
- Time since the last login

These features compare the event with the user's recent history.

### Global and system behavior

- Unique hosts
- Host entropy
- Top-host ratio
- Degree centrality approximation
- Cyclical hour-of-day encoding
- Cyclical day-of-week encoding

These features describe the event relative to the wider user-host activity
graph and its observed time pattern.

Training and online scoring use causal bounded historical windows. Training
events are processed chronologically, so a feature row can use prior activity
but not later validation or test activity. Raw hour and day values remain in
the evidence snapshot while sine and cosine encodings preserve their cyclical
relationship for model input. The resulting feature snapshot and
host-interaction snapshot are persisted so an analyst can inspect the evidence
used by the decision.

## Hybrid scoring

The implementation combines:

1. a global AutoEncoder reconstruction signal
2. a user-level Isolation Forest signal
3. normalized score fusion

The fused score is controlled by a tenant-level fusion balance and stored with
its component values, model version, and applied thresholds. The current
configuration uses a balanced starting value of alpha = 0.5.

Thresholds are represented as configurable tenant settings. The baseline-v2
validation profile supplies the demonstration defaults: caution =
0.4209913948058925 (validation p95) and lockout = 0.5315366108386527
(validation p99). These values are not presented as production-calibrated
constants.

## Risk policy

The policy layer maps the fused score to three bands:

| Band | Operational meaning | Typical response |
| --- | --- | --- |
| Safe | Activity remains within the current baseline | Allow and record |
| Caution | Activity needs review or additional verification | Step-up verification or alert |
| Lockout | Activity exceeds the blocking threshold | End session or lock account |

The final action is stored separately from the recommended action. This makes
behavior in Simulation and Notify only modes auditable, even when no provider
action is executed.

## Explainability

The dashboard presents a plain-language conclusion, overall risk, signal
components, activity summary, decision, and response history. Internal feature
names, model metadata, hashes, and identifiers remain available as technical
detail rather than being the primary analyst language.

Observed activity is kept separate from interpretation. The platform reports
that behavior differs from a baseline; it does not infer intent from the score.
