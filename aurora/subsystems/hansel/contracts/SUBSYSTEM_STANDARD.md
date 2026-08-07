<!-- ====================================================================== -->
<!-- FILE: aurora/subsystems/hansel/contracts/SUBSYSTEM_STANDARD.md -->
<!-- START: HANSEL_SUBSYSTEM_STANDARD -->
<!-- ====================================================================== -->

# Hansel Subsystem Standard

## Purpose

Hansel defines the repository-owned human and machine workflow used to make
Aurora subsystems self-discoverable.

Its objective is to eliminate repeated repository-wide searches for ownership,
runtime entry points, interfaces, dependencies, architectural decisions,
validation requirements, and the next authoritative source.

## Core Rule

Every subsystem must publish its minimum Hansel contracts when the subsystem is
created. The contracts may initially contain UNKNOWN or PLANNED information,
but the files themselves must exist from the beginning and be updated as the
architecture evolves.

## Required Subsystem Structure

Every subsystem must contain:

```text
<subsystem>/
    README.md

    contracts/
        SUBSYSTEM.md
        RUNTIME.md
        INTERFACES.md
        DEPENDENCIES.md
        DECISIONS.md
        VALIDATION.md
```

Optional contracts include:

- MIGRATION_PLAN.md
- SECURITY.md
- DATA_MODEL.md
- OPERATIONS.md

## Required Contract Responsibilities

### README.md
- Entry point for humans and AI.
- Identifies the subsystem.
- Points to `contracts/SUBSYSTEM.md`.

### SUBSYSTEM.md
Defines:
- purpose;
- ownership boundary;
- responsibilities;
- excluded responsibilities;
- implementation state;
- next Hansel breadcrumb.

### RUNTIME.md
Defines:
- initialization;
- execution flow;
- state transitions;
- shutdown;
- runtime validation.

### INTERFACES.md
Defines:
- public APIs;
- browser events;
- globals;
- commands;
- models;
- schemas;
- inputs and outputs.

### DEPENDENCIES.md
Defines:
- owned components;
- shared Aurora services;
- external dependencies;
- configuration;
- environment requirements.

### DECISIONS.md
Records architectural decisions, rationale, alternatives, and superseding
decisions.

### VALIDATION.md
Defines deterministic validation procedures, regression boundaries, rollback
requirements, and supported workflows.

## Knowledge States

Every statement must explicitly be one of:

```text
VERIFIED
PLANNED
UNKNOWN
DEFERRED
DEPRECATED
```

Unknowns must identify the next breadcrumb needed to resolve them.

## Evidence Rule

Never present assumptions as verified facts.

When verified knowledge ends:

1. Stop.
2. Record the unknown.
3. Record the narrowest next breadcrumb.
4. Continue discovery only from that authority.

## Breadcrumb Rule

Every contract ends with:

```
Next Hansel Breadcrumb
```

The breadcrumb must identify:

- the next contract,
- the exact repository file,
- the exact function/class/model,
- or the deterministic validation step.

Avoid repository-wide searches once an authority has been identified.

## Empty Contract Rule

Required contracts may begin mostly empty, but never blank.

Each must state:

- its purpose;
- current knowledge state;
- known facts;
- unknowns;
- update trigger.

## Update Rule

Architecture work is incomplete until affected Hansel contracts are updated.

## Anchor Rule

All contracts use complete anchored replacement regions with matching FILE,
START, and END markers.

## Delivery Rule

Large repository documents may be delivered as downloadable artifacts to
guarantee completeness.

## Success Condition

Hansel succeeds when a new human or AI can determine:

- where to begin;
- what owns the behavior;
- how it executes;
- what can be safely changed;
- how to validate changes;
- where to go next;

without another repository-wide "snipe hunt."

## Next Hansel Breadcrumb

Create canonical templates under:

```text
aurora/subsystems/hansel/templates/subsystem_contracts/
```

for:

- README.md
- SUBSYSTEM.md
- RUNTIME.md
- INTERFACES.md
- DEPENDENCIES.md
- DECISIONS.md
- VALIDATION.md

<!-- ====================================================================== -->
<!-- FILE: aurora/subsystems/hansel/contracts/SUBSYSTEM_STANDARD.md -->
<!-- END: HANSEL_SUBSYSTEM_STANDARD -->
<!-- ====================================================================== -->
