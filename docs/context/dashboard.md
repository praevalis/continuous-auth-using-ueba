# Dashboard Surface

## Purpose

The dashboard is the analyst and tenant administration surface for the
platform. It consumes tenant-scoped API contracts and presents event
evidence, risk decisions, and response history as one operational workflow.

## Analyst views

### Overview

The overview summarizes pipeline health, risk distribution, recent activity,
work requiring review, and system activity. It is intentionally a summary
surface; detailed evidence belongs in the threat feed.

### Threat feed

The threat feed provides a paginated event ledger with time, user label,
sign-in type, result, risk level, overall score, and response outcome. Selecting
an event opens its evidence view.

### Event evidence

The event detail view keeps the sign-in, processing status, feature summary,
score components, policy decision, alerts, and enforcement history together.
Technical identifiers and model metadata are secondary detail.

### Policies

The policy view exposes active risk settings, threshold positions, response
mode, and supported response mappings. User-facing labels explain Simulation,
Notify only, and Active response without exposing internal enum names as the
primary interface.

### Activity

The activity view groups recorded analysis, decisions, alerts, and response
activity. It distinguishes simulated or skipped responses from actions sent to
an external provider and includes pending, failed, acknowledged, and resolved
states where available.

## Administration views

- Tenant settings: tenant identity, mode, risk settings, and freshness
- Event sources: source configuration and ingestion credential lifecycle
- Response providers: provider connection status and supported capabilities

Secrets are shown only at creation time and are not treated as ordinary
dashboard data.

## Presentation principles

- Use plain operational language before model terminology.
- Show risk with labels and text, not color alone.
- Keep observed activity separate from inferred interpretation.
- Preserve the relationship between an event and its evidence on mobile.
- Use generated API contracts rather than handwritten dashboard copies.
- Provide explicit loading, empty, error, validation, and mutation states.
- Keep the visual hierarchy calm and information-dense without turning every
  section into a card.

The dashboard is a review and operations surface, not a model-training
console. Model details are available when they support an investigation, but
they do not define the primary experience.
