# ======================================================================

# FILE: docs/management/MIGRATION_CHECKLIST.md (PATCH 1 OF 1)

# START: AURORA_BASELINE_DEFINITION_OF_DONE

# ======================================================================

# Aurora Baseline Definition of Done

This document is **not** project state.

It defines the required conditions for the Aurora baseline to be considered complete.

Consult only during milestone reviews, release preparation, or merge readiness.

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
* [x] Patch validation
* [x] Malformed response rejection
* [x] Truncated response rejection
* [x] Structured review payload generation

---

## Wu Review Interface

* [x] Wu chat restored
* [x] Duplicate response elimination
* [x] Review slider
* [x] Monaco diff viewer
* [x] Current / Proposed orientation
* [x] Frontend patch integration
* [ ] PendingCodeChange approval
* [ ] Source consistency verification
* [ ] Single verified repository write
* [ ] Reject performs no mutation

---

## Observability

* [ ] Provider telemetry
* [ ] Model telemetry
* [ ] Patch lifecycle telemetry
* [ ] Approval telemetry

---

## Documentation

* [x] ADR-001
* [x] ADR-002
* [x] ADR-003
* [x] PROJECT_STATE.yaml
* [ ] DeltaDirective cleanup
* [ ] Protocol review

---

## Release Readiness

* [ ] Regression smoke test
* [ ] Temporary diagnostics removed
* [ ] Merge to main
* [ ] Aurora baseline complete

# ======================================================================

# END: AURORA_BASELINE_DEFINITION_OF_DONE (PATCH 1 OF 1)

# ======================================================================
