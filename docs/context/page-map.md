# Dashboard Page Map

## Purpose

This document defines the dashboard pages and the information each page is responsible for displaying. It keeps page boundaries aligned with the backend-supported workflows and the approved Continuous Auth dashboard language.

The dashboard should explain sign-in activity, risk, decisions, and response history in plain language. Internal model names, raw feature names, hashes, and enum values belong only in technical detail views.

## Navigation model

The primary navigation contains four pages:

1. Overview
2. Threat feed
3. Policies
4. Activity

Event detail is entered from the Threat feed and does not need to be a primary navigation item. Tenant administration and provider configuration are secondary administration views, available through the tenant or analyst context controls.

## Primary pages

### Overview

Suggested route: `/`

Status: implemented as the approved desktop and mobile concept.

Purpose:

- give an analyst a concise view of the current sign-in environment
- show what needs attention
- show the current response mode and recent system activity without requiring investigation first

Content:

- application context and data freshness
- platform status: Event intake, Analysis, and Responses
- risk landscape: Safe, Caution, and Lockout proportions
- recent activity trace using the most recent available data
- recent sign-in activity
- work to review, including caution decisions, lockout decisions, analysis still in progress, and responses skipped in Simulation
- main signal callout
- system activity timeline

The Overview must remain a summary. Detailed evidence and configuration do not belong here.

### Threat feed

Suggested route: `/threat-feed`

Purpose:

- provide the near-live operational stream of sign-in events
- let an analyst find events that require review
- keep identity, time, result, risk, score, and response information together

Content:

- event freshness and feed status
- filter and search controls for time, result, risk level, sign-in type, and response decision
- event rows containing:
  - occurred time
  - user label
  - sign-in type
  - result
  - risk level
  - overall risk score
  - response decision or “No action taken”
- pagination or incremental loading state
- selected-event state that opens the Event detail view

The feed should use a dense ledger on desktop and self-contained event entries on mobile. Mobile entries must not separate the user from the event data it describes.

### Policies

Suggested route: `/policies`

Purpose:

- show how the platform classifies risk and decides what to do
- allow authorized users to manage supported risk and response settings

Content:

- active risk settings profile
- Safe, Caution, and Lockout threshold values
- threshold instrument showing the normalized score range
- operating mode presented as:
  - Simulation
  - Notify only
  - Active response
- plain-language explanation of what each mode does
- response decision mapping for supported actions:
  - Ask for extra verification
  - End session
  - Lock account, only when configured
- profile status, scope, last updated time, and active/inactive state
- validation and confirmation before changing settings

The page must not expose `score_band`, `shadow`, `alert_only`, `enforce`, or internal action enum names as primary labels.

### Activity

Suggested route: `/activity`

Purpose:

- provide an audit-oriented view of analysis, alerts, decisions, and response activity
- help an analyst understand what the system recorded and what it actually carried out

Content:

- processing and analysis status
- policy decisions
- alerts and their delivery status
- response activity and enforcement history
- simulated, skipped, successful, failed, and pending outcomes
- event/user references, provider, requested time, completed time, and failure reason when available
- filters for time, activity type, status, and response mode

Simulation must clearly distinguish recorded decisions from actions carried out through a provider.

## Supporting views

### Event detail

Suggested route: `/threat-feed/:eventId`

Entry point: selected event in Threat feed.

Purpose:

- explain one sign-in event without hiding the surrounding feed context on desktop

Content:

- conclusion in plain language
- occurred time, user, sign-in type, result, and overall risk score
- risk level and threshold position
- environment signal and user activity signal
- signal balance only when useful to explain the result
- activity summary and baseline comparison
- response decision
- response activity or explicit “No action taken”
- analysis status and freshness
- expandable technical details for internal identifiers and model metadata

Observed activity must be separated from interpretation. The page must not claim intent or certainty that the backend does not establish.

## Administration views

These views are not part of the primary analyst navigation, but they are required for the tenant-facing administration workflow described by the platform scope.

### Tenant settings

Suggested route: `/settings/tenant`

Content:

- tenant identity and metadata
- tenant-specific operating mode settings
- active risk settings profile
- data freshness and connection status

### Event sources and credentials

Suggested route: `/settings/event-sources`

Content:

- configured event sources
- ingestion credential status
- source type and connection status
- last received event time
- credential creation, rotation, and retirement actions where supported

Raw credentials must never be displayed after creation.

### Provider connections

Suggested route: `/settings/providers`

Content:

- configured provider connections
- provider type and connection status
- supported response capabilities
- connection metadata status without exposing secrets

## Cross-page language rules

- Use “Sign-in event”, not “authentication event”, in primary UI copy.
- Use “User”, not `user_hash`.
- Use “Overall risk score”, not “fused anomaly score”.
- Use “Environment signal” and “User activity signal” when score components are shown.
- Use “Risk settings”, not “threshold profile”, unless managing named profiles.
- Use “Response decision”, not “policy decision”, in analyst-facing copy.
- Keep raw feature names, model names, hashes, internal IDs, and enum values inside expandable technical details.

## Out of scope for these pages

Do not add unsupported explanations or comparison factors such as travel possibility, geography-based intent, device reputation, or other signals that are not provided by the backend contract.
