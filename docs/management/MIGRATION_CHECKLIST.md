# AI Execution Platform Baseline

This checklist tracks Aurora's migration from a single-provider implementation to a resilient, vendor-independent AI Execution Platform.

---

# Phase 1 — Architecture

## Architectural Foundation

* [x] Define AI Execution Platform mission
* [x] ADR-001 — AI Execution Architecture
* [x] ADR-002 — Provider Routing & Failover
* [x] ADR-003 — AI Directive Contract
* [x] AI Execution Architecture overview document

---

# Phase 2 — Provider Layer

## Core Abstractions

* [x] AIProvider interface
* [x] AIResponse abstraction
* [x] Provider Registry

## Provider Router

* [ ] Implement Provider Router
* [ ] Centralize provider selection
* [ ] Centralize model resolution
* [ ] Implement provider priority
* [ ] Implement retry policy
* [ ] Implement automatic failover
* [ ] Implement provider health tracking

## Provider Implementations

* [ ] SimulatedProvider
* [ ] OpenAIProvider
* [ ] GeminiProvider
* [ ] Provider response normalization
* [ ] Provider streaming normalization

---

# Phase 3 — Execution Engine

* [ ] Integrate Provider Router
* [ ] Remove direct provider selection
* [ ] Remove direct model selection
* [ ] Remove all direct SDK usage
* [ ] Preserve streaming behavior
* [ ] Preserve usage accounting
* [ ] Preserve UI metrics

---

# Phase 4 — Configuration

* [ ] Centralize AI execution configuration
* [ ] Define provider priority
* [ ] Define provider/model mappings
* [ ] Define retry policy
* [ ] Define cooldown policy
* [ ] Migrate `DeltaDirectives.constraints` to a provider-independent schema

---

# Phase 5 — Cleanup

* [ ] Remove obsolete provider-specific code
* [ ] Remove obsolete provider-specific imports
* [ ] Remove dead code
* [ ] Remove deprecated configuration
* [ ] Verify complete provider isolation

---

# Phase 6 — Validation

## Manual Validation

* [ ] Provider selection
* [ ] Model resolution
* [ ] Streaming responses
* [ ] Automatic provider failover
* [ ] Usage accounting
* [ ] Error handling
* [ ] Wu Chat
* [ ] Active minions
* [ ] Existing workflows
* [ ] Application startup
* [ ] Server stability

## Automated Testing

> Deferred until the implementation baseline is stable.

* [ ] Rebuild SimulatedProvider tests
* [ ] Rebuild provider integration tests
* [ ] Rebuild execution engine tests

---

# Phase 7 — Merge Readiness

* [ ] Green build
* [ ] Documentation review
* [ ] Architecture review
* [ ] Manual regression validation complete
* [ ] Git commit
* [ ] Merge into `main`

---

# Implementation Order

The implementation shall proceed in the following order:

1. Provider Router
2. SimulatedProvider
3. OpenAIProvider
4. GeminiProvider
5. Execution Engine
6. Configuration migration
7. Manual validation
8. Automated test reconstruction
9. Green build
10. Merge

This order establishes the architectural foundation before implementing provider-specific behavior.

---

# Definition of Done

The AI Execution Platform baseline is complete when:

* The Provider Router owns all provider selection and execution policy.
* All provider implementations conform to the `AIProvider` interface.
* The SimulatedProvider serves as the canonical reference implementation for all providers.
* Application code contains no vendor-specific SDK usage outside provider implementations.
* The execution engine is completely vendor-independent.
* Model resolution is centralized and provider-independent.
* Automatic provider failover is operational.
* AI configuration is centralized.
* Existing application functionality is preserved.
* Manual regression validation is complete.
* The application builds cleanly and is ready to merge into `main`.
