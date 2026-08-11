# Dashboard Design System — Continuous Auth

## Purpose

This design system defines the visual language and interface organization for the continuous authentication dashboard. It is optimized for a security analyst reviewing a near-live threat feed, understanding why an event was scored as risky, checking policy decisions, and managing threshold profiles.

The dashboard should feel like a focused security workspace: calm, precise, editorial, and operational. It should make risk legible at a glance while preserving enough context for an analyst to trust and investigate a decision.

## Visual references

- [Home screen concept](./assets/desktop-mockup.png)
- [Mobile screen concept](./assets/mobile-mockup.png)

The existing mockups are useful for workflow coverage, but their dark-sidebar, pale-canvas, card-heavy composition is superseded by the design direction below. The final product name remains undecided.

## Product character

The design direction is inspired by archival ledgers, incident-room annotations, instrument panels, and muted English heritage colors.

The product should be:

- calm and low-noise when the system is healthy
- dense enough for operational scanning, with deliberate whitespace around decisions
- technical and precise without looking hostile or militaristic
- explicit about uncertainty, operating mode, and what action was or was not taken
- distinctive without becoming decorative

Avoid generic blue/green SaaS styling, neon cyber-security styling, gratuitous gradients, decorative charts, and color used as the only explanation of risk.

## Modern composition directive

Modern intent must be expressed through the structure and interaction model, not only through color, typography, or rounded corners. The dashboard must not look like a conventional admin template made from a sidebar, metric-card row, filter bar, and data table.

Use an analyst workbench built from:

- an asymmetric canvas with a clear primary focus and secondary evidence layer
- a continuous event stream or event rail instead of a spreadsheet-like table as the default feed
- event objects that combine identity, time, result, risk, and score in one readable unit
- inline evidence that unfolds beside or beneath the selected event
- score instruments, annotated thresholds, timeline markers, and signal traces instead of gauges and KPI cards
- a command surface for search, filtering, and navigation rather than many permanent controls
- strong typographic scale, whitespace, rule lines, and spatial grouping instead of boxed cards for every section

Desktop may use multiple simultaneous panes because the full event context can remain visible without scrolling. Mobile must preserve the same relationships through a single event thread: each event and its evidence remain one connected object, and detail expands in place.

The visual goal is a quiet instrument panel or evidence workspace, not a dashboard of widgets. Any new component should be rejected if it only repackages a standard card, table, KPI tile, or sidebar without improving analyst comprehension.

### Shell direction

Do not use a black navbar above a white sidebar or a white content area framed by dark application chrome. That contrast is a generic admin-layout pattern and is not part of the Continuous Auth visual language.

Use one continuous warm canvas with navigation integrated into the workspace:

- the page canvas uses parchment throughout, with no pure white content panels
- the primary navigation is a slim aubergine/plum command dock or floating vertical index, not a full white sidebar
- tenant, response mode, freshness, and analyst context live in a tonal context ribbon that belongs to the canvas rather than a black navbar
- navigation, context, and content use adjacent English-palette tones instead of black-to-white contrast
- use parchment, plum, terracotta, ochre, moss, and dusty lilac for hierarchy; reserve deep ink for text and small grounding details
- avoid pure black, pure white, bright blue, saturated green, and high-contrast chrome

The shell should feel like a considered editorial workspace with a continuous material surface, not a website frame wrapped around an application.

### Professional security application directive

The English color direction should create distinction through restrained color relationships, not through historical illustration or decorative styling. The interface must remain crisp, credible, and suitable for a security operations environment.

Do not use:

- engraved landscapes, castles, heraldry, botanical ornaments, or decorative illustrations
- paper grain, parchment texture, faux print effects, or ornamental flourishes
- large decorative serif treatments that compete with operational information
- irregular hand-drawn shapes or visual motifs that imply a lifestyle, editorial, or heritage brand

Use instead:

- flat cool-white and light-gray surfaces with subtle tonal layering
- clean 1px borders, precise alignment, and consistent component geometry
- restrained radii, approximately `8–12px` for surfaces and controls
- sans-serif-first typography with serif used only as a small accent, if needed
- compact line icons that communicate function rather than decorate the page
- English colors as restrained functional accents: graphite and Soft Carbon for structure and focus, ochre for caution, brick red for lockout, and moss for safe
- data visualizations that are simple, labeled, and operationally useful

The result should feel like a modern security product that happens to use a restrained English mineral palette—not an illustrated English heritage product.

### Color and composition principle

The interface should not be monochrome or neutral-only. Select one confident product color as the visual anchor, then use cool neutrals to create space, structure, and hierarchy around it. The primary color should appear consistently in active navigation, links, key chart emphasis, focused states, and recommended actions. It should not fill every surface or compete with semantic risk colors.

