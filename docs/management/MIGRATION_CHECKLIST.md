# Aurora Baseline Definition of Done

This document is **not** project state.

It defines the objective completion criteria for the Aurora baseline.

Consult only during:

* milestone reviews;
* release preparation;
* merge readiness.

---

## Provider Architecture

* [x] AIProvider interface
* [x] Provider registry
* [x] Provider router
* [x] OpenAI provider
* [x] Gemini provider
* [ ] Provider priority
* [ ] Automatic failover validation

---

## Workspace Pipeline

* [x] Repository path resolution
* [x] Repository boundary validation
* [x] Source hydration
* [x] Structured prompt construction

---

## Structured Patch Pipeline

* [x] PATCH_START / PATCH_END detection
* [x] Structured patch validation
* [x] Malformed response rejection
* [x] Truncated response rejection
* [x] Structured review payload generation

---

## Wu Review Workflow

* [x] Wu chat restored
* [x] Duplicate response elimination
* [x] Repository hydration
* [x] Review slider
* [x] Monaco diff viewer
* [x] Current / Proposed orientation
* [x] Frontend patch integration
* [x] PendingCodeChange persistence
* [x] Explicit approval workflow
* [x] Source consistency verification
* [x] Conflict detection
* [x] Single verified repository write
* [x] Reject performs no repository mutation

---

## Observability

* [x] Provider telemetry collection
* [x] Model telemetry collection
* [x] Token usage collection
* [x] Execution latency collection
* [ ] Telemetry pane presentation polish
* [ ] Provider failover telemetry

---

## Documentation

* [x] ADR-001
* [x] ADR-002
* [x] ADR-003
* [x] PROJECT_STATE.yaml
* [x] DeltaDirective cleanup
* [x] Protocol v3.2 alignment

---

## Release Readiness

* [ ] Regression smoke test
* [ ] Remove temporary diagnostics
* [ ] Merge feature/provider-abstraction into main
* [ ] Aurora baseline complete
