# ======================================================================
# FILE: aurora/subsystems/planning/contracts/INITIATIVE_CLOSEOUT.md
# START: PLANNING_INITIATIVE_CLOSEOUT
# ======================================================================

# Initiative Closeout

**Knowledge State: VERIFIED**

**Subsystem:** planning

---

## Purpose

Define the minimum evidence review required before a completed body of
Initiative work is accepted as authoritative engineering history.

Initiative closeout does not replace Planning lifecycle eligibility.

It verifies that the execution history being closed is coherent with the
repository state produced by the Initiative.

---

## Lifecycle Eligibility

Planning lifecycle authority determines whether an Initiative is eligible for
completion.

Normal eligibility requires:

```text
all non-cancelled Phases → COMPLETED
```

Cancelled Phases do not block completion.

The closeout checklist must not duplicate or bypass lifecycle transition rules.

---

## Closeout Checklist

Before human approval of Initiative completion, verify:

### 1. Lifecycle

- Initiative completion evaluation reports the Initiative eligible.
- No non-cancelled Phase remains unfinished.

### 2. Step Validation Evidence

For completed Steps:

- required deterministic validation is represented by the Step's validation
  authority;
- observed validation results are recorded;
- validation attribution is preserved.

Closeout does not invent missing validation after the fact.

Missing evidence is a closeout defect to resolve before approval.

### 3. Actual Repository Impact

For implementation Steps that changed repository files:

- observed repository impacts are recorded as ACTUAL Step files;
- ACTUAL paths describe what was changed rather than what was merely planned.

A Step that legitimately produced no repository file change does not require a
fabricated ACTUAL file record.

### 4. Hansel Reconciliation

Ask:

> Has this Initiative made a Hansel breadcrumb or ownership route stale?

If no, no Hansel mutation is required.

If yes:

- update affected routing to the current authority;
- remove obsolete routing;
- add routing only for durable knowledge destinations;
- verify changed breadcrumbs resolve.

A known broken or stale Hansel route must not be knowingly carried through
Initiative closeout.

### 5. Repository State

Before approval:

- the Initiative's intended repository changes are present;
- disposable validation artifacts are removed;
- the repository passes the validation appropriate to the work;
- the Initiative milestone is represented by a deliberate Git checkpoint.

Git is repository history.

Planning remains lifecycle authority.

---

## Human Approval

Initiative closeout ends with explicit human approval through Planning
lifecycle authority.

The checklist provides evidence for that decision.

It does not directly set Initiative status.

Human approval must not be replaced by arbitrary CRUD mutation.

---

## Reconciliation Failures

If closeout discovers that Planning history and repository reality disagree:

```text
stop
    ↓
identify the discrepancy
    ↓
reconcile the narrowest affected authority
    ↓
validate the correction
    ↓
resume closeout
```

Do not rewrite historical execution evidence merely to make the Initiative
appear complete.

Do not delete useful historical Planning records solely because implementation
evolved beyond the original plan.

---

## Scope

Initiative closeout is intentionally bounded.

It does not require:

- repository-wide rediscovery;
- rewriting every Hansel catalogue;
- speculative documentation;
- fabricated ACTUAL file records;
- retrospective redesign of completed work;
- deletion of historical Planning evidence.

Inspect only the evidence necessary to establish that the completed Initiative
and resulting repository state agree.

---

## Ownership Boundary

Planning owns:

- Initiative lifecycle eligibility;
- Step validation evidence;
- Step file-impact evidence;
- Initiative completion approval;
- reconciliation of Planning history with execution evidence.

Hansel owns:

- breadcrumb and ownership-route integrity;
- Hansel catalogue reconciliation.

Git owns repository history, not Planning lifecycle state.

---

## Validation

This contract is satisfied when an Initiative closeout can deterministically
answer:

1. Is the Initiative lifecycle-eligible for completion?
2. Do completed Steps retain their required validation evidence?
3. Are actual repository impacts recorded where repository files changed?
4. Did the Initiative make Hansel routing stale, and if so, was it reconciled?
5. Does repository state agree with the completed Planning work?
6. Has a human explicitly approved Initiative completion through lifecycle
   authority?

If any required answer is unresolved, closeout is incomplete.

---

## Sufficient Authority

For ordinary Initiative closeout, sufficient authority consists of:

```text
this contract
    +
Planning Initiative lifecycle evaluation
    +
Step validation and ACTUAL file evidence
    +
Hansel catalogue reconciliation rules
    +
task-appropriate repository validation
```

Escalate beyond these authorities only when closeout reveals a concrete
discrepancy.

# ======================================================================
# END: PLANNING_INITIATIVE_CLOSEOUT
# ======================================================================