Use color in a deliberate hierarchy:

- primary product color for focus, navigation, links, and important recommendations
- cool white and light gray for the canvas, surfaces, separators, and inactive content
- soft tints of the primary color for emphasis bands or selected context
- ochre, brick, and moss only for their risk or operational meanings
- graphite for text and structural contrast

Use the primary color selectively within open neutral space. Favor direct chart emphasis, short narrative callouts, and action-led sections when they improve comprehension.

Do not make every section an equal card. Establish hierarchy with:

- large editorial metrics paired with a short interpretation
- open charts with direct labels and threshold/baseline annotations
- horizontal status bands and progress tracks
- inset callouts with a colored edge rule
- numbered or prioritized next-action rows
- borderless content groups separated by whitespace and fine rules
- inline links and actions placed beside the information they affect

Cards are appropriate for contained workflows or high-priority evidence, but they are not the default container for every section.

### Surface and boundary discipline

The interface should blend into a near-white workspace rather than being divided into a collection of outlined boxes. Use tonal layering and spacing first; use borders only when they communicate an actual boundary or interaction.

- keep the main canvas near white and let white surfaces sit only slightly above it
- use pale gray or a very light Soft Carbon tint for grouping, not medium-gray blocks
- do not outline every section, chart, list, or status area
- reserve borders for form controls, tables where row definition is necessary, selected states, and contained workflows
- prefer one shared section rule or a colored edge marker over four-sided panel borders
- use whitespace, alignment, typography, and selective background tint to establish hierarchy
- keep shadows rare and extremely soft; never use them to compensate for weak layout hierarchy

The application should read as one calm surface with a few purposeful zones, not as a set of cards placed on a gray board.

### Refinement constraints for the home screen

Refinement must preserve the established home-screen organization. Do not change the composition in pursuit of color balance.

- keep the existing home-screen sequence: context/navigation, greeting and summary, platform status, risk landscape and response mode, recent activity and review work, then system activity
- render the project title and primary interface accents in Soft Carbon; use it consistently for active navigation, focus, links, section rules, and recommendations
- place a compact product mark directly beside the `Continuous Auth` name in the top context area
- maintain clear breathing space between sections, between section headings and content, and between rows of data; whitespace is part of the hierarchy
- use one consistent shape system: `12px` for composed surfaces, `8px` for controls, and no sharp-cornered panel mixed with rounded panels without a deliberate reason
- keep data rows compact but not cramped, with a clear separation between primary values, labels, and secondary metadata
- use Soft Carbon consistently within the existing organization, with pale neutral grouping surfaces and semantic risk colors; do not rearrange the page into a new layout

## Language and translation directive

The dashboard is an operational interface, not a developer or model-inspection console. Backend and research terminology must not be exposed directly in the primary interface when a clear user-friendly phrase is available.

Use plain language that an analyst or administrator can understand without detailed knowledge of the scoring implementation. Explain what the system observed and what the platform decided; do not require users to understand model architecture, feature engineering, database names, or internal enum values.

Technical names may remain available in an expandable `Technical details` area, API responses, logs, or an advanced configuration view. They must not be the default labels, headings, actions, or primary explanation text.

### Required terminology mapping

| Internal concept            | Primary dashboard language | Usage guidance                                                       |
| --------------------------- | -------------------------- | -------------------------------------------------------------------- |
| authentication event        | Sign-in event              | Use in page headings and feed descriptions                           |
| `event_type`                | Sign-in type               | Show the friendly event value when known                             |
| `outcome`                   | Result                     | Values should read as Success, Failed, Challenge, or Signed out      |
| `user_hash`                 | User                       | Never expose the word “hash” in the primary UI                       |
| `device_hash` / `host_hash` | Device or host             | Use the most useful available label for the context                  |
| `source_ip_prefix`          | Network                    | Explain that the value is redacted only in secondary detail          |
| global anomaly score        | Environment signal         | Describe the broader activity signal, not the model name             |
| local anomaly score         | User activity signal       | Describe activity compared with the user’s observed history          |
| fused anomaly score         | Overall risk score         | This is the primary score shown to analysts                          |
| `fusion_alpha`              | Signal balance             | Hide by default; expose only in advanced score details               |
| `score_band`                | Risk level                 | Use Safe, Caution, or Lockout                                        |
| threshold profile           | Risk settings              | Use “profile” only when managing named configurations                |
| caution threshold           | Review threshold           | Explain that reaching it calls for review or additional verification |
| lockout threshold           | Block threshold            | Explain the resulting response plainly                               |
| operating mode              | Response mode              | Use Simulation, Notify only, or Active response                      |
| `shadow`                    | Simulation                 | Explain that responses are recorded but not carried out              |
| `alert_only`                | Notify only                | Explain that an alert is produced without enforcement                |
| `enforce`                   | Active response            | Explain that configured responses may be carried out                 |
| policy decision             | Response decision          | Use for the platform’s resulting action                              |
| `step_up_mfa`               | Ask for extra verification | Do not expose the internal action enum                               |
| `terminate_session`         | End session                | Use in action history and response summaries                         |
| `lock_account`              | Lock account               | Use only when this is the actual configured action                   |
| processing run              | Analysis status            | Use Queued, In progress, Completed, or Failed                        |
| feature snapshot            | Activity summary           | Use for the analyst-facing explanation of measured activity          |
| enforcement action          | Response activity          | Use for provider execution history                                   |

