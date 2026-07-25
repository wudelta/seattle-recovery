# Aurora Patch Safety Kernel

**Version: 3.0**

---

# Purpose

The Patch Safety Kernel defines the minimum engineering rules that apply to every Aurora implementation session.

It is intentionally concise so it can be loaded at the beginning of development without significant context overhead.

The Safety Kernel exists to answer one question:

> **"How do we avoid delivering a bad implementation?"**

---

# 1. Human-Safe Editing

The objective of every implementation is to minimize opportunities for both AI mistakes and human editing mistakes.

Whenever practical:

* replace complete architectural units;
* avoid manual merging;
* eliminate partial edits;
* provide deterministic copy-and-paste replacements.

The safest implementation is the smallest complete replacement unit—not necessarily the implementation with the fewest changed lines.

---

# 2. Architectural Replacement Units

Every delivery should represent one cohesive architectural responsibility.

Examples include:

* one complete anchored region;
* one complete function;
* one complete class;
* one API endpoint;
* one JavaScript module;
* one template component;
* one documentation section;
* one complete file.

Do not split a logical implementation simply to satisfy an arbitrary size preference.

Architecture determines replacement boundaries.

---

# 3. Complete Replacement Rule

Every replacement unit must be complete.

A replacement must:

* preserve all unchanged content within its boundaries;
* include every remaining implementation element belonging to that unit;
* remain syntactically complete;
* require no manual merging;
* be immediately usable as delivered.

Never deliver only changed lines from a replacement unit.

---

# 4. Inspect Before Modifying

Never generate a replacement for code that has not been inspected.

Before implementation:

* verify the repository-relative file path;
* inspect the current source;
* understand the surrounding implementation;
* identify the intended modification.

Never invent unseen code.

When uncertainty exists, request the current source before proceeding.

---

# 5. Anchor Format

Anchored replacement units use:

```text
FILE:
START:
END:
```

The `FILE:` path is the authoritative source identifying the artifact being modified.

Patch numbering is no longer part of the protocol.

---

# 6. Symbol Preservation

Before delivering a replacement, account for every implementation element contained within the replacement unit.

Examples include:

* imports;
* constants;
* decorators;
* classes;
* methods;
* functions;
* configuration;
* exported symbols;
* docstrings;
* comments carrying engineering meaning.

Any omitted implementation element must be intentionally removed.

Unexplained omissions are considered implementation failures.

---

# 7. Deterministic Delivery

Each delivery performs exactly one deterministic editing operation.

Examples include:

* replace one anchored region;
* create one complete file;
* delete one file;
* rename one file.

The required editing operation should never require interpretation.

---

# 8. Validate Before Continuing

After every implementation:

1. perform the smallest deterministic validation capable of confirming the intended change;
2. review the result;
3. stop;
4. continue only after explicit approval.

A successful syntax check confirms only structural correctness.

Behavioral validation confirms the engineering objective has been achieved.

Both are required before implementation is considered complete.

---

# 8.1 Validation Matrix

Whenever practical, perform deterministic validation before behavioral testing.

| Artifact           | Deterministic Validation                               | Behavioral Validation                                                  |
| ------------------ | ------------------------------------------------------ | ---------------------------------------------------------------------- |
| Python             | `daurora-check`                                        | Exercise the affected endpoint, API, command, or workflow.             |
| JavaScript         | `djscheck`                                             | Exercise the affected browser interaction or UI workflow.              |
| Django Template    | `daurora-check`                                        | Render the affected page or panel and verify expected behavior.        |
| Database Migration | `dmakemigrations` (when applicable), `daurora-migrate` | Verify schema changes and affected CRUD operations.                    |
| Documentation      | Markdown rendering or structural review                | Human review for clarity, completeness, and architectural correctness. |

---

# 9. The GO Loop

Every implementation follows the same review cycle.

```text
Inspect
    ↓
Design
    ↓
Deliver One Complete Replacement Unit
    ↓
Validate
    ↓
Review
    ↓
GO
```

Do not skip review cycles.

Frequent validation and small recovery points are fundamental engineering practices.

---

# 9.1 One Replacement Unit Rule

Unless explicitly requested otherwise:

* deliver one complete replacement unit;
* stop;
* wait for **go** before continuing.

This minimizes rollback scope and keeps every implementation independently reviewable.

---

# 10. Final Pre-Delivery Checklist

Before delivering any implementation, confirm:

□ The correct file has been inspected.

□ The repository-relative path is correct.

□ The `FILE:` path is correct.

□ The `START:` anchor matches.

□ The `END:` anchor matches.

□ The replacement boundary is correct.

□ Every existing implementation element has been accounted for.

□ The replacement unit is complete.

□ No manual merge is required.

□ The implementation is syntactically valid.

□ The required deterministic validation has been identified.

□ The required behavioral validation has been identified.

If any item cannot be confidently answered, stop and resolve the uncertainty before delivering the implementation.

---

# Governing Rule

When simplicity, speed, or convenience conflict with safety, choose safety.

A complete, deterministic, reviewable replacement unit is always preferable to a faster implementation that depends on manual editing, assumptions, or incomplete context.

The Safety Kernel exists to prevent implementation mistakes before they reach the repository.
