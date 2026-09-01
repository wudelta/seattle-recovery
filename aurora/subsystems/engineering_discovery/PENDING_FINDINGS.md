# ======================================================================
# FILE: aurora/subsystems/engineering_discovery/PENDING_FINDINGS.md
# START: ENGINEERING_DISCOVERY_PENDING_FINDINGS
# ======================================================================

# Pending Engineering Findings

**Status:** TEMPORARY / NON-AUTHORITATIVE

## Purpose

Preserve concrete Engineering Finding candidates encountered while implementing
the Engineering Discovery Initiative before the bounded finding-submission and
persistence mechanism exists.

This file is a temporary transport ledger, not an Engineering Discovery
authority and not the future system of record.

Each entry must be submitted through the authoritative Engineering Discovery
submission mechanism once that mechanism exists. After all entries have been
successfully persisted and verified, delete this file.

Do not add speculative findings or repository-wide defect discoveries here.

---

## Finding 1 — Wu Chat Reconstructs Planning Execution State

**Provisional category:** BOUNDARY_VIOLATION  
**Provisional classification:** NON_BLOCKING  
**Provisional resolution state:** UNRESOLVED

### Observed condition

`aurora/subsystems/wu_chat/services/execution_context.py` independently queries
Planning Initiative, Phase, and Step models to reconstruct the ACTIVE execution
hierarchy for the user.

### Evidence

`ExecutionContextResolver.build()` directly reads Planning ORM models rather
than consuming a Planning-owned executable-work resolver.

By comparison,
`aurora/subsystems/engineering_session/services/status.py` obtains current
lifecycle-authoritative work through Planning's executable-work service and
derives the parent hierarchy from the returned Step.

### Why this qualifies

Wu Chat duplicates interpretation of lifecycle-authoritative Planning state
across a subsystem boundary.

### Why it is non-blocking

Engineering Discovery can obtain current work through existing Planning
authority without depending on Wu Chat's resolver.

### Required handling

Preserve for later deliberate remediation. Do not repair opportunistically
during the current capture/persistence work.

---

## Finding 2 — Structured Actual-File Evidence Is Not Maintained During Work

**Provisional category:** NEEDED_SOLUTION  
**Provisional classification:** NON_BLOCKING  
**Provisional resolution state:** UNRESOLVED

### Observed condition

Engineering Discovery Steps created and modified repository files, but the
existing structured Step actual-files-created / actual-files-mutated mechanism
was not updated during execution.

The paths were instead recorded manually in free-form Step validation notes.

### Evidence

This occurred during multiple Steps of the current Engineering Discovery
Initiative, including the work that created or modified Engineering Discovery
contracts and subsystem scaffold files.

### Why this qualifies

The repeated manual reconstruction demonstrates a missing deterministic workflow
for maintaining structured execution evidence that Aurora already intends to
own as structured state.

### Why it is non-blocking

The current implementation Steps can still be completed and validated, but
structured durable evidence is incomplete unless manually reconciled.

### Required handling

Preserve for later remediation through the owning Step-evidence mechanism.
Engineering Discovery does not automatically become the owner of actual-file
tracking.

---

## Migration Rule

When an authoritative Engineering Discovery persistence/submission mechanism is
available:

1. submit a still-valid entry through the live current-work mechanism only when
   its true originating Step is the lifecycle-authoritative ACTIVE Step;
2. never attribute an older finding to a later ACTIVE Step merely to move it
   into persistence;
3. retain historical pending entries until an explicit historical-ingest path
   can preserve their original Planning provenance without trusting arbitrary
   caller-supplied identifiers;
4. verify each persisted finding;
5. do not silently convert provisional classifications into authoritative values
   without validation;
6. remove an entry from this temporary ledger only after successful persistence
   and verification;
7. delete this file when no pending entries remain.

# ======================================================================
# END: ENGINEERING_DISCOVERY_PENDING_FINDINGS
# ======================================================================
