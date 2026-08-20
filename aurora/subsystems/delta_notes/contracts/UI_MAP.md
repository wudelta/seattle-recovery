# ======================================================================
# FILE: aurora/subsystems/delta_notes/contracts/UI_MAP.md
# START: DELTA_NOTES_UI_MAP
# ======================================================================

# Delta Notes UI Map

## Purpose

Route Delta Notes UI tasks to the narrowest authoritative repository surface.

This file is a map, not a UI specification.

---

## Delta Notes Console Structure

For the Delta Notes Console panel structure:

```text
aurora/templates/aurora/delta_notes/delta_notes_console_panel.html
```

---

## Delta Notes Browser Behavior

For Delta Notes loading, queue rendering, editing, deletion, and processed-state
display:

```text
aurora/static/aurora/js/delta_notes/delta_notes.js
```

This is the authoritative browser-side surface for refreshing the unprocessed
and processed Delta Notes queues.

---

## Aurora Console Integration

For loading the Delta Notes panel, JavaScript, or endpoint configuration into
Aurora Console:

```text
aurora/templates/aurora/aurora_console.html
```

Use this authority only when the task concerns application-level integration
rather than Delta Notes behavior itself.

---

## Cross-Subsystem UI Changes

Another subsystem must not directly manipulate Delta Notes UI state.

When another subsystem changes Delta Notes data:

```text
owning subsystem mutation
    ↓
browser event
    ↓
Delta Notes UI receives event
    ↓
Delta Notes reloads its authoritative state
```

The Delta Notes browser module remains responsible for rendering its own data.

---

## Unknown UI Territory

If a Delta Notes UI responsibility is not mapped here:

1. do not infer the owning file;
2. perform the narrowest discovery necessary to locate the authority;
3. if an existing breadcrumb points to a missing or stale authority, treat that
   as a Hansel defect;
4. repair the breadcrumb or create the missing durable authority before the task
   is considered complete;
5. add a new route only when future workers should not have to rediscover it.

---

## Sufficient Authority

Stop UI discovery when:

1. the authoritative UI surface is known;
2. the requested change is bounded;
3. behavior that must remain unchanged is known;
4. validation is known.

---

## Authority Reconciliation

After a Delta Notes UI architectural change, ask:

> Does every affected Hansel breadcrumb still resolve to an existing,
> authoritative destination?

If yes, no catalogue update is required.

If no:

1. repair stale routing;
2. create a missing referenced authority when that authority is genuinely
   required and durable;
3. remove obsolete routing;
4. validate every repaired breadcrumb resolves.

A known broken breadcrumb must not be left for a future worker to rediscover.

# ======================================================================
# END: DELTA_NOTES_UI_MAP
# ======================================================================