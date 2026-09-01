# ======================================================================
# FILE: aurora/subsystems/engineering_discovery/contracts/FINDING_CAPTURE.md
# START: ENGINEERING_DISCOVERY_FINDING_CAPTURE
# ======================================================================

# Engineering Finding Capture Boundaries

**Knowledge State: VERIFIED**

**Subsystem:** engineering_discovery

---

## Purpose

Define the authoritative capture points through which an Engineering Finding may
enter Aurora during implementation.

This contract identifies:

- where a finding may be observed;
- which subsystem owns submission and qualification;
- how authoritative Planning provenance is obtained;
- which existing execution surfaces may call Engineering Discovery;
- where unresolved findings must be reconciled before current Step completion.

This contract does not define persistence models, worker submission payloads,
database fields, Planning mutation, or closeout disposition.

---

## Governing Authorities

Finding qualification and category semantics are governed by:

```text
aurora/subsystems/engineering_discovery/contracts/HANSEL.md
```

Finding provenance, blocking classification, and lifecycle semantics are
governed by:

```text
aurora/subsystems/engineering_discovery/contracts/FINDING_LIFECYCLE.md
```

Planning remains authoritative for current executable work.

---

## Core Capture Boundary

Engineering Discovery owns Engineering Finding capture.

A worker or execution surface may report an observed condition to Engineering
Discovery, but the caller does not become the authority for:

- whether the condition qualifies as an Engineering Finding;
- which category applies;
- authoritative originating Planning work;
- blocking classification;
- resolution lifecycle.

Those responsibilities remain owned by Engineering Discovery and the governing
contracts.

---

## Authoritative Planning Provenance

Engineering Discovery must obtain current work provenance from Planning-owned
execution authority.

The required pattern is:

```text
authenticated user
    ↓
Planning-owned executable-work resolver
    ↓
authoritative ACTIVE Step
    ↓
Step.phase
    ↓
Phase.initiative
    ↓
Initiative.project
```

The originating Step is the authoritative anchor.

Engineering Discovery must not reconstruct ACTIVE Initiative, Phase, and Step
state independently through direct ORM queries when Planning already exposes an
application or service boundary for executable work.

The caller should not be trusted to provide arbitrary Project, Initiative,
Phase, or Step identifiers as authoritative provenance.

If no lifecycle-authoritative executable Step exists for the authenticated
user, finding submission must not silently invent provenance.

---

## Capture Point 1: Worker Observation

A potential finding begins when required current implementation exposes a
condition that may satisfy the Engineering Finding qualification rule.

The worker may originate from Wu Chat, another AI worker surface, a management
workflow, or another future execution adapter.

The worker's responsibility is limited to reporting the concrete observed
condition and evidence available from the required work.

The worker must not:

- search outside current required work for additional findings;
- decide persistence architecture;
- invent Planning provenance;
- mutate Planning state merely because a finding was observed.

---

## Capture Point 2: Engineering Discovery Submission Boundary

The canonical submission boundary belongs to Engineering Discovery.

A future bounded submission interface must:

1. require an authenticated user;
2. resolve the user's authoritative executable Planning Step through
   Planning-owned authority;
3. derive Phase, Initiative, and Project from that Step;
4. validate that the reported condition satisfies Engineering Finding
   qualification rules;
5. assign or validate one defined finding category;
6. establish BLOCKING or NON_BLOCKING classification;
7. preserve concrete evidence;
8. reject malformed, unsupported, speculative, or provenance-free submissions.

The bounded current-work submission surface is:

```text
aurora/subsystems/engineering_discovery/services/findings.py
```

with canonical operation:

```text
submit_finding(...)
```

It resolves provenance from the authenticated user's lifecycle-authoritative
ACTIVE Step. It does not accept caller-supplied Planning identifiers.

---

## Capture Point 3: Planning as Provenance Provider

Planning supplies authoritative current work.

Planning does not own Engineering Finding persistence or semantic qualification.

Engineering Discovery may depend on a Planning-owned executable-work resolver
to obtain the current Step and derive the rest of the hierarchy.

This dependency must remain one-way:

```text
Engineering Discovery
    ↓ asks for current executable work
Planning
```

Planning must not need to understand Engineering Finding internals merely to
answer which Step is current.

---

## Capture Point 4: Engineering Session Coordination

Engineering Session may coordinate Engineering Finding workflow because it
already coordinates activity occurring against lifecycle-authoritative Planning
work.

Engineering Session does not own Engineering Findings.

A future Engineering Session adapter may:

- expose finding workflow status;
- invoke Engineering Discovery submission;
- surface unresolved-finding state during active work;
- coordinate Step-completion checks.

Any such adapter must remain thin and call Engineering Discovery and Planning
through their owning boundaries.

Engineering Session must not duplicate finding qualification, provenance, or
lifecycle logic.

---

## Capture Point 5: Wu Chat and AI Execution

Wu Chat may be a caller of Engineering Discovery when an AI worker encounters a
qualifying condition during required work.

Wu Chat does not own Engineering Finding provenance or lifecycle.

