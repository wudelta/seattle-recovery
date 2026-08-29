# ======================================================================
# FILE: aurora/subsystems/delta_directives/contracts/DIRECTIVE_DEPLOYMENT.md
# START: DELTA_DIRECTIVE_DEPLOYMENT_CONTRACT
# ======================================================================

# Delta Directive Deployment Contract

**Version: 1.0**

---

## Purpose

This contract defines the authoritative workflow for changing persistent AI worker instructions in Aurora.

Delta Directives owns persistent worker configuration.

`DeltaDirectives.instructions` remains the canonical persistent runtime authority for worker instructions.

Worker instructions use Markdown as their canonical textual representation.

Repository-owned directive source artifacts exist to make changes to that runtime authority deliberate, reviewable, reproducible, and validatable.

This contract governs deployment into that authority.

It does not govern AI provider execution, worker orchestration, Planning lifecycle, or general repository navigation.

---

## Architectural Problem

Historically, worker instructions could be changed through browser/API mutation and AI-assisted prompt rewriting.

Those paths allow live worker behavior to change without a repository-owned source artifact, deterministic validation, dry-run, or post-deployment equivalence proof.

Worker directives are executable configuration.

A malformed or unintended directive change can alter how repository authority is interpreted, how engineering tasks are performed, and how future worker instructions are followed.

Therefore:

> Persistent worker instructions must not be mutated through an uncontrolled editing surface.

Directive changes must pass through one controlled deployment authority.

---

## Canonical Authorities

The directive system has two distinct authorities.

### Repository Source Authority

The repository owns the proposed deployable representation of a worker directive.

The source artifact:

* is Markdown;
* identifies exactly one `directive_name`;
* contains the complete intended instruction set;
* is reviewable before deployment;
* is validated before persistence;
* is suitable for deterministic comparison against persisted state.

The repository source is the authoritative deployment input.

It is not automatically the runtime instruction authority merely because it exists.

### Persistent Runtime Authority

`DeltaDirectives.instructions` is the canonical persistent instruction authority consumed by Aurora workers.

Deployment changes this authority only after the repository source passes validation and an explicit apply operation occurs.

After successful deployment, the source and persisted instruction text must be equivalent according to this contract.

---

## Deployment Flow

The canonical workflow is:

```text
authorized human or repository workflow
        ↓
approved deployment trigger
        ↓
repository-owned directive source
        ↓
deterministic validation
        ↓
dry-run
        ↓
explicit apply
        ↓
atomic whole-directive replacement
        ↓
DeltaDirectives.instructions
        ↓
post-apply equivalence validation
```

No stage may silently rewrite the directive.

---

## Deployment Trigger

A controlled mutation authority is useful only if it has an explicit entry point.

The initial human-facing deployment trigger is a repository-owned Django management command.

Conceptually:

```text
deploy_delta_directive
```

The command must support distinct dry-run and apply modes.

The management command is an entry point, not the implementation authority.

It must delegate validation and persistence to a reusable Delta Directives deployment service.

Therefore:

```text
management command
        ↓
deployment service
        ↓
validator
        ↓
persistent directive authority
```

Future authorized Aurora workflows may invoke the same deployment service programmatically.

They must not create an independent directive mutation implementation.

---

## Deployment Service Authority

Delta Directives must expose one reusable service responsible for controlled worker-instruction deployment.

The service owns:

* locating or accepting the canonical source artifact;
* determining the target `directive_name`;
* deterministic validation;
* dry-run evaluation;
* atomic whole-instruction replacement;
* post-apply verification;
* deployment result reporting.

The service must not own:

* worker execution;
* AI provider selection;
* Wu orchestration;
* Planning lifecycle;
* repository-navigation decisions;
* interactive prompt authoring.

---

## Whole-Directive Replacement

Deployment operates on the complete worker instruction document.

It must not perform:

* line-level merges against live instructions;
* conversational modifications directly against persisted instructions;
* AI-generated surgical edits against the live directive;
* implicit preservation of unspecified sections;
* partial database mutation followed by later repair.

The intended transformation is:

```text
validated complete source
        ↓
complete persisted replacement
```

This prevents the deployment mechanism from having to infer author intent.

---

## Validation Boundary

Validation must complete before persistent mutation.

At minimum, validation must establish:

1. the source artifact exists;
2. the source can be read as text;
3. the source identifies exactly one intended directive;
4. the target directive identity is valid;
5. the instruction document is not empty;
6. the instruction representation is Markdown text rather than generated HTML;
7. required Aurora-owned structural contracts are present when applicable;
8. prohibited or obsolete authority references defined by current validation rules are rejected;
9. the source is eligible for complete replacement;
10. no database mutation has occurred during validation.

Validation failures must explain the defect and stop deployment.

They must not silently normalize, repair, rewrite, or optimize the instructions.

---

## Structural Contract Validation

Some directives may contain repository-owned instruction protocols that are required for correct worker behavior.

Where such protocols exist, the validator may require exact structural markers or semantic invariants.

For example, a worker continuation protocol may require known boundary markers.

Those requirements must originate from current repository authority.

They must not be inferred from historical directive text.

Validation rules should be narrow enough to detect known invalid deployment states without turning the deployment service into an independent worker-behavior specification.

---

## Dry-Run

Dry-run is mandatory before intentional human deployment.

Dry-run must:

* load the same source that apply would use;
* run the same pre-deployment validation;
* resolve the same target directive;
* report whether the directive would be created or replaced;
* report meaningful validation results;
* perform no persistent mutation.

A successful dry-run proves eligibility to attempt apply.

It does not prove that apply occurred.

---

