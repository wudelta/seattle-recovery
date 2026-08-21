# ======================================================================
# FILE: aurora/subsystems/wu_chat/contracts/HANSEL.md
# START: WU_CHAT_HANSEL_CONTRACT
# ======================================================================

# Wu Chat — Hansel Contract

**Knowledge State:** VERIFIED
**Subsystem:** `wu_chat`

---

## Purpose

Wu Chat is Aurora's human-and-AI collaboration surface for engineering work.

It accepts developer instructions, assembles task-specific execution and
repository context, invokes Aurora's shared AI worker execution layer, persists
bounded conversation and code-review state, and presents proposed repository
changes for human review.

Wu Chat is an interaction and review subsystem.

It does not own repository mutation policy, Planning state, AI provider
implementation, or repository discovery policy.

---

## Ownership Boundary

Wu Chat owns:

* Wu conversational API behavior;
* persisted Wu conversation history;
* pending code-review transactions;
* Wu-specific execution-context assembly;
* repository file context hydration for Wu requests;
* parsing of structured Wu patch responses;
* preparation of code-review payloads;
* Wu-specific code-review workflow state;
* Wu-specific admin configuration;
* Wu-specific client-side interaction and review behavior.

Wu Chat does not own:

* AI provider implementations;
* provider routing policy;
* Delta Directive definitions;
* Component Registry lifecycle;
* general repository dependency discovery;
* Planning hierarchy or Initiative lifecycle;
* direct orchestration of Initiative execution;
* automatic repository mutation without human review;
* general-purpose Monaco/editor infrastructure.

---

## Canonical Data Authority

Authoritative Wu Chat models live in:

```text
aurora/subsystems/wu_chat/models.py
```

Current persistent models include:

```text
ChatLedgerEntry
PendingCodeChange
```

### ChatLedgerEntry

Stores bounded persisted Wu conversation history.

The model owns its persistence lifecycle and bounded history behavior.

### PendingCodeChange

Stores one Wu-generated code proposal awaiting developer review.

Known review states include:

```text
PENDING
APPLIED
REJECTED
CONFLICT
```

The persisted review record is authoritative for the proposal and its review
state.

---

## Repository Map

```text
wu_chat/
    admin.py
        Django administration for Wu Chat persistence models.

    models.py
        ChatLedgerEntry and PendingCodeChange persistence models.

    api/
        endpoint.py
            Primary Wu Chat HTTP/API execution surface.

    contracts/
        HANSEL.md
            Canonical Hansel discovery entry point.

        UI_MAP.md
            Routes Wu Chat UI work to the owning template and browser modules.

    services/
        execution_context.py
            Builds Wu execution context from current Aurora state.

        patch_parser.py
            Parses and validates structured Wu patch responses.

        workspace_context.py
            Resolves repository paths, reads source content, and hydrates
            Wu prompts with bounded repository context.
```

Wu Chat also owns client-side review behavior outside the Python subsystem
directory through framework/static integration surfaces documented below.

---

## Public Entry Points

### Wu Chat API

Primary server-side entry point:

```text
aurora/subsystems/wu_chat/api/endpoint.py
```

This endpoint coordinates Wu-specific request handling.

It consumes Wu Chat services rather than embedding all context and patch logic
directly in the API layer.

---

### Wu Chat UI

Primary UI routing contract:

```text
aurora/subsystems/wu_chat/contracts/UI_MAP.md
```

Use this contract when the task concerns Wu Chat workspace layout, core browser
chat behavior, Engineering Session controls, Delta Note workflow behavior,
Fleet Telemetry presentation, or Wu-specific Monaco diff review.

The UI map routes each concern to the narrowest template or JavaScript
authority.

Wu-specific browser assets remain owned by Wu Chat even when Django static-file
requirements place them outside:

```text
aurora/subsystems/wu_chat/
```

---

## Execution Flow

The verified high-level Wu Chat flow is:

```text
developer instruction
    ↓
Wu Chat API
    ↓
execution context resolution
    ↓
repository context resolution when required
    ↓
shared MinionRunner execution
    ↓
AI response
    ↓
patch marker detection and parsing when present
    ↓
PendingCodeChange persistence
    ↓
Wu diff-review payload
    ↓
human review
```

Wu Chat coordinates this interaction flow.

It does not own the shared provider layer beneath `MinionRunner`.

---

## Execution Context

Primary implementation:

```text
aurora/subsystems/wu_chat/services/execution_context.py
```

`ExecutionContextResolver` builds task-relevant Aurora execution context for Wu.

This service should remain Wu-specific unless a future orchestration subsystem
establishes a broader reusable execution-context abstraction.