Wu-specific prompt context may remain owned by Wu Chat, but authoritative
Planning provenance used for finding persistence must come from Planning-owned
execution authority.

Engineering Discovery must not depend on Wu Chat to determine current work.

---

## Capture Point 6: Step Completion Reconciliation

Before current Planning Step completion becomes final, the execution workflow
needs a deliberate reconciliation boundary for engineering evidence encountered
during that Step.

At minimum, that boundary must make it possible to determine whether:

- a qualifying observed finding remains unsubmitted;
- a BLOCKING finding remains unresolved;
- a NON_BLOCKING finding has been durably preserved before the Step closes;
- structured execution evidence owned elsewhere has been recorded through its
  owning mechanism.

This does not make Engineering Discovery the owner of all Step evidence.

In particular, actual-file tracking remains owned by the subsystem or model that
owns structured Step execution evidence.

The completion boundary exists to prevent durable evidence from being silently
lost when a Step is closed.

The exact completion integration is deferred to later authoritative Planning
work.

---

## Rejected Capture Patterns

The following patterns are not acceptable:

### Caller-Supplied Provenance as Authority

A worker submits `step_id=123` and Engineering Discovery trusts it without
checking authoritative current Planning work.

Reason: provenance can become stale, incorrect, or detached from actual
execution.

### Direct ORM Reconstruction

Engineering Discovery independently searches for ACTIVE Initiative, Phase, and
Step objects to reconstruct the current hierarchy.

Reason: Planning already owns lifecycle-authoritative executable work.

### Wu Chat as Provenance Authority

Engineering Discovery calls a Wu Chat execution-context resolver to determine
current Planning work.

Reason: this would invert subsystem ownership and make a generic engineering
domain depend on an AI/chat subsystem.

### Engineering Session as Finding Owner

Finding qualification or lifecycle logic is implemented inside Engineering
Session because that subsystem coordinates active work.

Reason: coordination does not transfer domain ownership.

### Completion by Prose Alone

A Step closes while known structured evidence or findings exist only inside
free-form validation notes.

Reason: later reconciliation would require prose archaeology or hidden
conversation history rather than repository-owned durable state.

---

## Observed Dogfood Findings

The following findings were encountered while performing the current Engineering
Discovery Initiative.

They are preserved here temporarily as implementation evidence until the
bounded finding-submission mechanism exists.

Findings whose true originating Step is still ACTIVE at submission time may be
submitted through the bounded current-work mechanism.

Findings encountered before that mechanism existed must remain in the temporary
pending-findings ledger until Aurora has an explicit historical-ingest path that
can preserve their original Planning provenance without trusting arbitrary
caller-supplied identifiers. They must not be falsely attributed to a later
ACTIVE Step merely to migrate them into persistence.

### Finding A: Wu Chat Reconstructs Planning Execution State

Observed condition:

```text
aurora/subsystems/wu_chat/services/execution_context.py
```

independently queries Planning Initiative, Phase, and Step models to reconstruct
the ACTIVE hierarchy for the user.

Existing comparison:

```text
aurora/subsystems/engineering_session/services/status.py
```

obtains lifecycle-authoritative work through Planning's executable-work service
and derives the hierarchy from the returned Step.

Provisional category:

```text
BOUNDARY VIOLATION
```

Provisional classification:

```text
NON_BLOCKING
UNRESOLVED
```

Reason it is non-blocking:

Engineering Discovery can obtain current work through Planning authority without
depending on Wu Chat's resolver.

Do not repair Wu Chat as part of this Step.

---

### Finding B: Structured Actual-File Evidence Is Not Maintained During Work

Observed condition:

Engineering Discovery Steps created and modified repository files, but the
structured Step actual-files-created / actual-files-mutated mechanism was not
updated during execution.

The paths were recorded manually in Step validation notes instead.

This omission occurred repeatedly across current Initiative work.

Provisional category:

```text
NEEDED SOLUTION
```

Provisional classification:

```text
NON_BLOCKING
UNRESOLVED
```

Reason it is non-blocking:

Current Steps can still be implemented and validated, but structured durable
execution evidence is not being maintained through its owning mechanism.

Engineering Discovery does not automatically own actual-file tracking.

Do not repair this mechanism as part of this Step.

---

## Step 328 Acceptance Conditions

This capture-boundary design is sufficient when a clean-context worker can
determine:

1. Engineering Discovery owns finding capture and qualification;
2. Planning owns authoritative executable-work provenance;
3. the current Step is the provenance anchor;
4. Phase, Initiative, and Project are derived from that Step;
5. callers do not supply trusted provenance IDs;
6. Wu Chat and Engineering Session may call or coordinate the workflow without
   owning the finding domain;
7. current Step completion is a required reconciliation boundary;
8. persistence schema and write interfaces remain deferred;
9. the two findings encountered during this work are preserved for later
   submission without being repaired opportunistically.

---

# ======================================================================
# END: ENGINEERING_DISCOVERY_FINDING_CAPTURE
# ======================================================================
