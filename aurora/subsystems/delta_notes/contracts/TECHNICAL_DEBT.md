<!-- ====================================================================== -->
<!-- FILE: aurora/subsystems/delta_notes/contracts/TECHNICAL_DEBT.md -->
<!-- START: DELTA_NOTES_TECHNICAL_DEBT -->
<!-- ====================================================================== -->

# Delta Notes Technical Debt

## Current Responsibility

Delta Notes is a lightweight Post-it note system.

Its current responsibility is limited to:

* capture an idea;
* display captured ideas;
* edit an idea;
* delete an idea;
* mark an idea processed.

Planning ingestion is outside the current Delta Notes responsibility.

---

## Current Functional State

**Status:** VERIFIED

The Delta Notes Post-it workflow is functional.

Validated behavior includes:

```text
initial note loading
note creation
unprocessed-note display
marking a note processed
processed-note display
user-scoped persistence
```

The previously reported UI failure was not a Delta Notes defect.

The apparent missing-data condition was caused by the active Aurora session
being authenticated as a different user. Delta Notes correctly scopes records
to:

```text
request.user
```

Do not treat that historical symptom as active Delta Notes technical debt.

---

## Canonical API Authority

**Status:** VERIFIED

The canonical Delta Notes API implementation is:

```text
aurora/subsystems/delta_notes/api/endpoint.py
```

It is exported through:

```text
aurora/subsystems/delta_notes/api/__init__.py
aurora/api/__init__.py
```

and routed through:

```text
aurora/urls.py
```

Do not reintroduce a competing Delta Notes API authority.

---

## Residual Timer State

**Status:** VERIFY / RELOCATE IF STILL PRESENT

Time tracking is not part of the Delta Notes Post-it note responsibility.

Historical Delta Notes behavior included timer state such as:

```text
total_seconds_logged
last_started_at
sync_timer
```

The current Delta Notes API does not own timer behavior.

Existing model fields or other residual timer artifacts may remain.

Before changing them:

1. verify what timer-related state still exists;
2. identify current consumers;
3. preserve useful behavior or data;
4. relocate it only after its owning authority is established.

Do not redesign timer functionality as part of ordinary Delta Notes work.

---

## Legacy Project Compilation

**Status:** VERIFY REMOVAL

Historical Delta Notes behavior compiled notes directly into:

```text
project.md
```

through behavior such as:

```text
compile_blueprint
```

This is not part of the current Delta Notes responsibility and is not present
in the canonical Delta Notes endpoint.

If legacy implementations still exist elsewhere in the repository, they should
not be treated as authoritative Delta Notes behavior.

Planning, not Delta Notes, is the intended authority for structured engineering
work.

---

## Legacy Telemetry Coupling

**Status:** VERIFY REMOVAL

Historical Delta Notes behavior used:

```text
PageSkeletonBuilder
```

for telemetry.

This dependency is not present in the canonical Delta Notes endpoint and is not
part of the Delta Notes responsibility.

If residual legacy references remain, their ownership should be resolved
separately rather than restored to Delta Notes.

---

## Legacy Wu Coupling

**Status:** VERIFY REMOVAL

Historical Wu behavior consumed Delta Notes directly.

Direct Wu consumption is not part of the Delta Notes Post-it responsibility.

If residual coupling remains elsewhere in the repository, determine its current
owner before changing it.

Do not expand Delta Notes into an orchestration or Planning authority.

---

## Remaining Success Criteria

Delta Notes is considered structurally clean when:

1. `aurora/subsystems/delta_notes/api/endpoint.py` remains the single canonical
   Delta Notes API implementation;
2. no live legacy Delta Notes API implementation competes with it;
3. residual timer ownership is identified and resolved when that work becomes
   necessary;
4. obsolete project-compilation behavior is absent from live Delta Notes
   runtime behavior;
5. obsolete telemetry coupling is absent from live Delta Notes runtime
   behavior;
6. obsolete direct Wu coupling is absent from live Delta Notes runtime
   behavior;
7. future Delta Notes changes preserve the lightweight Post-it responsibility.

Do not perform cleanup merely to satisfy this document.

Verify residual debt before acting on it.

<!-- ====================================================================== -->
<!-- END: DELTA_NOTES_TECHNICAL_DEBT -->
<!-- ====================================================================== -->
