# ======================================================================
# FILE: aurora/subsystems/anamod/contracts/TECHNICAL_DEBT.md
# START: ANAMOD_TECHNICAL_DEBT
# ======================================================================

# Anamod Technical Debt

This document records known defects and intentional architectural debt that
are outside the scope of the current migration.

Only verified issues belong here.

---

# Active Defects

## Monaco Worker Configuration

Status: ACTIVE

The Monaco editor falls back to executing worker code on the main thread.

Impact:

- Console errors are generated.
- Editor performance may degrade.

Current policy:

Deferred until the workspace migration is complete.

---

## Monaco Python Linter

Status: ACTIVE

Python diagnostics no longer appear inside Monaco.

Observed impact:

- Missing imports are not detected during editing.
- Runtime failures reach Django before they are discovered.

Current policy:

Every Python change must be validated independently of Monaco.

Deferred until the workspace migration is complete.

---

# Deferred Features

## Sandbox Execution

Status: DEFERRED

The sandbox feature has never been production-ready.

Current policy:

Ignore during the current migration.

---

# Architectural Debt

None currently recorded.

# ======================================================================
# END: ANAMOD_TECHNICAL_DEBT
# ======================================================================