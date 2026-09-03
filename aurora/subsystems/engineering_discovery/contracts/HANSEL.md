# ======================================================================
# FILE: aurora/subsystems/engineering_discovery/contracts/HANSEL.md
# START: ENGINEERING_DISCOVERY_HANSEL_CONTRACT
# ======================================================================

# Engineering Discovery Hansel Catalogue

**Knowledge State: VERIFIED**

**Subsystem:** engineering_discovery

---

## Purpose

Engineering Discovery owns the durable definition and handling of concrete
engineering findings encountered while performing authoritative engineering work
or workflow execution.

An Engineering Finding records an observable problem exposed by real execution
of an authoritative engineering path when that problem has significance beyond
ordinary successful execution evidence.

This subsystem exists to preserve need-driven engineering feedback without
turning implementation work into speculative repository review.

This catalogue routes workers to the smallest repository authority needed for
Engineering Discovery work.

---

## Ownership Boundary

Engineering Discovery owns:

- the definition of an Engineering Finding;
- qualification and exclusion rules for findings;
- finding categories;
- the boundary between findings and ordinary implementation evidence;
- the boundary between findings and human-entered Delta Notes;
- finding provenance, lifecycle, persistence, and closeout evidence surfaces;
- finding qualification before remedial Planning integration.

Engineering Discovery does not own:

- the current executable Planning hierarchy;
- Planning lifecycle transitions;
- repository navigation generally;
- Hansel breadcrumb ownership;
- ordinary Step implementation evidence;
- human-entered ad-hoc notes;
- speculative architecture review;
- backlog ideation;
- generalized technical-debt discovery;
- engineering-efficiency measurement or scoring.

Planning owns work once a finding is deliberately incorporated into the
persisted Project → Initiative → Phase → Step hierarchy.

Hansel owns repository navigation and breadcrumb integrity.

Delta Notes remains the human-entered ad-hoc mechanism for items a person wants
to preserve outside the Engineering Finding contract.

---

## Engineering Finding Definition

An **Engineering Finding** is a concrete engineering problem encountered while
performing authoritative engineering work or workflow execution, supported by
observable evidence, whose significance extends beyond merely documenting
successful execution.

An executable Planning Step is useful situational provenance when one exists,
but it is not required for the finding itself to qualify.

A finding may be blocking or non-blocking.

Blocking status is not part of finding qualification. A valid finding may allow
the current authoritative work to continue and still require later disposition.

---

## Qualification Rule

A worker may record an Engineering Finding only when all of the following are
true:

1. the condition was encountered while following the authoritative path needed
   for the worker's current assigned work;
2. the condition is supported by directly observable repository or execution
   evidence;
3. the condition represents a concrete engineering problem rather than a
   preference, idea, prediction, or generalized best-practice recommendation;
4. the condition has significance beyond ordinary evidence that the current
   authoritative work or workflow executed and validated successfully.

A worker must not search outside the required implementation path for examples
of finding categories.

Engineering Discovery is a capture mechanism for problems exposed by needed
work, not a mandate to hunt for defects.

---

## Finding Categories

### Broken Hansel Trail

An authoritative Hansel breadcrumb or repository authority refers to something
that does not exist, cannot be resolved, or is non-functional for its declared
purpose.

Examples include:

- a `HANSEL.md` routes to a missing file;
- a declared command or interface does not exist;
- a breadcrumb resolves to an authority that cannot perform its stated role.

### Dead End

The authoritative path does not provide enough information to reach an existing
solution, even though the required responsibility or solution is expected to
exist.

A dead end differs from a Broken Hansel Trail because the known breadcrumbs may
all resolve correctly; the failure is that they stop before sufficient
authority is reached.

### Needed Solution

Required implementation exposes repetitive or reconstructive behavior that has
no durable repository-owned solution and should not need to be repeatedly
performed manually.

This category applies only when repetition or reconstruction is actually
encountered during required work.

It must not be used to speculate that automation might someday be useful.

### Inefficient Navigation

Required implementation reaches the correct authority, but the navigation path
includes unnecessary hops, redundant discovery, backtracking, or information
that does not contribute to implementation or validation.