---

## Repository Context

Primary implementation:

```text
aurora/subsystems/wu_chat/services/workspace_context.py
```

Despite the historical `workspace_context` name, this service owns bounded
repository-file context hydration for Wu requests.

Known responsibilities include:

* extracting a requested repository path;
* resolving repository-relative paths;
* reading source content;
* constructing a hydrated Wu prompt.

The name is currently retained because it describes Wu request context rather
than the removed historical `aurora/workspace/` subsystem.

If future Hansel or orchestration services replace this responsibility with a
shared repository-discovery abstraction, ownership and naming should be
re-evaluated.

**Knowledge State:** VERIFIED

---

## Patch Parsing

Primary implementation:

```text
aurora/subsystems/wu_chat/services/patch_parser.py
```

Wu Chat expects structured patch markers for code-review responses.

Known responsibilities include:

* detecting structured patch markers;
* validating a single patch response;
* normalizing repository paths;
* detecting display language;
* producing a parsed patch payload.

Patch parsing prepares a proposal for review.

It does not itself apply repository changes.

---

## AI Usage

Wu Chat uses AI for conversational engineering assistance and code proposal
generation.

AI execution is delegated through Aurora's shared:

```text
MinionRunner
```

Current implementation authority:

```text
aurora/minions/engine.py
```

This path is intentionally retained as an architectural marker pending the
design of Aurora's future orchestration subsystem.

Wu Chat consumes `MinionRunner`.

Wu Chat does not own:

* provider selection infrastructure;
* provider-specific behavior;
* global minion execution architecture.

AI-generated code must remain a proposal until the Wu review workflow explicitly
authorizes mutation.

---

## Dependencies

### Delta Directives

Wu Chat depends on Aurora's directive/minion configuration architecture through
shared AI execution.

Authoritative subsystem:

```text
aurora/subsystems/delta_directives/
```

Wu Chat does not own directive definitions.

---

### Shared AI Provider Layer

Wu Chat indirectly depends on:

```text
core_logic/ai/
```

through `MinionRunner`.

Provider-specific behavior belongs to the provider layer, not Wu Chat.

---

### Django

Wu Chat depends on:

```text
Django ORM
Django admin
Django API/request handling
Django static/template integration
```

---

### Monaco

Wu Chat's review UI uses Monaco for code-diff rendering.

Monaco is a client-side presentation dependency.

Wu Chat owns the Wu-specific integration, not Monaco itself.

---

## Consumers

Known consumers include:

```text
Delta
    Uses Wu Chat as the primary human/AI engineering collaboration surface.

Aurora Console
    Hosts the Wu Chat interface and code-review slider.

Future orchestration
    May eventually consume or replace portions of Wu execution-context
    coordination when Initiative execution becomes orchestrated.
```

Other subsystems may invoke shared AI execution independently of Wu Chat.

Wu Chat is not the universal AI execution layer.

---

## Framework Integration Surfaces

Wu Chat uses repository locations outside its subsystem because Django and the
Aurora Console impose integration surfaces.

### Static JavaScript and Templates

Wu Chat browser and template integration surfaces are routed through:

```text
aurora/subsystems/wu_chat/contracts/UI_MAP.md
```

The current Wu Chat UI spans Django static assets and templates outside the
Python subsystem directory. Those locations are framework integration surfaces,
not ownership boundaries.

Use the UI map rather than rediscovering client-side ownership from filenames.

### Model Export

Wu Chat models are re-exported through:

```text
aurora/models.py
```

### Admin Registration

Wu Chat admin configuration is loaded through:

```text
aurora/admin.py
```

These are integration surfaces, not ownership boundaries.

---

## Validation Protocol

Wu Chat changes require proof appropriate to the specific mutation.

### Consumer Mapping

Before moving, renaming, or deleting a Wu Chat service, model, API symbol,
static asset, or template reference, map its consumers.

Example:

```bash
grep -RIn <old-path-or-symbol> aurora core_logic
```

The consumer map defines the known blast radius before mutation.

---

### Tombstone Validation

After a path, symbol, module, or static asset is moved or renamed, verify the old
reference no longer exists.

Examples include searching for:

```text
aurora.wu
old Wu service paths
old static asset paths
obsolete Wu template paths
old exported symbols
```

Expected:

```text
no live references
```

---

### Model Survival Validation

For source-only Wu Chat model moves:

```bash
dmakemigrations --check
daurora-cmd check
```

Expected:

```text
No changes detected
System check identified no issues
```

Where relevant, verify:

```text
model.__module__
model._meta.app_label
model._meta.db_table
existing row count
```

