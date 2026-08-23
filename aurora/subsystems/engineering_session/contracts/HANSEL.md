# ======================================================================
# FILE: aurora/subsystems/engineering_session/contracts/HANSEL.md
# START: ENGINEERING_SESSION_HANSEL_CATALOGUE
# ======================================================================

# Engineering Session Management — Hansel Catalogue

## Purpose

Engineering Session Management coordinates Aurora's active engineering
workflow.

It owns session lifecycle and active-work coordination across Aurora while
leaving domain authority with the subsystems that own the underlying data and
behavior.

---

## Ownership

Engineering Session Management owns:

```text
engineering session start and end
active session state
work-time attribution
active Planning work coordination
session-level workflow events
cross-subsystem session coordination
```

It may coordinate:

```text
Planning
Delta Notes
Component Registry
Hansel
Wu Chat
telemetry
validation
future Aurora subsystems
```

Those subsystems retain ownership of their own domain behavior and data.

---

## Presentation Surfaces

Engineering Session controls may appear wherever the workflow requires them.

Known presentation surfaces include:

```text
Aurora Console
    overall engineering-session start/end
    total session timer
    workspace lock/unlock

Wu Chat
    active work controls
    session-management messages
    Planning Step work events
    Delta Notes processing
    Component Registry maintenance
    Component Registry enrichment
```

UI location does not determine domain ownership.

---

## Current Implementation Authority

Engineering Session Management has established persistence, API, and service
authorities.

For session persistence:

```text
aurora/subsystems/engineering_session/models.py
```

For browser/API workflow routing:

```text
aurora/subsystems/engineering_session/api/endpoint.py
```

The API package contains bounded action modules for specific coordinated
workflows.

Enter those modules through `endpoint.py` rather than assuming Engineering
Session owns the underlying domain behavior.

For session lifecycle behavior:

```text
aurora/subsystems/engineering_session/services/lifecycle.py
```

For Planning coordination:

```text
aurora/subsystems/engineering_session/services/planning.py
```

For Delta Notes coordination:

```text
aurora/subsystems/engineering_session/services/delta_notes.py
```

For session-status behavior:

```text
aurora/subsystems/engineering_session/services/status.py
```

These authorities define Engineering Session coordination behavior only.

When implementation crosses into Planning, Delta Notes, Component Registry,
Hansel, Wu Chat, or another subsystem, follow that subsystem's canonical
`contracts/HANSEL.md` rather than extending Engineering Session ownership.

---

## Component Registry Session Events

Routine deterministic registry maintenance:

```text
daurora-cmd maintain_component_registry
```

Semantic enrichment:

```text
daurora-cmd enrich_component_registry
```

Engineering Session Management may coordinate these operations but does not own
Component Registry behavior.

---

## Unknown Territory

If a session-management task requires an authority not identified here:

1. perform the narrowest discovery necessary;
2. enter an owning subsystem through its `contracts/HANSEL.md` when available;
3. preserve that subsystem's ownership boundary;
4. add a breadcrumb here only when the route is durable and session-specific.

---

## Sufficient Authority

Stop discovery when all four are known:

1. who owns the behavior;
2. what must change;
3. what must remain unchanged;
4. how the change will be validated.

Do not preload unrelated subsystem knowledge merely because Engineering Session
Management may eventually coordinate it.

---

## Catalogue Reconciliation

After changing session workflow, ask:

> Has this change created or invalidated a durable Engineering Session
> breadcrumb?

Update this catalogue only when the answer is yes.

Do not turn this catalogue into a description of every subsystem that may
participate in an engineering session.

# ======================================================================
# FILE: aurora/subsystems/engineering_session/contracts/HANSEL.md
# END: ENGINEERING_SESSION_HANSEL_CATALOGUE
# ======================================================================