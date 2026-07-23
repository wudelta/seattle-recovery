# ADR-002 — Provider Routing & Failover

**Status:** Accepted (Baseline)

**Date:** 2026-07-07

---

# Context

ADR-001 establishes the AI Execution Platform and defines the Provider Router as the central authority responsible for AI execution policy.

This ADR defines how the Provider Router selects providers, resolves models, detects failures, and maintains application availability during provider outages.

The primary design objective is to eliminate a single point of failure within Aurora's AI subsystem.

---

# Motivation

Aurora originally communicated directly with a single AI provider.

Operational experience revealed several failure modes outside the application's control, including:

* Provider overload (HTTP 503 UNAVAILABLE)
* Rate limiting
* Temporary network failures
* Provider maintenance windows
* Billing interruptions
* Quota exhaustion

Although these failures originate outside Aurora, they should not unnecessarily interrupt user workflows when alternative providers are available.

---

# Decision

Aurora shall introduce a Provider Router responsible for all provider selection and routing decisions.

The router shall act as the sole entry point into every AI provider implementation.

The execution engine will never communicate directly with provider implementations.

---

# Provider Router Responsibilities

The Provider Router owns:

* provider discovery;
* provider registration;
* provider enablement;
* provider priority;
* model resolution;
* provider selection;
* retry policy;
* automatic failover;
* provider health status;
* execution metrics.

No other component shall perform these responsibilities.

---

# Provider Registration

Each provider implementation registers itself with the router.

Example conceptually:

```text
OpenAIProvider

GeminiProvider

AnthropicProvider

MockProvider
```

Adding a new provider should require:

1. implementing the provider interface;
2. registering the provider;
3. supplying provider configuration.

No application code should require modification.

---

# Provider Priority

Provider selection shall be determined through configuration.

Example:

```text
Priority

1 OpenAI

2 Anthropic

3 Gemini
```

The router attempts providers in priority order until a successful execution occurs or all providers fail.

---

# Model Resolution

Application code shall never contain vendor-specific model names.

Instead, the router shall resolve execution intent into provider-specific model names using centralized configuration.

Conceptually:

```text
Execution Level

low

medium

high
```

↓

```text
OpenAI

low → GPT-5.5 Mini

medium → GPT-5.5

high → GPT-5.5
```

↓

```text
Gemini

low → Gemini Flash

medium → Gemini Pro

high → Gemini Thinking
```

The exact configuration mechanism is defined separately.

---

# Failover Policy

The router shall attempt failover only when the failure is considered recoverable.

Examples include:

* HTTP 429
* HTTP 503
* connection failures
* gateway timeouts
* temporary network errors
* provider service interruptions
* quota exhaustion
* billing interruptions

The router shall immediately attempt the next provider in priority order.

---

# Non-Recoverable Errors

The router shall not automatically fail over when failures originate from the application itself.

Examples include:

* malformed requests;
* programming errors;
* invalid configuration;
* unsupported parameters;
* invalid directives.

These errors should be reported immediately to the caller.

---

# Provider Health

The router shall maintain an in-memory health record for each provider.

Example conceptual state:

```text
Provider

Healthy

Unavailable

Cooldown

Retry After
```

Providers experiencing repeated failures may be temporarily skipped until their cooldown period expires.

Persistent storage of provider health is intentionally out of scope for the baseline.

---

# Execution Flow

Conceptually:

```text
Execution Engine

↓

Provider Router

↓

Resolve Execution Policy

↓

Resolve Provider

↓

Resolve Model

↓

Execute

↓

Success?

↓

Yes → Return Response

↓

No

↓

Retry Eligible?

↓

Yes

↓

Next Provider

↓

No

↓

Return Failure
```

---

# Provider Responsibilities

Provider implementations remain intentionally simple.

Providers:

* execute requests;
* translate SDK calls;
* normalize responses;
* normalize streaming.

Providers shall never:

* perform routing;
* select alternate providers;
* retry other providers;
* own execution policy.

---

# Logging

The router should record:

* selected provider;
* selected model;
* execution duration;
* failover attempts;
* provider failures;
* final execution result.

These metrics provide operational visibility while remaining independent of provider implementations.

---

# Consequences

The Provider Router becomes Aurora's central AI execution policy engine.

Future enhancements—including intelligent routing, cost optimization, capability-aware routing, load balancing, and distributed execution—can be added within the router without affecting the application or provider implementations.

---

# Future Considerations

Future enhancements may include:

* dynamic provider scoring;
* cost-aware routing;
* latency-aware routing;
* provider capability discovery;
* parallel execution strategies;
* circuit breakers;
* persistent health monitoring.

These enhancements extend the router rather than altering the architectural responsibilities established by this ADR.
