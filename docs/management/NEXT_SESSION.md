<!-- ====================================================================== -->
<!-- FILE: docs/management/NEXT_SESSION.md (PATCH 1 OF 1) -->
<!-- START: SESSION_RESUME -->
<!-- ====================================================================== -->

# Next Development Session

## Immediate Objective

Complete and validate the AI Execution Platform baseline.

The provider abstraction is architecturally complete. The remaining work is to
verify production behavior, implement baseline failover, rebuild confidence
through validation, and prepare the branch for merge into `main`.

Avoid introducing new architectural features unless they are required to
complete the baseline or directly support shared functionality needed by
HopeHub.

---

## Resume Order

1. Verify that `AI_PROVIDER` from configuration is honored by the Provider Router.
2. Validate provider routing behavior across OpenAI and Gemini.
3. Implement simple provider failover within the Provider Router.
4. Centralize model resolution within the Provider Router.
5. Migrate `DeltaDirectives.constraints` to a provider-independent schema.
6. Perform manual validation:
   - Provider selection
   - Streaming responses
   - Usage accounting
   - Error handling
   - Wu Chat
   - Active minions
   - Existing workflows
7. Rebuild automated tests around the provider abstraction.
8. Achieve a green build.
9. Review documentation and prepare merge into `main`.

Future enhancements (not required for baseline):

- Provider health tracking
- Cooldown policies
- Cost-aware routing
- Advanced routing strategies
- Additional provider integrations

---

## Current Architecture State

Completed:

- AIProvider interface
- AIResponse normalization contract
- Provider Registry
- Provider Router baseline
- SimulatedProvider reference implementation
- OpenAIProvider implementation
- GeminiProvider implementation
- Execution engine provider integration
- Removal of direct SDK dependency from the execution engine
- Environment-configurable default provider (`AI_PROVIDER`)

Current architectural boundaries:

- Provider Registry owns provider registration.
- Provider Router owns routing and failover decisions.
- Provider implementations own vendor SDK interaction only.
- Application code remains vendor-independent.
- SimulatedProvider is reserved for testing and should never be selected by
  production failover.

---

## Important Reminders

- Verify existing behavior before implementing new features.
- Keep runtime architecture explicit and simple.
- Automate repetitive developer workflows through tooling rather than adding
  runtime complexity.
- Do not move routing logic back into provider implementations.
- Do not allow application code to import vendor SDKs.
- Preserve anchor topology during repository modifications.
- Use the Green Build Rule before merge decisions.
- Commit stable checkpoints before large migrations.

---

## Known Risks

- Legacy provider-specific configuration may still exist in directives.
- Automated tests have not yet been rebuilt after the architecture migration.
- Baseline failover has not yet been implemented.
- Provider behavior needs validation against real workflows.

---

## Success Criteria

The next development session is successful when:

- `AI_PROVIDER` routing has been verified.
- Baseline failover is operational.
- Model resolution is centralized.
- Directive configuration is provider-independent.
- Automated tests cover the provider abstraction.
- Aurora passes manual regression validation.
- The provider abstraction branch is ready for review and merge into `main`.

<!-- ====================================================================== -->
<!-- END: SESSION_RESUME (PATCH 1 OF 1) -->
<!-- ====================================================================== -->