### Explanation rules

- Lead with a plain-language conclusion, for example “This sign-in has a high risk score” rather than “The fused anomaly score exceeded the lockout threshold.”
- Describe evidence as measured activity, not as intent or certainty. Use “The activity differs from this user’s recent pattern,” not “The user is anomalous.”
- Do not expose raw feature names such as `host_entropy`, `top_host_ratio`, or `degree_centrality` in the default view. Translate them into concise labels such as “Device variety,” “Most-used device,” and “Shared device connections,” with optional help text.
- Do not expose raw enum values such as `step_up_mfa`, `alert_only`, or `terminate_session` outside technical detail views.
- Keep model names, score normalization, fusion weighting, feature versions, and internal identifiers in secondary detail areas.
- Every technical term that remains visible must have nearby explanatory text or help content.
- Preserve exact backend values in data contracts; this directive changes presentation language, not domain or API naming.

## Visual foundation

### Palette

Use cool near-white and light gray as the foundation, with graphite structure and Soft Carbon as the primary product color. Soft Carbon anchors focus, active navigation, links, and recommended actions. Purple, bright blue, saturated green, yellow-tinted backgrounds, copper, and oxblood should not appear in the primary interface. Moss is reserved for semantic safe states, not branding.

| Role           | Token                  | Value     |
| -------------- | ---------------------- | --------- |
| Deep structure | `--color-graphite-950` | `#222827` |
| Shell surface  | `--color-graphite-900` | `#303837` |
| Primary text   | `--color-graphite-800` | `#26302F` |
| Muted text     | `--color-graphite-500` | `#687371` |
| Canvas         | `--color-paper-100`    | `#F7F8F7` |
| Surface        | `--color-paper-50`     | `#FFFFFF` |
| Subtle surface | `--color-stone-100`    | `#F0F2F1` |
| Border         | `--color-stone-300`    | `#E1E6E4` |
| Primary accent | `--color-primary`      | `#3B4140` |
| Accent soft    | `--color-primary-soft` | `#EDF0EF` |
| Focus/action   | `--color-primary`      | `#3B4140` |
| Caution        | `--color-ochre-600`    | `#A87528` |
| Lockout        | `--color-brick-600`    | `#984A43` |
| Safe           | `--color-moss-600`     | `#667A68` |
| Information    | `--color-neutral-600`  | `#667477` |

Risk states must always combine color with a text label, icon or shape, and score position or marker.

| Semantic token         | Meaning                     | Presentation                            |
| ---------------------- | --------------------------- | --------------------------------------- |
| `--color-moss-600`     | safe, healthy, completed    | moss label and stable marker            |
| `--color-ochre-600`    | caution, review, step-up    | ochre label and review cue              |
| `--color-brick-600`    | lockout, blocked, high risk | brick label and explicit action outcome |
| `--color-neutral-600`  | neutral system information  | neutral label or annotation             |
| `--color-graphite-500` | unknown, pending, disabled  | muted label, never safe by default      |

Keep risk colors out of large page backgrounds. Apply them to labels, thin rules, score markers, icons, and small supporting surfaces.

### Typography

Use a crisp application-oriented type system:

```css
:root {
    --font-sans: "DM Sans", "Segoe UI", sans-serif;
    --font-display: var(--font-sans);
    --font-mono: "IBM Plex Mono", "Cascadia Code", Consolas, monospace;
}
```

Use `DM Sans` for all primary headings, controls, and dense operational content. Use the monospace face for scores, timestamps, identifiers, and event values. Serif type is not part of the primary application UI.

