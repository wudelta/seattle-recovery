# ======================================================================
# FILE: aurora/subsystems/hansel/contracts/SUBSYSTEM_GENERATOR.md
# START: HANSEL_SUBSYSTEM_GENERATOR_CONTRACT
# ======================================================================

# Hansel Subsystem Generator Contract

**Knowledge State: VERIFIED**

**Subsystem:** hansel

---

## Purpose

Define the deterministic contract for creating the minimum repository scaffold
of a new Aurora subsystem.

The generator exists to ensure that every newly created subsystem begins with
a valid Hansel entry point without generating speculative architecture.

---

## Canonical Command

The repository-owned generator is exposed as:

```text
python manage.py create_subsystem <subsystem>
```

The management command is a thin interface over Hansel-owned deterministic
generation logic.

---

## Input

The generator accepts exactly one subsystem identifier.

The identifier:

- is required;
- uses lowercase snake_case;
- begins with a lowercase ASCII letter;
- contains only lowercase ASCII letters, digits, and underscores;
- must not contain path separators;
- must not contain `.` or `..`;
- must identify exactly one direct child of `aurora/subsystems/`.

Examples:

```text
valid_subsystem
resource_discovery
planning2
```

Invalid examples:

```text
ValidSubsystem
valid-subsystem
../planning
planning/contracts
```

---

## Destination

For subsystem `<subsystem>`, the canonical destination is:

```text
aurora/subsystems/<subsystem>/
```

The minimum generated scaffold is:

```text
aurora/subsystems/<subsystem>/
    __init__.py
    contracts/
        __init__.py
        HANSEL.md
```

No other directories or implementation files are generated automatically.

In particular, the generator does not speculate that a subsystem requires:

- models;
- APIs;
- services;
- templates;
- static assets;
- validators;
- admin integration;
- management commands;
- additional contracts.

Those authorities are created only when real subsystem responsibilities
require them.

---

## Template Authority

The only canonical Hansel contract template is:

```text
aurora/subsystems/hansel/templates/subsystem_contracts/HANSEL.md
```

The generator must read this repository-owned template.

It must not contain an independent embedded copy of the scaffold.

---

## Deterministic Substitution

Generation replaces these template placeholders:

```text
<subsystem>
<Subsystem>
<SUBSYSTEM>
```

Their meanings are:

```text
<subsystem>
    exact validated lowercase snake_case identifier

<Subsystem>
    human-readable title derived deterministically from the identifier

<SUBSYSTEM>
    uppercase identifier used by repository anchors
```

For example:

```text
resource_discovery

<subsystem> = resource_discovery
<Subsystem> = Resource Discovery
<SUBSYSTEM> = RESOURCE_DISCOVERY
```

No AI generation or semantic inference participates in substitution.

---

## Preflight

Before any filesystem mutation, the generator must verify:

1. the subsystem identifier is valid;
2. `aurora/subsystems/` exists;
3. the canonical template exists and is readable;
4. the destination subsystem path does not already exist;
5. every planned destination remains beneath `aurora/subsystems/`;
6. all required template placeholders are present.

Any failed preflight condition stops generation before mutation.

---

## Dry Run

The generator supports:

```text
--dry-run
```

Dry run performs complete preflight and rendering.

It reports the exact directories and files that would be created.

It performs no filesystem mutation.

A successful dry run must therefore leave repository state unchanged.

---

## Apply

Without `--dry-run`, generation may proceed only after successful preflight.

Apply creates exactly the approved minimum scaffold.

The generator must never overwrite an existing file or directory.

Existing destination state is a collision, not an update request.

---

## Atomic Failure

Generation is all-or-nothing from the repository's perspective.

If generation fails after filesystem mutation begins, the generator must remove
only paths created by that invocation.

It must never remove or modify repository state that existed before the
invocation.

A failed generation must not leave a partial subsystem scaffold.

---

## Validation

Before generation is considered successful, the rendered subsystem must pass
deterministic Hansel validation.

Validation must prove at minimum:

1. the generated `contracts/HANSEL.md` exists;
2. its FILE anchor matches its canonical repository path;
3. its declared subsystem identity matches the generated subsystem;
4. required Hansel concerns are present;
5. deterministic repository breadcrumbs resolve.

Validation failure makes the generation unsuccessful and triggers atomic
cleanup of newly created paths.

---

## Refusal Conditions

The generator must refuse to proceed when:

- the identifier is invalid;
- the destination already exists;
- the template is missing or unreadable;
- required placeholders are missing;
- a destination escapes `aurora/subsystems/`;
- a filesystem collision occurs;
- generated Hansel validation fails;
- generation cannot complete atomically.

The generator does not repair, merge, update, or overwrite existing
subsystems.

---

## Ownership Boundary

Hansel owns:

- the subsystem scaffold contract;
- the canonical Hansel template;
- deterministic scaffold generation;
- generated Hansel validation.

The management command owns only CLI argument handling and presentation of
generator results.

Component Registry reconciliation, repository documentation, and other
post-generation repository intelligence remain owned by their respective
subsystems.

---

## Sufficient Authority

Implementation of `create_subsystem` has sufficient authority when the worker
knows:

1. this generator contract;
2. the canonical Hansel template;
3. the deterministic Hansel validator interface;
4. Aurora management-command conventions.

No neighboring subsystem implementation should be loaded unless a concrete
dependency requires it.

---

# ======================================================================
# END: HANSEL_SUBSYSTEM_GENERATOR_CONTRACT
# ======================================================================