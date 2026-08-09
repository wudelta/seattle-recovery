# ======================================================================
# FILE: aurora/subsystems/delta_notes/contracts/HANSEL.md
# START: DELTA_NOTES_HANSEL_CONTRACT
# ======================================================================

# Delta Notes — Hansel Contract

**Knowledge State:** VERIFIED
**Subsystem:** `delta_notes`

---

## Purpose

Delta Notes stores developer intentions, active work notes, and accumulated
focus-time information associated with a developer session.

It provides lightweight persistent engineering continuity.

Delta Notes is not the authoritative Planning system and does not own Initiative,
Phase, or Step lifecycle.

---

## Ownership Boundary

Delta Notes owns:

* persistent developer note entries;
* note text;
* processed/unprocessed state;
* accumulated focus-time state;
* active timer timestamps;
* Delta Notes API behavior;
* Delta Notes Django administration.

Delta Notes does not own:

* Project, Initiative, Phase, or Step planning;
* durable engineering execution history;
* repository discovery;
* Component Registry state;
* AI provider execution;
* worker directives;
* Wu Chat conversation history;
* orchestration of engineering work.

---

## Canonical Data Authority

Authoritative model:

```text
aurora/subsystems/delta_notes/models.py
    DeltaNotesEntry
```

Current persisted state includes:

```text
user
text
created_at
updated_at
processed
total_seconds_logged
last_started_at
```

Delta Notes entries are lightweight developer-session records.

They must not silently become a second Planning hierarchy.

---

## Repository Map

```text
delta_notes/
    admin.py
        Django administration for DeltaNotesEntry.

    models.py
        Authoritative DeltaNotesEntry persistence model.

    api/
        endpoint.py
            Delta Notes API behavior.

    contracts/
        HANSEL.md
            Canonical Hansel discovery entry point.

        TECHNICAL_DEBT.md
            Known Delta Notes technical debt and unresolved implementation
            concerns.

    services/
        __init__.py
            Empty service-layer package.
```

The `services/` directory currently contains no implemented service behavior.

**Knowledge State:** VERIFIED

Its continued existence should be justified by current architecture or removed
if it represents abandoned scaffolding.

---

## Public Entry Points

Primary API entry point:

```text
aurora/subsystems/delta_notes/api/endpoint.py
```

Persistent state:

```text
aurora/subsystems/delta_notes/models.py
```

Administrative interface:

```text
aurora/subsystems/delta_notes/admin.py
```

---

## AI Usage

Delta Notes does not currently own AI-assisted behavior.

**Knowledge State:** VERIFIED

If future AI functionality is introduced, deterministic note persistence and
timer state must remain distinguishable from AI interpretation or summarization.

---

## Dependencies

### Django

Delta Notes depends on:

```text
Django ORM
Django admin
Django API/request handling
```

### Aurora User Model

Entries reference:

```text
settings.AUTH_USER_MODEL
```

No additional subsystem dependency is established by this contract.

---

## Consumers

Known consumers include:

```text
Aurora user interfaces
    Read and modify developer notes and timer state.

Delta
    Uses Delta Notes as lightweight persistent engineering continuity.
```

Whether future orchestration or Planning should consume Delta Notes directly is
not established.

**Knowledge State:** UNKNOWN

Next breadcrumb:

```text
aurora/subsystems/delta_notes/api/endpoint.py
aurora/subsystems/delta_notes/contracts/TECHNICAL_DEBT.md
```

---

## Framework Integration Surfaces

Delta Notes models are re-exported through:

```text
aurora/models.py
```

Delta Notes admin registration is loaded through:

```text
aurora/admin.py
```

These are Django integration surfaces.

Domain ownership remains:

```text
aurora/subsystems/delta_notes/
```

---

## Validation Protocol

### Consumer Mapping

Before moving, renaming, or deleting a Delta Notes model field, API symbol,
module, or UI integration, identify consumers first.

Example:

```bash
grep -RIn <old-path-or-symbol> aurora core_logic
```

The consumer map defines the known blast radius.

---

### Tombstone Validation

After moving, renaming, or deleting Delta Notes assets, search for obsolete:

* imports;
* module paths;
* model symbols;
* field names;
* API references.

Expected:

```text
no live references
```

---