Token consumption, elapsed implementation time, number of Hansel hops, and
similar measurements may later provide evidence about navigation cost, but
those metrics are not themselves Engineering Findings and are not owned by this
Initiative.

### Authority Conflict

Two apparently authoritative repository sources provide incompatible
instructions, ownership rules, lifecycle behavior, interfaces, or validation
requirements such that the worker cannot deterministically know which authority
governs the current work.

### Boundary Violation

The required solution exists or can be identified, but following it would
require bypassing an established architectural ownership or application
boundary.

Examples include:

- directly mutating domain state through ORM access when an owning application
  interface is required;
- placing domain behavior in a framework adapter that is explicitly defined as
  a thin interface;
- crossing a subsystem ownership boundary in a way the governing contract
  forbids.

### Validation Gap

The implementation path is known and executable, but no deterministic authority
or evidence path exists to prove that the required result is correct.

A Validation Gap differs from a Dead End:

- in a Dead End, the worker cannot reach sufficient authority to perform the
  work;
- in a Validation Gap, the worker can perform the work but cannot
  deterministically prove completion.

---

## Qualifying Examples

The following are Engineering Findings when encountered through required current
work:

- Hansel routes the worker to a repository path that does not exist.
- An authoritative contract requires a management command that is absent.
- Required lifecycle orchestration produces a state that violates the governing
  Planning contract.
- The owning API cannot represent an operation required to complete the current
  Step correctly.
- Two authoritative contracts give incompatible instructions for the same
  required operation.
- The only apparent implementation path requires bypassing a declared subsystem
  or application boundary.
- The worker can implement the required behavior but no deterministic validation
  path exists.
- The worker repeatedly reconstructs the same deterministic procedure because
  no repository-owned automation or authority exists.
- The worker reaches the correct implementation authority only after
  unnecessary Hansel hops or irrelevant repository material that did not
  contribute to the work.

---

## Non-Qualifying Examples

The following are not Engineering Findings:

- "This module could probably be cleaner."
- "This architecture might be improved someday."
- "We should eventually add feature X."
- A worker inspects neighboring modules specifically to look for technical debt.
- A worker searches the repository for additional defects after sufficient
  authority for the current Step has already been reached.
- A naming or formatting preference that does not prevent correct implementation
  or validation.
- Normal documentation that the current Step changed files and validation
  passed.
- A generalized best-practice recommendation not exposed by required current
  work.
- High token usage or long implementation time without an observable navigation
  or workflow failure.
- A human remembers an unrelated item they want to preserve for later.

The last case belongs in Delta Notes.

---

## Delta Notes Boundary

Delta Notes and Engineering Findings serve different purposes.

Use an Engineering Finding when:

- the problem is observed by a worker while performing required engineering
  work;
- the condition satisfies the Engineering Finding qualification rule;
- observable engineering evidence supports the finding.

Use Delta Notes when:

- a human wants to preserve an ad-hoc thought, reminder, idea, or unrelated item;
- the item was not established through the Engineering Finding qualification
  rule;
- no evidence-backed engineering finding is required.

Engineering Discovery must not absorb or replace Delta Notes.

---

## Ordinary Step Evidence Boundary

Successful implementation evidence is not automatically an Engineering Finding.

Examples of ordinary Step evidence include:

- files modified or created;
- commands executed;
- validation results;
- expected behavior confirmed;
- normal implementation decisions required to complete the Step.

Create an Engineering Finding only when execution exposes an additional concrete
engineering problem meeting the qualification rule.

---

## Deferred Authorities

The following responsibilities remain outside the authorities currently
catalogued here and must not be inferred:

- closeout disposition persistence;
- cleanup Initiative generation;
- efficiency telemetry, scoring, or performance analysis.

Do not invent these mechanisms before their owning Planning work becomes
authoritative.

---

## Knowledge Catalogue

### Define whether an observed problem is an Engineering Finding

Use this contract.

A worker has sufficient authority when it can determine:

1. whether the condition was encountered through authoritative current work or
   workflow execution;
2. whether direct evidence supports it;
3. whether one of the defined categories applies;
4. whether an exclusion makes it ordinary Step evidence, a Delta Note, or
   speculative work instead.

### Define finding provenance and lifecycle

Go to:

```text
aurora/subsystems/engineering_discovery/contracts/FINDING_LIFECYCLE.md
```

Use this authority when a worker must determine the durable origin, evidence
requirements, blocking classification, resolution state, or lifecycle of a
qualified Engineering Finding.

### Identify finding capture boundaries

Go to:

```text
aurora/subsystems/engineering_discovery/contracts/FINDING_CAPTURE.md
```

Use this authority when a worker must determine where findings are observed,
which subsystem owns capture, how authoritative Planning provenance is obtained
when available, which execution surfaces may submit findings, or where Step
completion must reconcile encountered evidence when a Step exists.

### Decide whether an observed condition qualifies for capture

Go to:

```text
aurora/subsystems/engineering_discovery/contracts/CAPTURE_POLICY.md
```

Use this authority before submission to prevent speculative finding generation,
unrelated defect hunting, generalized best-practice findings, and hypothetical
cleanup work.

### Decide whether a qualified finding blocks current work

Go to:

```text
aurora/subsystems/engineering_discovery/contracts/BLOCKING_DECISION.md
```

Use this authority after finding qualification and before deciding whether the
current authoritative work or workflow may continue.

### Route a BLOCKING finding into remedial Planning work

Read:

```text
aurora/subsystems/planning/contracts/BLOCKING_REMEDIATION.md
```

Then use:

```text
aurora/subsystems/engineering_discovery/services/remediation.py
```

Engineering Discovery validates the finding and owns its durable remediation
link. Planning owns creation and lifecycle activation of the remedial Phase and
Steps.

### Submit one Engineering Finding during current work or workflow execution

Use:

```text
aurora/subsystems/engineering_discovery/services/findings.py
```

Canonical worker-facing operation:

```text
submit_finding(
    user,
    *,
    category,
    blocking_classification,
    observed_condition,
    evidence="",
    steps_to_reproduce="",
)
```

The service asks Planning for lifecycle-authoritative current execution state.
When an ACTIVE Step exists it is preserved as Planning provenance; when none
exists the finding is captured without invented Planning provenance. Callers
must not supply Project, Initiative, Phase, or Step identifiers.

A finding requires an observed condition plus evidence,
`steps_to_reproduce`, or both.

Historical findings encountered before this submission surface existed must not
be misattributed to the current Step merely to move them out of a temporary
ledger.

### Read unresolved Engineering Findings for Initiative closeout

Use:

```text
aurora/subsystems/engineering_discovery/services/closeout.py
```

Use this read-only boundary when Initiative closeout or postmortem needs the
persisted unresolved findings originating from one Planning Initiative.

The Initiative is the closeout scope.

Engineering Discovery returns finding evidence and originating Planning
provenance. This boundary does not reconcile findings, choose future work, or
mutate Planning state.

### Reconcile Engineering Findings at Initiative closeout

Read:

```text
aurora/subsystems/engineering_discovery/contracts/FINDING_RECONCILIATION.md
```

Use this authority when Initiative closeout or postmortem must assign each
persisted finding exactly one evidence-supported disposition.

Reconciliation determines whether a finding is resolved, invalidated, accepted,
or still requires future work.

A finding does not automatically become Planning work. Human objective
selection remains required before unresolved findings become a future cleanup
Initiative.

---

## Unknown Territory

If the catalogue does not identify sufficient authority for the task:

1. do not invent ownership, behavior, architecture, lifecycle, or persistence;
2. inspect the narrowest likely repository authority;
3. follow cross-boundary dependencies only when required;
4. request additional repository evidence when necessary;
5. add a breadcrumb only when discovery reveals a durable route a future worker
   should not need to rediscover.

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

After completing Engineering Discovery work, ask:

> Has this change made a Hansel breadcrumb or ownership route stale?

If no, no additional Hansel change is required.

If yes:

1. update affected breadcrumbs to current durable authorities;
2. remove obsolete routing;
3. add routing only for durable knowledge destinations;
4. verify changed breadcrumbs resolve.

Do not expand this catalogue with unrelated implementation knowledge learned
during the task.

The objective is accurate navigation to Engineering Discovery authority.

---

# ======================================================================
# END: ENGINEERING_DISCOVERY_HANSEL_CONTRACT
# ======================================================================
