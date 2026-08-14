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

It owns the planning data and workflows used to define, organize, estimate,
validate, import, export, and track that work.

Planning does not own repository discovery, AI execution, or execution
orchestration.

---

## Knowledge Catalogue

### Understand or change planning data

Go to:

```text
aurora/subsystems/planning/models.py
```

### Understand Planning lifecycle and reconciliation

Go to:

```text
aurora/subsystems/planning/contracts/LIFECYCLE_AND_RECONCILIATION.md
```

Use this authority for:

- execution-state transitions;
- active-work rules;
- pause and resume semantics;
- assignment and historical attribution;
- Planning reconciliation;
- Planning and Engineering Session boundaries.

### Understand or change Planning CRUD/API behavior

Start at:

```text
aurora/subsystems/planning/api/endpoint.py
```

Then follow the narrowest relevant module under:

```text
aurora/subsystems/planning/api/
```

### Import, export, or update structured plans

Go to:

```text
aurora/subsystems/planning/io/
```

### Generate an import-ready planning dictionary

Go to:

```text
aurora/subsystems/planning/contracts/PLANNING_DICTIONARY_GENERATION.md
```

### Understand or change the Planning Console UI

Go to:

```text
aurora/subsystems/planning/contracts/UI_MAP.md
```

### Understand or change Planning administration

Go to:

```text
aurora/subsystems/planning/admin.py
```

---

## Unknown Territory

If the task is not covered by this catalogue:

1. do not infer ownership or behavior;
2. inspect the immediate subsystem structure for the narrowest likely authority;
3. if framework-owned surfaces may contain the missing authority, perform the
   narrowest repository discovery needed to locate it;
4. request additional repository evidence only when required;
5. add a new Hansel breadcrumb only if discovery reveals a durable knowledge
   destination that future workers should not have to rediscover.

---

## Sufficient Authority

Stop following Hansel breadcrumbs when all four are known:

1. who owns the behavior;
2. what must change;
3. what must remain unchanged;
4. how the change will be validated.

Do not continue loading context merely because more documentation or source
files exist.

A breadcrumb must reduce uncertainty, establish missing authority, or define
validation. Otherwise, do not follow it.

---

## Authority Reconciliation

After completing a change, ask:

> Has this change made any breadcrumb, ownership statement, or routing decision
> in this `HANSEL.md` stale or non-authoritative?

If no, no Hansel update is required.

If yes:

1. update `HANSEL.md` to point to the new authority;
2. remove obsolete breadcrumbs;
3. add a new breadcrumb only when the change created a genuine new knowledge
   destination;
4. verify every changed breadcrumb resolves to an existing authority.

Do not expand `HANSEL.md` with implementation details discovered during the
work.

The objective is to keep the catalogue accurate, not to record everything
learned.

# ======================================================================
# END: PLANNING_HANSEL_CATALOGUE
# ======================================================================