# ======================================================================
# FILE: aurora/subsystems/anamod/contracts/UI_MAP.md
# START: ANAMOD_UI_MAP
# ======================================================================

# Anamod UI Map

## Purpose

Route Anamod UI tasks to the narrowest authoritative repository surface.

This file is a map, not a UI specification.

## Console Structure

For Anamod Console structure, editor layout, action controls, and operational
log markup:

```text
aurora/templates/aurora/anamod/anamod_console_panel.html
```

## Client Behavior

For Anamod editor interaction, workspace actions, Monaco coordination, and
operational log behavior:

```text
aurora/static/aurora/js/anamod/anamod.js
```

## Styling

For Anamod-specific presentation:

```text
aurora/static/aurora/css/anamod.css
```

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
viewport returns to the top after each new message
```

This is the current reference pattern for comparable Aurora operational logs.

## Unknown UI Territory

If the requested Anamod UI responsibility is not mapped here:

1. do not infer the owning file;
2. perform the narrowest exact-symbol discovery necessary;
3. add a breadcrumb only for a durable UI authority.

## Sufficient Authority

Stop UI discovery when the authoritative surface, bounded change, preserved
behavior, and validation method are known.

## Authority Reconciliation

After an Anamod UI change, verify this map still routes each affected concern
to the correct authority.

Keep the map small and pattern-oriented.

# ======================================================================
# END: ANAMOD_UI_MAP
# ======================================================================