| Role             | Size / line height | Weight | Use                                   |
| ---------------- | ------------------ | ------ | ------------------------------------- |
| page title       | `30px / 36px`      | 600    | primary page heading                  |
| display emphasis | `28px / 32px`      | 500    | selected incident or explanation lead |
| section title    | `17px / 23px`      | 650    | workspace and evidence headings       |
| body             | `14px / 21px`      | 400    | normal content                        |
| compact body     | `13px / 18px`      | 400    | dense ledger rows and metadata        |
| label            | `11px / 16px`      | 650    | short overlines and status labels     |
| metric           | `24px / 28px`      | 650    | score and signal-strip values         |
| data             | `13px / 18px`      | 450    | IDs, timestamps, scores, raw values   |

Use sentence case for headings and controls. Use uppercase only for short overlines, status labels, and navigation group labels. Keep dense-view body text at or above `13px`.

### Spacing and shape

Use a 4px base unit:

```css
:root {
    --space-1: 4px;
    --space-2: 8px;
    --space-3: 12px;
    --space-4: 16px;
    --space-5: 20px;
    --space-6: 24px;
    --space-8: 32px;
    --space-10: 40px;
    --space-12: 48px;
    --radius-control: 6px;
    --radius-panel: 10px;
    --radius-status: 999px;
    --shadow-floating: 0 12px 32px rgb(34 40 39 / 0.12);
}
```

Prefer open surfaces and separators over boxed cards. Use cards only for independent workflows or high-priority evidence. Use thin rules, inset bands, tabs, rails, and timeline structures for hierarchy.

Avoid excessive rounded corners. Shadows are reserved for drawers, menus, and floating command surfaces. Ordinary content should be separated primarily by whitespace, rules, and tonal contrast.

### Tailwind theme

Implement these tokens with Tailwind v4's CSS-first theme format in `apps/dashboard/src/styles/tokens.css`. Do not introduce a `tailwind.config.js` for these values.

```css
@import "tailwindcss";

@theme {
    --color-graphite-950: #222827;
    --color-graphite-900: #303837;
    --color-graphite-800: #26302f;
    --color-graphite-500: #687371;
    --color-paper-100: #f1f3f1;
    --color-paper-50: #fafbfa;
    --color-stone-100: #e7ebe9;
    --color-stone-300: #cdd5d2;
    --color-primary: #3b4140;
    --color-primary-soft: #edf0ef;
    --color-ochre-600: #a87528;
    --color-brick-600: #984a43;
    --color-moss-600: #667a68;
    --color-neutral-600: #667477;
    --font-sans: "DM Sans", "Segoe UI", sans-serif;
    --font-display: var(--font-sans);
    --font-mono: "IBM Plex Mono", "Cascadia Code", Consolas, monospace;
    --spacing-18: 4.5rem;
    --spacing-60: 15rem;
    --spacing-360: 90rem;
    --radius-control: 0.375rem;
    --radius-panel: 0.625rem;
    --shadow-floating: 0 12px 32px rgb(34 40 39 / 0.12);
    --breakpoint-xl: 90rem;
}
```

Keep semantic utility compositions named and consistent. Avoid arbitrary color values in component markup.

## Application organization

### Workspace shell

Use a layered workspace rather than a conventional full-width sidebar:

```text
┌─────────────────────────────────────────────────────────────┐
│ context bar: tenant · mode · freshness · analyst             │
├──────────────┬──────────────────────────────┬───────────────┤
│ command rail │ primary operational surface  │ evidence rail  │
│ navigation   │ feed / config / chart        │ explanation    │
└──────────────┴──────────────────────────────┴───────────────┘
```

Desktop proportions:

- command rail: `72px` collapsed icon rail, `232px` expanded navigation
- context bar: `56px`
- evidence rail: `360–420px`
- content padding: `24–32px`
- maximum content width: fluid, approximately `1600px`

The navigation rail should be icon-led by default. The active item can expand into a labeled current-workspace tab rather than using a large filled sidebar button.

Keep tenant, operating mode, feed freshness, and analyst identity visible at all times. `shadow`, `alert_only`, and `enforce` materially change how an analyst interprets a decision.

Navigation groups:

- **Monitor**: Threat feed, Events
- **Investigate**: Event detail entered from the feed
- **Respond**: Enforcement history
- **Configure**: Threshold profiles, operating mode, provider connections

### Page anatomy

Every primary page uses the same sequence:

1. context bar
2. page heading with overline, title, purpose, and primary action when needed
3. signal strip with only decision-relevant metrics
4. primary operational workspace
5. evidence, audit context, empty state, or pagination

Do not place a large marketing hero above operational data. The first viewport should answer “what needs attention?” and “what mode are we operating in?”

## Core components

### Signal strip

Replace large metric-card rows with a horizontal strip of operational signals:

