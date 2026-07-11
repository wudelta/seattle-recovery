# Aurora Development Resume Guide

## Session Summary

The AI Execution Platform architecture has reached baseline completion. The focus of development has shifted from building infrastructure to validating that infrastructure through real-world Wu Chat workflows.

This phase is intentionally conservative. The objective is to prove the existing architecture, eliminate integration defects, and prepare the provider abstraction branch for merge into `main`.

Wu Chat now serves as the primary validation harness for the entire AI execution pipeline.

---

## Confirmed Execution Path

```text
Browser
    ↓
wu_chat.js
    ↓
wu_chat_api.py
    ↓
MinionRunner
    ↓
ProviderRouter
    ↓
Selected Provider
    ↓
AI Response
```

The execution path is understood end-to-end and should remain the primary reference when investigating integration issues.

---

## Current Development Focus

Development has transitioned from architectural implementation to integration validation.

The remaining work centers on:

* validating provider routing
* validating telemetry collection
* classifying conversational versus mutation requests
* repairing the Monaco review workflow
* removing obsolete UI behavior only after replacement functionality has been validated

No additional architectural expansion should occur during the Aurora baseline.

---

## Major Discoveries

* Provider abstraction successfully isolates UI code from provider implementations.
* Provider implementations are responsible only for SDK communication.
* Provider selection belongs exclusively to the Provider Router.
* Wu currently behaves as a synchronous request/response system despite existing streaming infrastructure.
* Console websocket infrastructure exists but currently carries mostly local UI events instead of execution telemetry.
* Every Wu interaction currently creates a `WorkspaceTransaction`.
* Because every interaction becomes a transaction, the approval drawer opens for ordinary conversations.
* The missing architectural boundary is intent classification (conversation versus workspace mutation).
* `ChatLedger` has replaced browser-side history reconstruction as the system of record.
* `dev_streamer_api` appears to contain both production infrastructure and historical demonstration code that should be evaluated before cleanup.
* The Monaco slideout remains the intended mutation review interface and should be validated before removing the legacy approval workflow.

---

## Next Development Sequence

### Phase 1 — Wu Execution Trace

Trace the complete browser-to-provider execution path.

Objectives:

* verify request flow
* verify response flow
* verify provider selection
* verify model resolution
* identify telemetry collection points

This phase should prioritize observation over modification.

---

### Phase 2 — Telemetry Validation

Validate the execution telemetry pipeline.

Confirm availability of:

* provider
* resolved model
* request timing
* execution latency
* token usage
* request metrics

Surface existing data before introducing new telemetry.

---

### Phase 3 — Intent Classification

Introduce explicit classification between:

* conversational requests
* workspace mutation requests

Expected outcome:

* ordinary conversations no longer create `WorkspaceTransaction` records
* approval workflows execute only when workspace mutations are requested

This is expected to resolve several downstream UI issues simultaneously.

---

### Phase 4 — Workflow Cleanup

After successful validation:

* repair the Monaco slideout workflow
* validate mutation review
* remove redundant approval mechanisms
* evaluate removal of obsolete browser-side history logic
* review historical demonstration code for retirement

---

## Engineering Guidance

Continue following **The Delta Way**.

* Make small, surgical, production-safe changes.
* Prefer understanding before modification.
* Keep each checkpoint independently stable.
* Remove obsolete code only after replacement behavior has been validated.
* Avoid architectural expansion during the Aurora baseline.
* If work cannot be completed safely within a short session, stop, commit, and resume later.

The objective is not rapid feature accumulation.

The objective is a stable Aurora baseline suitable for merge into `main`.

---

## Current Milestone

**Target:** Aurora Baseline Complete — **July 15, 2026**

Success criteria:

* Wu Chat validates the complete AI execution platform.
* Provider routing is verified.
* Telemetry is validated.
* Intent classification is functioning.
* UI workflow is stable.
* Branch is ready for merge into `main`.

Following completion of the Aurora baseline, development focus shifts to the HopeHub beta prototype targeting **August 15, 2026**.
