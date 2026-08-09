# ======================================================================
# FILE: aurora/subsystems/planning/contracts/UI_MAP.md
# START: PLANNING_UI_MAP
# ======================================================================

# Planning UI Map

## Purpose

Route Planning UI tasks to the narrowest authoritative repository surface.

This file is a map, not a UI specification.

## Aurora Console Entry

For the button or navigation control used to enter Planning:

```text
aurora/templates/aurora/aurora_console.html
```

## Planning Console Structure

For Planning Console layout and rendered workspace structure:

```text
aurora/templates/aurora/planning/
```

For the Initiative navigator structure specifically:

```text
aurora/templates/aurora/planning/workspace.html
```

## Initiative Navigator

For Initiative navigator rendering, ordering, grouping, and filtering:

```text
aurora/static/aurora/js/planning/renderers/navigator_renderer.js
```

For Initiative navigator selection and filter events:

```text
aurora/static/aurora/js/planning/events/initiative_events.js
```

## Planning Client Behavior

For other browser-side Planning behavior:

```text
aurora/static/aurora/js/planning/
```

Follow the narrowest relevant module within that directory.

## Planning Styling

For Planning-specific styling and workspace dimensions:

```text
aurora/static/aurora/css/planning.css
```

## Unknown UI Territory

If the requested Planning UI responsibility is not mapped here:

1. do not infer the owning file;
2. perform the narrowest discovery necessary to locate the authority;
3. add a breadcrumb here only if the newly discovered destination represents a
   durable UI responsibility.

## Sufficient Authority

Stop UI discovery when:

1. the authoritative UI surface is known;
2. the exact requested change is bounded;
3. the behavior that must remain unchanged is known;
4. the validation method is known.

## Authority Reconciliation

After a UI architectural change, ask whether this map still routes the affected
responsibility correctly.

Update this map only when the authoritative destination changes or a durable
UI responsibility has been discovered that future workers should not have to
rediscover.

Do not record transient implementation details.

# ======================================================================
# END: PLANNING_UI_MAP
# ======================================================================