```text
23 lockout signals   87 caution signals   1,842 events   Feed delayed 12s
```

Each item uses a number, short label, trend indicator, and thin baseline marker. This keeps summary data visible without creating a row of disconnected cards.

### Threat ledger

Use a ledger-style event surface rather than a generic table:

- rows are separated by fine rules, not card borders
- the left risk marker varies by risk band
- the score is rendered as a compact horizontal trace
- policy outcome is an inline action phrase
- the selected event receives a parchment highlight and aubergine edge rule
- timestamps and identifiers use monospace
- secondary metadata appears beneath the primary value

The primary scan order is risk band and score, user and time, source/device context, then policy action and enforcement state.

On desktop, selecting a row updates the evidence rail without hiding the feed context. Show freshness explicitly, for example `Updated 12 seconds ago`.

### Evidence rail

Keep the explanation view persistent on desktop instead of treating it as a temporary card. Use stacked sections separated by labels and rules:

- Decision
- Score composition
- Observed signals
- Baseline comparison
- Policy outcome
- Enforcement history

Use expandable evidence rows and a vertical timeline for enforcement history. The rail should visually resemble an evidence dossier.

Explainability must distinguish observed facts from interpretation. Use labels such as `Observed`, `Compared with baseline`, and `Policy result`.

### Score instrument

Avoid gauges and oversized circular charts. Use a horizontal instrument:

```text
safe ───────── caution ───────── lockout
0              40       70             100
                              ● 92
```

Add small contribution bars for global model, user behavior, context/environment, and entity or asset risk. Use the same threshold geometry in the threat feed, event detail, and threshold editor.

The score component must include the normalized range, active threshold profile, band label, threshold markers, and a clear “not available” treatment when a component is absent.

### Threshold editor

Treat threshold editing as a configuration workflow, not a dashboard widget. Use a split profile workspace:

- left: profile index
- center: editable threshold instrument
- right: live scenario preview

Identify the active profile with an aubergine tab and a small active stamp. Threshold changes should immediately update the preview outcome.

Include validation help, scope, last updated time, active/inactive state, and a review summary before save. Use caution-colored confirmation for changes that alter lockout behavior.

### Inline annotations

Use annotation blocks instead of generic alert cards:

- `Observed`
- `Compared with baseline`
- `Policy result`
- `Simulation note`

Each annotation can use a colored vertical rule, small overline, and short explanatory paragraph.

### Enforcement history

Use a chronological table or vertical timeline with action type, user/event, provider, status, requested time, completed time, and failure reason. Pending, succeeded, failed, skipped, and simulated outcomes each need distinct labels. In `shadow` mode, simulated actions must be visibly different from real provider actions.

## Responsive behavior

Desktop is the primary interface.

At widths below `1100px`:

- collapse the evidence rail below the main workspace
- reduce the navigation rail to icons
- move filters into a horizontal scroll strip
- preserve ledger rows where possible

At widths below `760px`:

- convert the command rail into a drawer
- make the context bar two rows
- convert ledger rows into self-contained event entries; never separate the user from the event data it describes
- keep each mobile event entry together with its occurred time, user, sign-in type, result, risk level, and overall risk score
- expand the selected event in place so its activity summary and response decision remain visibly attached to that event
- place score, decision, evidence, and enforcement history in one vertical sequence
- keep the selected event state visible during navigation

The mobile experience is a compressed analyst workflow, not a separate visual language. Desktop may use columns because the full event remains visible in one viewport; mobile must prioritize relationship and context over table density.

## Interaction rules

- Keyboard focus uses a 2px apricot or aubergine outline with a 2px offset.
- Minimum interactive target is `40px` high; compact ledger controls may be `32px` only when adjacent spacing is clear.
- Loading states use skeleton rows and preserve layout; avoid full-screen spinners for feed refreshes.
- Empty states explain the condition and give the next useful action.
- Errors state what failed, whether data may be stale, and how to retry.
- Refreshing the feed must not erase the selected event or reset filters.
- Use motion only for drawer transitions, row/detail entry, and staged loading. Keep transitions between `120ms` and `220ms` and respect `prefers-reduced-motion`.
- Never animate a risk score continuously; a changing score is data, not decoration.

## Data display conventions

- timestamps use local time in the primary view and expose UTC on hover/detail
- scores display three decimals when model precision matters, for example `0.463`
- IDs and provider event references use monospace and allow copy
- labels use domain terms consistently: `safe`, `caution`, `lockout`, `shadow`, `alert_only`, `enforce`
- show `No action taken` explicitly when policy evaluates but enforcement is skipped
- pair every chart or color-coded scale with a textual legend
