<!-- ====================================================================== -->
<!-- FILE: docs/management/MIGRATION_CHECKLIST.md (PATCH 1 OF 1) -->
<!-- START: REMAINING_BASELINE_WORK -->
<!-- ====================================================================== -->

# Phase 2 — Provider Layer

## Core Abstractions

- [x] AIProvider interface
- [x] AIResponse abstraction
- [x] Provider Registry

## Provider Router

- [x] Implement Provider Router baseline
- [x] Centralize provider selection
- [ ] Verify `AI_PROVIDER` configuration routing
- [ ] Centralize model resolution
- [ ] Implement baseline provider failover
- [ ] Validate provider routing
- [ ] Implement provider health tracking (future enhancement)

## Provider Implementations

- [x] SimulatedProvider
- [x] OpenAIProvider
- [x] GeminiProvider
- [x] Provider response normalization
- [x] Provider streaming normalization

---

# Phase 4 — Configuration

- [x] Centralize AI execution configuration
- [x] Environment-configurable default provider (`AI_PROVIDER`)
- [ ] Define provider priority policy
- [ ] Define provider/model mappings
- [ ] Migrate `DeltaDirectives.constraints` to a provider-independent schema

---

# Phase 6 — Validation

## Manual Validation

- [ ] Verify configured provider selection
- [ ] Model resolution
- [ ] Streaming responses
- [ ] Baseline provider failover
- [ ] Usage accounting
- [ ] Error handling
- [ ] Wu Chat
- [ ] Active minions
- [ ] Existing workflows
- [x] Application startup
- [x] Server stability

---

# Implementation Order

Completed baseline implementation order:

1. Provider Router baseline
2. SimulatedProvider
3. OpenAIProvider
4. GeminiProvider
5. Execution Engine integration

Remaining implementation order:

6. Verify configured provider routing
7. Baseline failover
8. Model resolution
9. Directive configuration migration
10. Manual validation
11. Automated test reconstruction
12. Green build
13. Merge

---

# Definition of Done

The AI Execution Platform baseline is complete when:

- The Provider Router owns provider selection.
- The configured default provider is honored.
- Baseline provider failover is operational.
- All provider implementations conform to the `AIProvider` interface.
- The SimulatedProvider serves as the canonical reference implementation for testing.
- Application code contains no vendor-specific SDK usage outside provider implementations.
- The execution engine is vendor-independent.
- Provider routing decisions are isolated from application logic.

<!-- ====================================================================== -->
<!-- END: REMAINING_BASELINE_WORK (PATCH 1 OF 1) -->
<!-- ====================================================================== -->