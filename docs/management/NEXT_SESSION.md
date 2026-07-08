# Next Development Session

## Immediate Objective

Implement the Provider Router as the foundation of the AI Execution Platform.

This is the next architectural milestone and should be completed before additional provider implementations or execution engine refactoring.

---

## Resume Order

1. Design and implement the Provider Router.
2. Refactor the existing MockProvider into the SimulatedProvider reference implementation.
3. Complete the OpenAIProvider.
4. Complete the GeminiProvider.
5. Refactor `engine.py` to delegate all provider selection to the Provider Router.
6. Migrate `DeltaDirectives.constraints` to the provider-independent schema.
7. Perform manual validation.
8. Rebuild automated tests.
9. Achieve a green build.
10. Commit and merge into `main`.

---

## Important Reminders

* The Provider Router owns provider selection, model resolution, retry policy, and failover.
* Provider implementations are responsible only for translating between Aurora's `AIProvider` interface and vendor SDKs.
* No application code may depend directly on a vendor SDK.
* The SimulatedProvider is the canonical reference implementation for the `AIProvider` interface.
* Preserve streaming behavior, usage accounting, and existing application functionality throughout the refactor.

---

## Success Criteria

The next development session is successful when:

* The Provider Router has been implemented.
* The architecture remains consistent with the approved ADRs.
* The project is ready to begin completing provider implementations without further architectural redesign.
