<!-- ====================================================================== -->
<!-- FILE: aurora/subsystems/delta_notes/contracts/TECHNICAL_DEBT.md -->
<!-- START: DELTA_NOTES_TECHNICAL_DEBT -->
<!-- ====================================================================== -->

# Delta Notes Technical Debt

## Current Responsibility

Delta Notes is a transient Post-it note system.

Its current responsibility is limited to:

* capture an idea;
* display captured ideas;
* edit an idea;
* delete an idea.

Future Planning ingestion is explicitly outside the current refactor.

---

## Active Defects

### Delta Notes UI

**Status:** BROKEN

The Delta Notes panel is currently non-functional.

The failure predates the current subsystem refactor.

Current policy:

* do not preserve broken behavior merely for compatibility;
* restore only the Post-it note workflow defined by this subsystem;
* unrelated historical functionality is not part of the repair target.

---

## Duplicate API Authority

**Status:** ACTIVE ARCHITECTURAL DEBT

Two separate implementations of `delta_notes_endpoint()` currently exist:

```text
aurora/api/endpoints.py
aurora/api/delta_notes_api.py
```

The currently routed implementation is:

```text
aurora/api/endpoints.py
```

The two implementations have diverged and contain different behavior.

Current policy:

* establish one canonical Delta Notes API inside this subsystem;
* preserve only behavior required by the Post-it note responsibility;
* eliminate the obsolete duplicate implementation;
* remove the corresponding legacy API file from `aurora/api/` as part of the subsystem migration.

---

## Misowned Timer Behavior

**Status:** RELOCATE

Delta Notes currently contains time-tracking behavior through fields and
actions such as:

```text
total_seconds_logged
sync_timer
```

Time tracking is not part of the Delta Notes Post-it note responsibility.

The capability is expected to belong to the Aurora Console or another
repository-wide engineering session metrics owner.

Current policy:

* remove timer behavior from the Delta Notes runtime;
* preserve useful timer implementation before removing its current ownership;
* do not redesign or expand timer functionality during this refactor;
* relocate the capability through a separate bounded migration when its
  target ownership is defined;
* existing database fields may remain temporarily if removing or relocating
  them requires an unrelated schema migration.

Future purpose:

Timer and activity metrics may provide actual engineering effort data to
Planning and Hansel.

Examples include comparing:

```text
Estimated initiative duration: 2 hours
Actual engineering duration:   4 hours
```

Such metrics can later support analysis of:

* estimate accuracy;
* unexpected discovery work;
* validation failures;
* excessive Hansel navigation;
* other sources of engineering variance.

---

## Legacy Project Compilation

**Status:** REMOVE

Delta Notes currently contains legacy behavior that compiles notes directly
into:

```text
project.md
```

This includes the `compile_blueprint` action.

Direct project file compilation is no longer part of the Delta Notes
responsibility.

Current policy:

* remove direct `project.md` writes;
* remove blueprint compilation behavior;
* Planning will eventually own consumption of captured ideas.

---

## Misowned Telemetry

**Status:** RELOCATE

The active Delta Notes endpoint currently uses `PageSkeletonBuilder`
for telemetry.

`PageSkeletonBuilder` does not own telemetry and should not participate in the
Delta Notes runtime.

Current policy:

* remove this dependency from Delta Notes;
* preserve any useful telemetry behavior for relocation;
* establish a proper telemetry owner in a future bounded migration.

---

## Wu Coupling

**Status:** REMOVE

Wu currently consumes Delta Notes directly.

This creates competing workflow authority between free-form notes, Wu, and the
Planning subsystem.

Current policy:

* Wu must stop consuming Delta Notes directly;
* Delta Notes remains a lightweight Post-it note capture system;
* Planning will eventually own ingestion of captured ideas;
* Wu should consume Planning, not Delta Notes.

---

## Migration Success Criteria

The Delta Notes refactor is complete when:

1. Delta Notes has one canonical API implementation.
2. The UI can create, display, edit, and delete Post-it notes.
3. Timer functionality has been removed from Delta Notes ownership.
4. `project.md` compilation has been removed.
5. `PageSkeletonBuilder` has been removed from the Delta Notes runtime.
6. Duplicate endpoint implementations have been consolidated.
7. Delta Notes follows the standard subsystem layout.
8. Remaining known debt is documented here rather than hidden in legacy code.

<!-- ====================================================================== -->
<!-- END: DELTA_NOTES_TECHNICAL_DEBT -->
<!-- ====================================================================== -->
