# ======================================================================
# FILE: aurora/subsystems/hansel/contracts/HANSEL.md
# START: HANSEL_HANSEL_CONTRACT
# ======================================================================

# Hansel — Repository Knowledge Catalogue

## Purpose

Hansel is Aurora's repository-owned navigation system.

Its purpose is to move a worker from:

```text
task
    ↓
owning authority
    ↓
task-specific authority
    ↓
sufficient context
    ↓
work
    ↓
validation
```

Hansel is an index, not an encyclopedia.

It should provide the smallest useful breadcrumb needed to continue discovery.

Do not load repository knowledge merely because it exists.

---

## Start Here

Given a task:

1. identify the repository authority most likely to own the requested behavior;
2. if a subsystem owns it, go to that subsystem's canonical Hansel catalogue:

```text
aurora/subsystems/<subsystem>/contracts/HANSEL.md
```

3. if Hansel identifies a direct application-level authority, go directly to
   that destination;
4. follow the narrowest breadcrumb relevant to the task;
5. continue only while additional authority is required.

Do not begin with repository-wide discovery when an existing Hansel breadcrumb
can identify the next authority.

---

## Authority Catalogue

### Subsystem-Owned Behavior

Canonical subsystem Hansel entry points live at:

```text
aurora/subsystems/*/contracts/HANSEL.md
```

Examples include:

```text
aurora/subsystems/planning/contracts/HANSEL.md
aurora/subsystems/delta_directives/contracts/HANSEL.md
aurora/subsystems/delta_notes/contracts/HANSEL.md
aurora/subsystems/hansel/contracts/HANSEL.md
```

A subsystem catalogue should route a task to the narrowest authoritative source
needed for that work.

It should not duplicate the implementation or architectural knowledge available
at that destination.

### Aurora Application Access Control

Go to:

```text
aurora/access/
```

Use this authority when the task concerns who may enter or use Aurora.

Do not infer Django administration permissions from Aurora access policy.

---

## When Ownership Is Unclear

If the task does not clearly identify an owning authority:

1. perform the narrowest repository discovery necessary to identify likely
   ownership;
2. prefer repository structure and existing Hansel breadcrumbs over inference;
3. enter the discovered authority through its narrowest canonical entry point;
4. continue from that authority.

Do not perform broad repository discovery merely to accumulate context.

---

## When a Breadcrumb Fails

A breadcrumb that does not resolve is a Hansel defect.

A breadcrumb is broken when its referenced authority:

- does not exist;
- cannot be resolved;
- no longer owns the stated responsibility;
- or routes the worker to stale or non-authoritative knowledge.

When a broken breadcrumb is encountered:

1. stop treating that breadcrumb as authoritative;
2. perform the narrowest discovery necessary to recover the durable authority;
3. continue the immediate task only with evidence from that recovered authority;
4. repair or replace the broken breadcrumb;
5. if the breadcrumb correctly names a durable contract that is missing, create
   that contract;
6. validate that the repaired breadcrumb resolves;
7. do not consider the task complete while a known broken breadcrumb remains.

Do not merely work around a broken breadcrumb and leave it for another worker
to rediscover.

If a catalogue does not contain a breadcrumb for the task at all:

1. do not invent ownership, behavior, or architecture;
2. inspect the narrowest likely authority;
3. follow cross-boundary dependencies only when the task requires them;
4. request additional repository evidence when necessary;
5. add a new breadcrumb only when discovery reveals a durable route that a
   future worker should not have to rediscover.
   
---

## Cross-Boundary Work

A task may begin in one authority and reveal work owned by another.

When this happens:

```text
current authority
    ↓
dependency or ownership boundary discovered
    ↓
owning authority
    ↓
continue discovery
```

If the new owner is a subsystem, enter through its `contracts/HANSEL.md`.

If Hansel identifies a direct application-level authority, go directly to that
authority.

Do not preload neighboring knowledge in anticipation of possible dependencies.

Discover it when the task crosses the boundary.

---

## Sufficient Authority

Stop following Hansel breadcrumbs when all four are known:

1. who owns the behavior;
2. what must change;
3. what must remain unchanged;
4. how the change will be validated.

A breadcrumb must reduce uncertainty, establish missing authority, or define
validation.

Otherwise, do not follow it.

---

## Working on Hansel

To create, evaluate, or change subsystem Hansel catalogues, go to:

```text
aurora/subsystems/hansel/contracts/SUBSYSTEM_STANDARD.md
```

To inspect Hansel validation implementation, go to:

```text
aurora/subsystems/hansel/validators/
```

These sources are task-specific deeper authorities.

They are not required context for ordinary repository work.

---

## Catalogue Reconciliation

After completing work, ask:

> Has this change made a Hansel breadcrumb or ownership route stale?

If no, no Hansel change is required.

If yes:

1. update the affected catalogue to point to the current authority;
2. remove obsolete routing;
3. add new routing only when a durable knowledge destination was created;
4. verify changed breadcrumbs resolve to real repository authorities.

Do not expand Hansel catalogues with implementation knowledge learned during the
task.

The objective is accurate navigation.

# ======================================================================
# END: HANSEL_HANSEL_CONTRACT
# ======================================================================
