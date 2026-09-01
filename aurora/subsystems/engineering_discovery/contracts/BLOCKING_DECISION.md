# ======================================================================
# FILE: aurora/subsystems/engineering_discovery/contracts/BLOCKING_DECISION.md
# START: ENGINEERING_DISCOVERY_BLOCKING_DECISION
# ======================================================================

# Engineering Finding Blocking Decision Boundary

**Knowledge State: VERIFIED**

**Subsystem:** engineering_discovery

---

## Purpose

Define the deterministic decision boundary between BLOCKING and NON_BLOCKING
Engineering Findings.

This contract answers one question:

> Can the current authoritative Planning Step be completed correctly and
> validated without resolving this finding?

If yes, the finding is NON_BLOCKING.

If no, the finding is BLOCKING.

This contract does not mutate Planning state or create remedial work. That
integration belongs to later Planning-authorized implementation.

---

## Governing Principle

Blocking classification is about the executability of the **current Step**.

It is not a measure of:

- severity;
- architectural importance;
- cleanup priority;
- urgency;
- technical debt;
- user visibility;
- expected implementation effort.

A serious problem may be NON_BLOCKING if the current Step can still be completed
correctly and validated.

A small problem may be BLOCKING if the current Step cannot proceed correctly
without resolving it.

---

## Authoritative Question

Classify the finding by asking:

```text
Can the lifecycle-authoritative current Step be completed correctly
and validated without resolving this finding?
```

### YES

```text
NON_BLOCKING
```

Persist the finding and continue current work.

### NO

```text
BLOCKING
```

Persist the finding and do not falsely complete the blocked Step.

---

## BLOCKING Conditions

A finding is BLOCKING when continuing the current Step without resolution would
require one or more of the following:

- violating an established subsystem or application boundary;
- inventing an unsupported assumption;
- bypassing repository-owned authority;
- proceeding through invalid Planning or execution state;
- skipping required deterministic validation;
- pretending a broken Hansel breadcrumb or authority surface works;
- knowingly producing an incorrect implementation;
- knowingly closing the Step without satisfying its validation requirement.

The finding need not make all engineering work impossible.

It only needs to prevent **this Step** from being completed correctly and
validated.

---

## NON_BLOCKING Conditions

A finding is NON_BLOCKING when:

- the current Step still has a correct authoritative implementation path;
- required validation can still be performed;
- the finding does not require an ownership or lifecycle violation;
- the finding can be durably preserved for later reconciliation;
- continuing current work does not falsify evidence or state.

NON_BLOCKING does not mean unimportant.

It means resolution is not required for correct completion of the current Step.

---

## Classification Timing

Classify immediately after a condition qualifies as an Engineering Finding.

The sequence is:

```text
problem encountered
    ↓
finding qualification
    ↓
blocking decision
    ↓
persist finding
    ↓
BLOCKING: route into remedial current work
NON_BLOCKING: continue current Step
```

Do not postpone blocking classification until Initiative closeout.

The purpose of classification is to determine whether current work may proceed.

---

## Classification Changes

Blocking classification may change only when new execution evidence changes the
answer to the authoritative question.

Examples:

- A workaround is discovered that is repository-authorized and fully
  validatable. A BLOCKING finding may become NON_BLOCKING.
- New evidence shows the apparent workaround violates an ownership boundary. A
  NON_BLOCKING finding may become BLOCKING.

A classification change must preserve the original finding provenance and
supporting evidence.

Do not reclassify merely because priorities changed.

---

## Relationship to Resolution State

Blocking classification and resolution state are independent dimensions.

Valid combinations include:

```text
BLOCKING + UNRESOLVED
NON_BLOCKING + UNRESOLVED
BLOCKING + RESOLVED
NON_BLOCKING + RESOLVED
```

Once a BLOCKING finding is resolved, the current Step may become executable
again.

Resolution does not erase the historical fact that the finding blocked work.

---

## Relationship to Planning

Engineering Discovery owns the blocking decision semantics.

Planning owns executable work and lifecycle mutation.

Therefore:

```text
Engineering Discovery
    decides whether the finding blocks current work

Planning
    owns any change to Initiative / Phase / Step execution state
```

Engineering Discovery must not directly create, activate, pause, reorder, or
complete Planning objects merely because a finding is BLOCKING.

The controlled workflow that introduces remedial work into the current
Initiative belongs to the next implementation Step.

---

## BLOCKING Examples

### Broken required authority

The current Step requires a repository-owned contract.

The Hansel breadcrumb points to a missing file and there is no alternative
authoritative route.

The Step cannot be completed without inventing authority.

```text
BLOCKING
```

### Required boundary would be violated

The current Step needs data from another subsystem.

The only discovered implementation path would directly mutate that subsystem's
ORM objects while an application boundary is required.

No authorized interface exists.

```text
BLOCKING
```

### Required validation is impossible

The implementation can be written, but the Step's required deterministic
validation cannot be performed because the validation surface is missing or
broken.

```text
BLOCKING
```

---

## NON_BLOCKING Examples

### General capability in an awkward location

The current Step needs a Planning executable-work resolver.

The resolver exists, works correctly, and is authoritative, but lives under a
narrower time-tracking module.

The Step can still use it correctly and validate the result.

```text
NON_BLOCKING
```

### Nearby subsystem has architectural debt

Required work reveals that another subsystem persists directly through an HTTP
endpoint.

The current Engineering Discovery Step does not depend on that mutation path.

```text
NON_BLOCKING
```

### Missing structured historical evidence

Current work reveals that prior Steps did not maintain an existing structured
actual-files mechanism.

The current Step can still be completed correctly while the omission is
preserved for later remediation.

```text
NON_BLOCKING
```

---

## Worker Decision Checklist

Before assigning BLOCKING, verify:

```text
[ ] The finding already passed Engineering Finding qualification.
[ ] The problem affects the lifecycle-authoritative current Step.
[ ] Correct implementation or deterministic validation cannot proceed without
    resolving it.
[ ] Continuing would require an invalid assumption, boundary bypass, false
    evidence, or unsatisfied validation.
```

If these are not all true, classify NON_BLOCKING.

---

## Step 331 Acceptance Condition

A clean-context worker must be able to distinguish:

- finding qualification from blocking classification;
- severity from executability;
- NON_BLOCKING deferral from dismissal;
- BLOCKING status from Planning lifecycle mutation;
- finding resolution from historical blocking classification.

The worker must know exactly when current work may continue and when it must not
be falsely completed.

# ======================================================================
# END: ENGINEERING_DISCOVERY_BLOCKING_DECISION
# ======================================================================