### Model Survival Validation

For source-only model relocation:

```bash
dmakemigrations --check
daurora-cmd check
```

Expected:

```text
No changes detected
System check identified no issues
```

Where appropriate, also verify:

```text
DeltaNotesEntry.__module__
DeltaNotesEntry._meta.app_label
DeltaNotesEntry._meta.db_table
existing row count
```

---

### Admin Survival Validation

After moving admin configuration, verify:

```text
DeltaNotesEntry in admin.site._registry
```

Expected:

```text
True
```

---

### Behavioral Survival Validation

Changes to Delta Notes behavior should prove the affected invariant.

Examples include:

```text
notes remain readable;
notes remain writable where supported;
processed state persists correctly;
focus time remains accumulated correctly;
timer timestamps remain internally consistent.
```

The exact validation should correspond to the behavior changed.

---

## Change Validation Principle

Hansel distinguishes:

```text
structural validation
    subsystem ownership and repository grammar

change-specific validation
    consumer map, tombstone, identity, and survival proof

persistent regression tests
    durable note/timer behavior worth protecting over time
```

A permanent test module is not required merely because a Delta Notes module
exists.

---

## Known Gaps

### Current Functional State

**State:** VERIFIED

Delta Notes is known to have unresolved functional problems in its current user
workflow.

This contract does not infer the cause.

Next authority:

```text
aurora/subsystems/delta_notes/contracts/TECHNICAL_DEBT.md
```

and, where required:

```text
aurora/subsystems/delta_notes/api/endpoint.py
```

Do not use current UI behavior as proof that a structural refactor failed when
the workflow was already broken before that refactor.

---

### Empty Service Layer

**State:** UNKNOWN

The directory:

```text
aurora/subsystems/delta_notes/services/
```

currently contains no service implementation.

Possible explanations include:

```text
planned service extraction
abandoned scaffolding
unfinished migration
```

No explanation is currently verified by this contract.

Next breadcrumb:

```text
aurora/subsystems/delta_notes/contracts/TECHNICAL_DEBT.md
```

If no planned responsibility exists, the empty directory should be considered
for removal.

---

### Planning Relationship

**State:** UNKNOWN

Delta Notes and Planning both represent aspects of engineering work, but their
formal integration boundary is not established here.

Planning is authoritative for structured engineering work.

Delta Notes must not duplicate Planning lifecycle merely because both capture
developer activity.

Next breadcrumb:

```text
aurora/subsystems/planning/contracts/HANSEL.md
aurora/subsystems/delta_notes/contracts/TECHNICAL_DEBT.md
```

---

## Deeper Contracts

### Technical Debt

Authoritative deeper contract:

```text
aurora/subsystems/delta_notes/contracts/TECHNICAL_DEBT.md
```

Use it when investigating:

* known broken behavior;
* incomplete migration;
* unresolved architecture;
* intended future cleanup.

Do not duplicate technical-debt detail in `HANSEL.md`.

---

## Hansel Rules for This Subsystem

A worker modifying Delta Notes must:

1. begin with this contract;
2. preserve Delta Notes as lightweight developer continuity rather than a second
   Planning system;
3. consult `TECHNICAL_DEBT.md` before attempting to repair known broken
   behavior;
4. map consumers before moving or deleting assets;
5. perform tombstone validation after rename or removal;
6. preserve Django model identity during source-only moves;
7. validate note or timer behavior when those invariants change;
8. do not treat pre-existing functional failure as evidence of structural
   refactor failure;
9. do not preserve empty scaffolding without an explainable responsibility;
10. update this contract when ownership, lifecycle, implementation layers, or
    validation rules change.

---

## Next Hansel Breadcrumb

For the authoritative model:

```text
aurora/subsystems/delta_notes/models.py
```

For API behavior:

```text
aurora/subsystems/delta_notes/api/endpoint.py
```

For administration:

```text
aurora/subsystems/delta_notes/admin.py
```

For known technical debt and unresolved behavior:

```text
aurora/subsystems/delta_notes/contracts/TECHNICAL_DEBT.md
```

For the unresolved empty service layer:

```text
aurora/subsystems/delta_notes/services/
```

# ======================================================================
# END: DELTA_NOTES_HANSEL_CONTRACT
# ======================================================================
