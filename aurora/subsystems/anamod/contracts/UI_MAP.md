# ======================================================================
# FILE: aurora/subsystems/anamod/contracts/UI_MAP.md
# START: ANAMOD_UI_MAP
# ======================================================================

# Anamod UI Map

## Purpose

Route Anamod UI tasks to the narrowest authoritative repository surface.

This file is a map, not a UI specification.

---

## Console Structure

For Anamod Console structure, editor layout, Workflow Controls, Component
Registry description presentation, Activity state, and operational-log markup:

```text
aurora/templates/aurora/anamod/anamod_console_panel.html
```

---

## Editor and Active-File Behavior

For Monaco coordination, active-file state, save/discard behavior, Component
Registry description loading, registry workflow controls, and Anamod operational
log behavior:

```text
aurora/static/aurora/js/anamod/anamod.js
```

---

## Project Hierarchy and Workspace Interaction

For Project Hierarchy behavior, tree refresh and expansion, Load/Create,
repository-path loading, file/directory creation, rename/delete interaction, and
tree focus:

```text
aurora/static/aurora/js/anamod/anamod_workspace.js
```

This is a separate browser authority from `anamod.js`.

---

## Styling

For Anamod-specific presentation:

```text
aurora/static/aurora/css/anamod.css
```

---

## Component Registry Integration

Anamod consumes Component Registry knowledge and operations through:

```text
aurora/subsystems/component_registry/contracts/HANSEL.md
```

Component Registry retains ownership of:

```text
file-path registry lookup
description freshness
deterministic maintenance
AI enrichment
```

Anamod owns only presentation and invocation of those capabilities.

---

## Shared Telemetry

The shared Aurora Console WebSocket transport is dispatched to browser
consumers through:

```text
aurora/static/aurora/js/console.js
    aurora:telemetry_stream
```

Anamod consumes relevant Component Registry telemetry in:

```text
aurora/static/aurora/js/anamod/anamod.js
```

Do not create an Anamod-specific WebSocket transport.

---

## Operational Pipeline Log Feed

The operational log element is:

```text
#anamod-terminal-stream
```

The browser writer is:

```text
aurora/static/aurora/js/anamod/anamod.js
```

Reference behavior:

```text
newest message is inserted at the top
older history descends
latest activity remains immediately visible
```

---

## Unknown UI Territory

If the requested Anamod UI responsibility is not mapped here:

1. do not infer the owning file;
2. perform the narrowest exact-symbol discovery necessary;
3. add a breadcrumb only for a durable UI authority.

---

## Sufficient Authority

Stop UI discovery when the authoritative surface, bounded change, preserved
behavior, and validation method are known.

---

## Authority Reconciliation

After an Anamod UI change, verify this map still routes each affected concern
to the correct authority.

Keep the map small and pattern-oriented.

# ======================================================================
# END: ANAMOD_UI_MAP
# ======================================================================