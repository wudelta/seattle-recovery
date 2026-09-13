# ======================================================================
# FILE: aurora/subsystems/decision_engine/contracts/UI_MAP.md
# START: DECISION_ENGINE_UI_MAP
# ======================================================================

# Decision Engine UI Map

## Purpose

Route Decision Engine UI work to the narrowest authoritative repository surface.

## Aurora Console Entry

```text
aurora/templates/aurora/aurora_console.html
```

## Panel Structure

```text
aurora/templates/aurora/decision_engine/decision_engine_console_panel.html
```

## Browser Behavior

```text
aurora/static/aurora/js/decision_engine/decision_engine.js
```

## Styling

```text
aurora/static/aurora/css/decision_engine.css
```

## API and Aggregation

```text
aurora/subsystems/decision_engine/api/endpoint.py
aurora/subsystems/decision_engine/services/inbox.py
```

The current UI is read-only. It must not mutate Delta Notes or Engineering
Findings, and it does not establish reconciliation, approval, assignment, or
Planning-ingestion behavior.

# ======================================================================
# END: DECISION_ENGINE_UI_MAP
# ======================================================================
