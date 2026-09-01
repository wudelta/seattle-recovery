# ======================================================================
# FILE: aurora/subsystems/planning/contracts/HANSEL.md
# START: PLANNING_HANSEL_CATALOGUE
# ======================================================================

# Planning — Hansel Catalogue

## Purpose

Planning owns Aurora's persisted engineering-work hierarchy:

```text
Project → Initiative → Phase → Step
```

Use this catalogue to move from a Planning task to the narrowest authoritative
contract, service, API, or framework adapter required to perform it.

Planning does not own repository discovery or AI execution.

---

## Knowledge Catalogue

### Determine what engineering work happens next

Go to:

```text
aurora/subsystems/planning/contracts/INITIATIVE_TRANSITION.md
```

Use this when:

- no executable Initiative is active;
- an Initiative was completed or paused;
- priorities are changing between Initiatives;
- or a worker must present available engineering objectives.

The worker presents Planning choices.

The human selects the engineering objective.

---

### Inspect persisted Planning state

Use:

```text
aurora/management/commands/inspect_planning_state.py
```

Commands:

```text
daurora-cmd inspect_planning_state
daurora-cmd inspect_planning_state --initiative <initiative_id>
```

Add `--full` only for forensic detail.

This management command is an application-level framework adapter to
Planning-owned reconciliation behavior.

Do not reconstruct persisted Planning state through ad hoc ORM queries when this
entry point can answer the question.

---

### Understand Planning lifecycle and reconciliation

Go to:

```text
aurora/subsystems/planning/contracts/LIFECYCLE_AND_RECONCILIATION.md
```

Use this for:

- ACTIVE / PAUSED / COMPLETED lifecycle behavior;
- active-work invariants;
- pause and resume semantics;
- assignment and historical attribution;
- completion eligibility;
- Planning reconciliation;
- Planning and Engineering Session boundaries.

---

### Execute worker Planning transitions

Use:

```text
aurora/subsystems/planning/services/workflow.py
```

Use this when a worker must:

- complete validated current work;
- stop at Phase or Initiative review boundaries;
- approve eligible current Phase work;
- or advance to the next executable Step.

Do not reconstruct these workflows from lower-level lifecycle primitives when a
worker-facing operation already exists.

---

### Route a BLOCKING Engineering Finding into remedial work

Read:

```text
aurora/subsystems/planning/contracts/BLOCKING_REMEDIATION.md
```

Executable Planning boundary:

```text
aurora/subsystems/planning/services/remediation.py
```

Use this when required current work encounters a qualified BLOCKING Engineering
Finding and remedial work must be inserted into the same Initiative without
losing the interrupted resume position.

Engineering Discovery owns finding qualification and blocking classification.

Planning owns remedial hierarchy creation and lifecycle mutation.

---

### Route executable Planning work into repository authority

When an ACTIVE Planning Step requires repository implementation, treat the Step
as the current engineering task and return to:

```text
aurora/subsystems/hansel/contracts/HANSEL.md
```

Follow Hansel to the owning repository authority and then to the narrowest
task-specific source required for implementation and validation.

Do not use Planning UI selection state as execution authority.

---

### Expose bounded Planning state to an AI worker

Use:

```text
aurora/subsystems/planning/api/worker_resources.py
```

This is the read-only worker application boundary for one bounded Planning
resource.

It owns Planning-side resolution and serialization.

It does not own AI continuation, worker orchestration, or repository discovery.

---

### Understand or change Planning CRUD/API behavior

Start at:

```text
aurora/subsystems/planning/api/endpoint.py
```

Then follow the narrowest relevant module under:

```text
aurora/subsystems/planning/api/
```

CRUD does not own lifecycle-controlled mutation.

---

### Import, export, or append structured Planning data

Go to:

```text
aurora/subsystems/planning/io/
```

Use the executable schema and updater there as the authoritative persistence
boundary for structured Planning dictionaries.

---

### Generate an import-ready Planning dictionary

Go to:

```text
aurora/subsystems/planning/contracts/PLANNING_DICTIONARY_GENERATION.md
```

Use this authority to transform engineering intent into a validated,
import-ready Planning dictionary.

---

### Understand or change Planning data models

Go to:

```text
aurora/subsystems/planning/models.py
```

Use this only when the task requires Planning persistence structure or model
behavior.

---

### Understand or change the Planning Console UI

Go to:

```text
aurora/subsystems/planning/contracts/UI_MAP.md
```

---

### Understand or change Planning administration

Go to:

```text
aurora/subsystems/planning/admin.py
```

---

## Unknown Territory

If the task is not covered by this catalogue:

1. do not infer ownership or behavior;
2. inspect only the immediate Planning subsystem structure needed to locate the
   narrowest likely authority;
3. inspect framework-level surfaces only when the required authority may
   legitimately live there;
4. request additional repository evidence only when required;
5. add a Hansel breadcrumb only when discovery reveals a durable authority that
   future workers should not have to rediscover.

---

## Sufficient Authority

Stop following breadcrumbs when all four are known:

1. who owns the behavior;
2. what must change;
3. what must remain unchanged;
4. how the change will be validated.

Do not load additional context merely because it exists.

A breadcrumb must reduce uncertainty, establish authority, or define validation.

---

## Authority Reconciliation

After a Planning change, ask:

> Has this change made any breadcrumb or ownership route in this catalogue stale?

If no, do not change this file.

If yes:

1. point the affected breadcrumb to the current authority;
2. remove obsolete routing;
3. add new routing only for a durable knowledge destination;
4. verify every changed breadcrumb resolves to a real repository authority.

Keep this catalogue navigational.

Do not turn it into implementation documentation.

# ======================================================================
# END: PLANNING_HANSEL_CATALOGUE
# ======================================================================
