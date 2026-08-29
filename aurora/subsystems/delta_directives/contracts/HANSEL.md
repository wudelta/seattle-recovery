# ======================================================================
# FILE: aurora/subsystems/delta_directives/contracts/HANSEL.md
# START: DELTA_DIRECTIVES_HANSEL_CATALOGUE
# ======================================================================

# Delta Directives — Hansel Catalogue

## Purpose

Delta Directives owns Aurora's persistent AI worker instructions and execution
constraints.

It defines worker configuration.

It does not own AI provider implementation, shared AI execution, Planning, or
workflow orchestration.

---

## Knowledge Catalogue

### Understand or change directive data

Go to:

```text
aurora/subsystems/delta_directives/models.py
```

`DeltaDirectives.instructions` is the canonical persistent worker-instruction
authority.

Worker instructions use Markdown as their canonical textual representation.

The stored Markdown is semantic configuration, not presentation content.
Persistence and editing surfaces must preserve the instruction text without
silently converting it to HTML or otherwise changing its meaning.

HTML may be produced for presentation, but HTML is not a canonical directive
storage format.

Changes to worker behavior belong in the directive instructions rather than in
consumer code when the behavior is properly a worker instruction. Execution
mechanics remain owned by the consuming workflow.


### Deploy or replace canonical worker instructions

Go to:

```text
aurora/subsystems/delta_directives/contracts/DIRECTIVE_DEPLOYMENT.md
```

This contract owns the controlled workflow for moving repository-owned worker
instructions into persistent `DeltaDirectives.instructions`.

Use it when the task involves directive deployment, directive validation,
dry-run/apply behavior, deployment triggers, or restricting uncontrolled
instruction mutation.

Do not infer deployment behavior from the UI or API merely because those
surfaces can currently mutate directive records.


### Understand or change Delta Directives API behavior

Go to:

```text
aurora/subsystems/delta_directives/api/endpoint.py
```

### Understand or change Delta Directives UI

Go to:

```text
aurora/subsystems/delta_directives/contracts/UI_MAP.md
```

### Understand or change Delta Directives administration

Go to:

```text
aurora/subsystems/delta_directives/admin.py
```

### Understand how directives are executed by AI workers

Delta Directives does not own execution.

Follow the shared execution authority referenced by the consuming workflow.

If that authority is not established by the current task trail, do not infer
it. Use the narrowest consumer discovery required to locate it.

---

## Unknown Territory

If the task is not covered by this catalogue:

1. do not infer ownership or behavior;
2. inspect the immediate Delta Directives subsystem structure for the narrowest
   likely authority;
3. if framework-owned surfaces may contain the missing authority, perform the
   narrowest repository discovery needed to locate it;
4. request additional repository evidence only when required;
5. add a Hansel breadcrumb only when discovery reveals a durable knowledge
   destination.

---

## Sufficient Authority

Stop following Hansel breadcrumbs when all four are known:

1. who owns the behavior;
2. what must change;
3. what must remain unchanged;
4. how the change will be validated.

Do not load additional files merely because they exist.

A breadcrumb must reduce uncertainty, establish missing authority, or define
validation. Otherwise, do not follow it.

---

## Authority Reconciliation

After completing a change, ask:

> Has this change made any breadcrumb, ownership statement, or routing decision
> in this `HANSEL.md` stale or non-authoritative?

If no, no Hansel update is required.

If yes:

1. point the affected catalogue entry to the new authority;
2. remove obsolete breadcrumbs;
3. add new breadcrumbs only for genuine durable knowledge destinations;
4. verify every changed breadcrumb resolves to an existing authority.

Do not add implementation details learned during the task.

Keep the catalogue accurate and small.

# ======================================================================
# END: DELTA_DIRECTIVES_HANSEL_CATALOGUE
# ======================================================================