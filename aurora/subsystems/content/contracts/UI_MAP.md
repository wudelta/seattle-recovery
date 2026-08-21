# ======================================================================
# FILE: aurora/subsystems/content/contracts/UI_MAP.md
# START: CONTENT_UI_MAP
# ======================================================================

# Content UI Map

## Purpose

Route Content UI tasks to the narrowest authoritative repository surface.

This file is a map, not a UI specification.

## Console Structure

For Content Console structure, editor controls, inventory layout, and
operational log markup:

```text
aurora/templates/aurora/content/content_console_panel.html
```

## Client Behavior

For Content inventory behavior, editing interactions, persistence controls, and
operational log behavior:

```text
aurora/static/aurora/js/content/content.js
```

## Styling

For Content-specific presentation:

```text
aurora/static/aurora/css/content.css
```

## Operational Pipeline Log Feed

The operational log element is:

```text
#cc-terminal-stream
```

The browser writer is:

```text
aurora/static/aurora/js/content/content.js
```

Normalization target:

```text
newest message at the top
older history below
viewport remains at the top after a new message
```

## Unknown UI Territory

If the requested Content UI responsibility is not mapped here:

1. do not infer the owning file;
2. perform the narrowest exact-symbol discovery necessary;
3. add a breadcrumb only for a durable UI authority.

## Sufficient Authority

Stop UI discovery when the authoritative surface, bounded change, preserved
behavior, and validation method are known.

## Authority Reconciliation

After a Content UI change, verify this map still routes the affected
responsibility correctly.

Keep the map small and pattern-oriented.

# ======================================================================
# END: CONTENT_UI_MAP
# ======================================================================