## Apply

Apply must be explicit.

Apply must:

1. repeat or otherwise guarantee the same validation used by dry-run;
2. resolve exactly one target directive;
3. perform the instruction replacement atomically;
4. preserve Markdown text without presentation conversion;
5. update the persistent directive only through the deployment service;
6. verify the persisted result before reporting success.

A failed apply must not report success.

Partial mutation must not be accepted as a valid deployment result.

---

## Post-Apply Equivalence

Successful deployment requires deterministic evidence that the deployed instruction document is the intended document.

At minimum:

```text
canonical source instruction text
        ==
persisted DeltaDirectives.instructions
```

Comparison rules may normalize only representation details explicitly defined by this contract or its validator.

They must not disguise substantive differences.

If equivalence cannot be proven, deployment is not successfully validated.

---

## Audit Evidence

A deployment result must provide enough evidence to determine:

* which directive was targeted;
* which repository source produced it;
* whether the operation was dry-run or apply;
* whether validation passed;
* whether persistent mutation occurred;
* whether post-apply equivalence passed.

Existing model timestamps may contribute to this evidence.

If implementation proves that durable deployment attribution requires additional persistent metadata, that requirement must be added deliberately rather than inferred by the command.

This contract does not require speculative audit schema changes before that need is demonstrated.

---

## User Interface Boundary

The Delta Directives UI is a troubleshooting and inspection surface.

It may expose information such as:

* directive inventory;
* active/inactive state where appropriate;
* directive name;
* persisted instruction text;
* constraints;
* modification metadata;
* copy or search capability.

The UI must not provide an uncontrolled mutation path for canonical worker instructions.

In particular, the UI must not:

* save edited worker instructions directly;
* optimize live instructions through an AI worker;
* perform partial directive rewrites;
* bypass deployment validation;
* invoke an independent persistence path.

The controlled deployment workflow is the mutation entry point.

The browser is not an alternate deployment authority.

---

## Existing API Mutation

Existing Delta Directives API behavior that directly mutates worker instructions predates this contract.

Such behavior is not authoritative merely because it exists.

Implementation work following this contract must reconcile those mutation paths so that worker instruction deployment cannot bypass the controlled deployment service.

Read-only API behavior may remain where useful.

Other configuration behavior such as constraints or activation state must not be redesigned merely because worker-instruction deployment is being secured.

If those behaviors later prove to require equivalent controls, they must be addressed through their own observed engineering requirement.

---

## AI-Assisted Directive Authoring

AI may assist in proposing or drafting repository-owned directive source.

AI output must never become live worker instruction state merely because it was generated.

The boundary remains:

```text
AI or human proposal
        ↓
repository-owned source
        ↓
validation
        ↓
explicit deployment
```

The deployment service does not optimize instructions.

It validates and deploys an already chosen complete instruction document.

---

## Source Location

Canonical directive source artifacts must live under a repository-owned Delta Directives location established by implementation.

The exact directory and source schema must be chosen before the first deployment implementation is considered complete.

The location must be:

* deterministic;
* discoverable through Delta Directives Hansel authority;
* suitable for version control;
* independent of browser presentation;
* unambiguous with respect to `directive_name`.

Do not create multiple competing source locations.

---

## Failure Behavior

Deployment must fail closed.

Examples include:

```text
missing source
invalid source
ambiguous directive identity
failed structural validation
unknown target when creation is prohibited
persistence failure
post-apply mismatch
```

A failure must:

* report the reason;
* avoid claiming deployment success;
* avoid silent retries that change semantics;
* avoid AI repair of the source;
* preserve the previous valid persisted directive whenever atomicity permits.

---

## Validation of the Deployment System

The deployment authority is functioning correctly when deterministic tests prove that:

1. a valid directive source passes validation;
2. an invalid directive source fails before mutation;
3. dry-run performs no database mutation;
4. apply performs one complete instruction replacement;
5. persisted Markdown remains semantically unchanged by presentation conversion;
6. post-apply source/database equivalence is verified;
7. browser/API worker-instruction mutation cannot bypass deployment authority;
8. AI-assisted optimization cannot directly alter live instructions;
9. deployment failures leave clear evidence;
10. the management command and any future authorized caller use the same deployment service.

---

## Ownership Boundary

Delta Directives owns:

```text
worker configuration
repository-owned directive source
directive deployment validation
controlled worker-instruction persistence
deployment equivalence proof
```

Delta Directives does not own:

```text
AI provider implementation
shared AI execution
Wu conversational orchestration
Planning lifecycle
Hansel repository navigation
general engineering workflow orchestration
```

Cross those boundaries only through the owning subsystem's Hansel trail.

---

## Hansel Authority

Workers seeking to deploy or change canonical worker instructions must be routed from:

```text
aurora/subsystems/delta_directives/contracts/HANSEL.md
```

to this contract.

Implementation details discovered while building the deployment service do not belong in Hansel unless they establish a new durable knowledge destination.

---

## Completion Standard

This contract is implemented when Aurora has:

```text
one repository-owned directive source authority
        +
one deterministic validator
        +
one reusable deployment service
        +
one explicit management-command trigger
        +
dry-run
        +
atomic apply
        +
post-apply equivalence proof
        +
no uncontrolled browser/API mutation of worker instructions
```

Until those conditions are satisfied, the existing persistent directive system remains operational but its mutation path is not considered fully controlled under this contract.

# ======================================================================
# FILE: aurora/subsystems/delta_directives/contracts/DIRECTIVE_DEPLOYMENT.md
# END: DELTA_DIRECTIVE_DEPLOYMENT_CONTRACT
# ======================================================================
