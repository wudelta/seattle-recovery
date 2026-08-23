# ======================================================================
# FILE: aurora/subsystems/<subsystem>/contracts/HANSEL.md
# START: <SUBSYSTEM>_HANSEL_CONTRACT
# ======================================================================

# <Subsystem> Hansel Catalogue

**Knowledge State: VERIFIED**

**Subsystem:** <subsystem>

---

## Purpose

<Describe the responsibility this subsystem owns in one concise paragraph.>

This catalogue routes workers to the smallest repository authority needed for
work owned by this subsystem.

---

## Knowledge Catalogue

### <Task or responsibility>

Go to:

```text
<repository authority>
```

Use this authority when <state the narrow reason a worker needs it>.

---

## Unknown Territory

If the catalogue does not identify sufficient authority for the task:

1. do not invent ownership, behavior, or architecture;
2. inspect the narrowest likely repository authority;
3. follow cross-boundary dependencies only when required;
4. request additional repository evidence when necessary;
5. add a breadcrumb only when discovery reveals a durable route a future
   worker should not need to rediscover.

---

## Sufficient Authority

Stop following breadcrumbs when all four are known:

1. who owns the behavior;
2. what must change;
3. what must remain unchanged;
4. how the change will be validated.

Do not load neighboring knowledge merely because it exists.

---

## Catalogue Reconciliation

After completing work, ask:

> Has this change made a Hansel breadcrumb or ownership route stale?

If no, no Hansel change is required.

If yes:

1. update affected breadcrumbs to current durable authorities;
2. remove obsolete routing;
3. add routing only for durable knowledge destinations;
4. verify changed breadcrumbs resolve.

Do not expand this catalogue with implementation knowledge learned during the
task.

The objective is accurate navigation.

---

# ======================================================================
# END: <SUBSYSTEM>_HANSEL_CONTRACT
# ======================================================================