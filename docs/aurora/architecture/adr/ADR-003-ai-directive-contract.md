# ADR-003 — AI Directive Contract

**Status:** Accepted (Baseline)

**Date:** 2026-07-07

---

# Context

The `DeltaDirectives` model defines how Aurora's AI-powered minions execute work. Prior to the Provider Abstraction Initiative, the `constraints` JSON field contained vendor-specific configuration such as Gemini model names.

As Aurora evolved into a provider-independent AI Execution Platform, embedding vendor-specific information inside application directives created an architectural conflict.

This ADR establishes the contract between the Aurora application layer and the AI Execution Platform.

---

# Problem Statement

The application should describe **what it needs**, not **how a specific AI vendor provides it**.

For example, this is an implementation detail:

```json
{
    "model": "gemini-2.5-flash"
}
```

The application should not know that model exists.

Likewise:

```json
{
    "model": "gpt-5.5"
}
```

is equally vendor-specific.

Vendor model names are implementation details belonging to the AI Execution Platform.

---

# Decision

`DeltaDirectives.constraints` shall contain **provider-independent execution intent**.

It shall never contain:

* vendor names;
* SDK-specific options;
* provider-specific model names;
* API keys;
* routing decisions.

The AI Execution Platform is responsible for translating execution intent into provider-specific implementation details.

---

# Ownership of Configuration

The following table defines architectural ownership.

| Configuration         | Owner                     |
| --------------------- | ------------------------- |
| Prompt Instructions   | DeltaDirectives           |
| Execution Intent      | DeltaDirectives           |
| Temperature           | DeltaDirectives           |
| Maximum Output Tokens | DeltaDirectives           |
| Streaming Preference  | DeltaDirectives           |
| Active Provider       | Application Configuration |
| Provider Priority     | Provider Router           |
| Model Resolution      | Provider Router           |
| Retry Policy          | Provider Router           |
| Failover Policy       | Provider Router           |
| API Keys              | Environment Configuration |
| SDK Translation       | Provider Implementation   |

Each configuration value shall have exactly one owner.

---

# Execution Intent

Rather than describing vendor models, directives describe the nature of the work to be performed.

Conceptually:

```json
{
    "execution_level": "low",
    "temperature": 0.1,
    "max_output_tokens": 1200
}
```

The exact vocabulary may evolve over time.

Examples include:

* low
* medium
* high

or

* simple
* standard
* advanced

The execution vocabulary intentionally remains vendor-independent.

---

# Model Resolution

The router translates execution intent into provider-specific models.

Conceptually:

```text
Execution Level

↓

Provider Router

↓

Provider Model

↓

Provider SDK
```

The application never performs this translation.

---

# Extensibility

Adding a new AI provider shall not require changes to existing directives.

Only the Provider Router configuration should require updates.

This ensures that existing minions continue functioning regardless of which providers are available.

---

# Stable Contract

The application shall communicate only through normalized structures.

The engine receives:

* instructions;
* execution constraints;
* prompt content.

The engine never receives:

* SDK objects;
* provider-specific requests;
* vendor-specific model names.

Likewise, the application receives only normalized responses regardless of which provider generated them.

---

# Backward Compatibility

During the Provider Abstraction migration, existing directives containing vendor-specific model names may be migrated to the new execution intent schema.

Because Aurora currently has a limited number of active directives, this migration is considered low risk and will be completed as part of the baseline implementation.

---

# Design Principles

The directive contract follows these principles:

* describe intent rather than implementation;
* remain provider-independent;
* minimize future migration effort;
* maintain stable application interfaces;
* support future provider expansion without modifying application code.

---

# Consequences

Future AI providers can be introduced without modifying:

* database schema;
* application workflows;
* minion implementations;
* execution engine.

Only the Provider Router configuration and provider implementation require updates.

This significantly reduces future maintenance effort and strengthens Aurora's long-term architectural stability.

---

# Future Considerations

Future versions of the execution intent vocabulary may become more expressive as Aurora evolves.

Possible future attributes include:

* reasoning complexity;
* context requirements;
* latency preference;
* deterministic execution;
* structured output preference;
* multimodal capability requirements.

These additions shall remain provider-independent and continue to describe application intent rather than provider implementation.
