# ADR-001 — AI Execution Architecture

**Status:** Accepted (Baseline)

**Date:** 2026-07-07

---

# Context

Aurora began with a direct integration to a single AI provider (Google Gemini). As the application matured, several architectural limitations became apparent:

* Aurora became tightly coupled to a single vendor SDK.
* AI model names became embedded throughout the application.
* Provider outages (503 UNAVAILABLE), quota exhaustion, and billing interruptions could halt AI-assisted workflows.
* Supporting additional providers required invasive application changes.
* The application lacked a consistent abstraction for interacting with AI services.

The objective of this ADR is to establish a permanent architectural foundation that allows Aurora to interact with multiple AI providers while insulating the remainder of the application from vendor-specific implementations.

---

# Mission Statement

**Aurora's AI Execution Platform provides a vendor-independent, resilient, and configurable execution layer that routes AI workloads to the most appropriate available provider while insulating the application from provider-specific SDKs, models, and service failures.**

This statement serves as the guiding principle for all future AI-related development.

---

# Architectural Goals

The AI Execution Platform shall:

* support multiple AI providers simultaneously;
* eliminate vendor-specific logic from application code;
* provide automatic provider failover;
* support configurable provider priorities;
* centralize AI execution policy;
* normalize provider responses into a common interface;
* minimize vendor lock-in;
* allow future providers to be added with minimal code changes.

---

# Architecture

```
Aurora Application
        │
        ▼
 MinionRunner (Execution Engine)
        │
        ▼
 Provider Router
        │
        ├──────────────┐
        │              │
        ▼              ▼
 OpenAI Provider   Gemini Provider
        │              │
        ▼              ▼
 OpenAI SDK       Gemini SDK
```

Future providers (Anthropic, Azure OpenAI, Ollama, local models, etc.) become additional provider implementations without requiring changes to the application layer.

---

# Layer Responsibilities

## Application Layer

Responsible for:

* workflows
* minions
* directives
* prompts
* business logic

The application **must never communicate directly with vendor SDKs.**

---

## Execution Engine

Responsible for:

* orchestrating AI execution;
* obtaining directives;
* invoking the Provider Router;
* exposing normalized results to the application.

The engine is intentionally unaware of provider-specific implementation details.

---

## Provider Router

Responsible for:

* selecting the provider;
* resolving execution policy;
* resolving provider-specific models;
* managing provider priority;
* automatic failover;
* provider health monitoring;
* retry decisions.

The router owns AI execution policy.

---

## Provider Implementations

Each provider is responsible solely for translating normalized requests into SDK-specific API calls.

Providers:

* communicate with vendor SDKs;
* normalize responses;
* normalize usage statistics;
* normalize streaming behavior.

Providers must not:

* know about other providers;
* perform routing;
* perform failover;
* contain application business logic.

---

# Design Principles

The AI Execution Platform follows these principles:

1. Separation of Concerns
2. Vendor Independence
3. Single Responsibility
4. Configuration over Hardcoding
5. High Availability
6. Extensibility
7. Stable Interfaces

---

# Non-Goals

This architecture intentionally does not include:

* load balancing;
* cost optimization;
* intelligent provider selection;
* parallel execution across providers;
* distributed routing;
* persistent provider health storage.

These may be added in future revisions without altering the architectural boundaries established by this ADR.

---

# Consequences

Implementation will include:

* provider interface abstraction;
* provider registry;
* provider router;
* normalized AI response objects;
* removal of direct SDK usage outside provider classes.

Existing Gemini-specific logic throughout the application will be refactored into provider implementations.

---

# Success Criteria

The architecture is considered complete when:

* switching AI providers requires only configuration changes;
* new providers can be added without modifying application code;
* vendor SDKs are isolated within provider classes;
* the execution engine contains no vendor-specific logic;
* provider failures do not necessarily result in application failures.

---

# Future Considerations

Future ADRs will define:

* provider routing strategy;
* provider failover policy;
* directive configuration schema;
* provider capability discovery;
* execution telemetry and metrics.

This ADR intentionally establishes the architectural foundation without prescribing implementation details for those subsystems.
