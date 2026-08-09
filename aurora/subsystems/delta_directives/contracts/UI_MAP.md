# ======================================================================
# FILE: aurora/subsystems/delta_directives/contracts/UI_MAP.md
# START: DELTA_DIRECTIVES_UI_MAP
# ======================================================================

# Delta Directives UI Map

## Purpose

Route Delta Directives UI tasks to the narrowest authoritative repository
surface.

This file is a map, not a UI specification.

## Console Structure

For Delta Directives Console layout, controls, and rendered structure:

```text
aurora/templates/aurora/delta_directives/directives_console_panel.html
```

## Client Behavior

For directive inventory rendering, status filtering, selection, and
browser-side interaction:

```text
aurora/static/aurora/js/delta_directives/directives.js
```

## Styling

For Delta Directives-specific presentation:

```text
aurora/static/aurora/css/directives.css
```

## Unknown UI Territory

If the requested Delta Directives UI responsibility is not mapped here:

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
# END: DELTA_DIRECTIVES_UI_MAP
# ======================================================================