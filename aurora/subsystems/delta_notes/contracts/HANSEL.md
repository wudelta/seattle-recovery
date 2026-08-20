# ======================================================================
# FILE: aurora/subsystems/delta_notes/contracts/HANSEL.md
# START: DELTA_NOTES_HANSEL_CONTRACT
# ======================================================================

# Delta Notes — Hansel Catalogue

## Purpose

Delta Notes owns Aurora's lightweight persistent Post-it note workflow.

Its current responsibility is limited to:

```text
create
display
edit
delete
```

Delta Notes does not own structured Planning work.

---

## Knowledge Catalogue

### Understand or change persisted Delta Notes data

Go to:

```text
aurora/subsystems/delta_notes/models.py
```

### Understand or change Delta Notes CRUD/API behavior

Go to:

```text
aurora/subsystems/delta_notes/api/endpoint.py
```

### Understand or change the Delta Notes UI

Go to:

```text
aurora/subsystems/delta_notes/contracts/UI_MAP.md
```

### Investigate known broken or legacy Delta Notes behavior

Go to:

```text
aurora/subsystems/delta_notes/contracts/TECHNICAL_DEBT.md
```

### Understand or change Delta Notes administration

Go to:

```text
aurora/subsystems/delta_notes/admin.py
```

---

## Unknown Territory

If the task is not covered by this catalogue:

1. do not infer ownership or behavior;
2. inspect the immediate Delta Notes subsystem structure for the narrowest
   likely authority;
3. if framework-owned surfaces may contain the missing authority, perform the
   narrowest repository discovery necessary;
4. follow another subsystem's `HANSEL.md` when the task crosses an ownership
   boundary;
5. add a new breadcrumb only when discovery reveals a durable knowledge
   destination future workers should not have to rediscover.

---

## Sufficient Authority

Stop following breadcrumbs when all four are known:

1. who owns the behavior;
2. what must change;
3. what must remain unchanged;
4. how the change will be validated.

Do not continue loading Delta Notes context merely because additional
documentation or source files exist.

---

## Catalogue Reconciliation

After completing a change, ask:

> Has this change made a Delta Notes breadcrumb or ownership route stale?

If no, no Hansel update is required.

If yes:

1. update the affected breadcrumb;
2. remove obsolete routing;
3. add new routing only for durable knowledge destinations;
4. verify changed breadcrumbs resolve to existing authorities.

Do not add implementation detail to this catalogue.

The objective is accurate navigation.

# ======================================================================
# END: DELTA_NOTES_HANSEL_CONTRACT
# ======================================================================