---

### Admin Survival Validation

After moving Wu Chat admin configuration:

```text
ChatLedgerEntry in admin.site._registry
PendingCodeChange in admin.site._registry
```

Expected:

```text
True
True
```

---

### Static Asset Survival Validation

After moving Wu-specific JavaScript:

1. update the Django static reference;
2. tombstone the old static path;
3. run Django system validation;
4. verify the Wu diff viewer still loads in Aurora Console when the affected UI
   workflow is available.

---

### Patch Review Survival Validation

Changes to patch parsing or review flow should prove, as applicable:

```text
structured patch markers are recognized;
repository path normalization remains bounded;
current and proposed content remain distinct;
PendingCodeChange is created correctly;
the review payload reaches the client;
the Monaco diff renders current versus proposed content;
approval/rejection state remains correct.
```

Persistent regression tests may be appropriate for durable parser or review
invariants.

One-time structural moves require change-specific survival proof instead.

---

## Change Validation Principle

Hansel distinguishes:

```text
structural proof
    ownership and repository grammar

change-specific proof
    consumer map, tombstone, identity, and survival

persistent regression tests
    durable parser, review, security, or runtime behavior
```

Do not create a mirrored test module merely because a Wu Chat module exists.

Protect durable behavior, not file topology for its own sake.

---

## Known Gaps

### Orchestration Boundary

**State:** PLANNED

Wu Chat currently invokes shared `MinionRunner` directly.

A future orchestration subsystem is expected to coordinate Initiative execution
across Planning, Hansel, Component Registry, Delta Directives, and AI workers.

Wu Chat should remain the human collaboration surface rather than becoming the
general orchestration engine.

Next breadcrumb:

```text
aurora/minions/engine.py
```

and the future orchestration design.

---

### Repository Context Ownership

**State:** VERIFIED

Wu Chat currently owns:

```text
services/workspace_context.py
```

for bounded Wu-specific repository context hydration.

Whether some portion of this responsibility should later move into Hansel or
orchestration is not yet established.

**Knowledge State:** UNKNOWN

Next breadcrumb:

```text
future orchestration and Hansel repository-context design
```

Do not move this service merely because another subsystem may eventually need
similar capability.

---

### Review Application Boundary

**State:** VERIFIED

`PendingCodeChange` represents reviewed code proposals.

The exact current repository-write implementation used after approval is not
fully described by this contract.

**Knowledge State:** UNKNOWN

Next breadcrumb:

```text
aurora/subsystems/wu_chat/api/endpoint.py
```

Inspect the approval/application path before modifying repository-write
semantics.

---

## Deeper Contracts

The current authoritative deeper UI contract is:

```text
aurora/subsystems/wu_chat/contracts/UI_MAP.md
```

Use it for Wu Chat template and browser-module ownership.

Future deeper contracts should be created only when complexity justifies them.

Potential future candidates include:

```text
CODE_REVIEW.md
SESSION_LIFECYCLE.md
```

These are not required today.

`HANSEL.md` remains the canonical discovery entry point.

---

## Hansel Rules for This Subsystem

A worker modifying Wu Chat must:

1. begin with this contract;
2. identify whether the change concerns API, persistence, execution context,
   repository context, patch parsing, or client-side UI behavior;
3. map consumers before moving or deleting Wu Chat assets;
4. perform tombstone validation after rename or removal;
5. preserve human review as the boundary before code mutation;
6. keep provider-specific behavior outside Wu Chat;
7. keep Planning ownership outside Wu Chat;
8. keep general orchestration outside Wu Chat;
9. preserve Django model identity during source-only model moves;
10. perform survival validation specific to the changed workflow;
11. update this contract when ownership, entry points, dependencies, or review
    boundaries change.

---

## Next Hansel Breadcrumb

For Wu Chat request execution:

```text
aurora/subsystems/wu_chat/api/endpoint.py
```

For persistent Wu conversation and review state:

```text
aurora/subsystems/wu_chat/models.py
```

For execution-context assembly:

```text
aurora/subsystems/wu_chat/services/execution_context.py
```

For repository context hydration:

```text
aurora/subsystems/wu_chat/services/workspace_context.py
```

For patch parsing:

```text
aurora/subsystems/wu_chat/services/patch_parser.py
```

For Wu Chat client-side UI work:

```text
aurora/subsystems/wu_chat/contracts/UI_MAP.md
```

For the shared AI worker execution marker:

```text
aurora/minions/engine.py
```

# ======================================================================
# END: WU_CHAT_HANSEL_CONTRACT
# ======================================================================
