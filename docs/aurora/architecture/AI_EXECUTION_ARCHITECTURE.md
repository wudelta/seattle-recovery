# Aurora AI Execution Architecture

**Version:** 1.0

**Status:** Active

---

# Overview

Aurora's AI Execution Platform provides a vendor-independent, resilient, and configurable execution layer that allows the application to interact with multiple AI providers without exposing provider-specific implementation details to the remainder of the system.

The architecture is designed around four primary layers:

1. Application
2. Execution Engine
3. Provider Router
4. Provider Implementations

Each layer has a single, well-defined responsibility.

---

# High-Level Architecture

```text
+----------------------------------------------------------+
|                  Aurora Application                      |
|----------------------------------------------------------|
|                                                          |
|  Wu Chat                                                 |
|  Minions                                                 |
|  Workflows                                               |
|  Business Logic                                          |
|                                                          |
+---------------------------+------------------------------+
                            |
                            v
+----------------------------------------------------------+
|                 Minion Execution Engine                  |
|----------------------------------------------------------|
|                                                          |
|  Loads DeltaDirective                                    |
|  Builds AI request                                       |
|  Invokes Provider Router                                 |
|  Returns normalized response                             |
|                                                          |
+---------------------------+------------------------------+
                            |
                            v
+----------------------------------------------------------+
|                    Provider Router                       |
|----------------------------------------------------------|
|                                                          |
|  Provider Registry                                       |
|  Provider Selection                                      |
|  Model Resolution                                        |
|  Retry Policy                                            |
|  Failover                                                |
|  Provider Health                                         |
|  Metrics                                                 |
|                                                          |
+------------+---------------+---------------+-------------+
             |               |               |
             v               v               v

      OpenAI Provider   Gemini Provider   Anthropic Provider
             |               |               |
             v               v               v

        OpenAI SDK      Gemini SDK      Anthropic SDK
```

---

# Execution Flow

A typical request follows this sequence.

```text
User Request

↓

Minion

↓

DeltaDirective

↓

Execution Engine

↓

Provider Router

↓

Resolve Provider

↓

Resolve Model

↓

Provider

↓

Vendor SDK

↓

Normalized AI Response

↓

Application
```

The application never communicates directly with vendor SDKs.

---

# Layer Responsibilities

## 1. Application Layer

Responsible for:

* user interaction;
* workflows;
* minions;
* prompts;
* business logic.

The application is completely unaware of provider SDKs.

---

## 2. Execution Engine

Responsible for:

* loading directives;
* orchestrating execution;
* invoking the Provider Router;
* returning normalized responses.

The engine contains no vendor-specific logic.

---

## 3. Provider Router

The Provider Router is the policy engine of the AI subsystem.

Responsibilities include:

* provider registration;
* provider selection;
* provider priority;
* model resolution;
* retry policy;
* automatic failover;
* provider health tracking;
* execution metrics.

The router is the only component responsible for deciding where an AI request is executed.

---

## 4. Provider Implementations

Each provider implementation is responsible only for translating normalized requests into provider-specific SDK calls.

Providers:

* execute requests;
* normalize responses;
* normalize usage;
* normalize streaming.

Providers never:

* perform routing;
* perform retries;
* know about other providers;
* contain application logic.

---

# Configuration Ownership

| Configuration               | Owner                    |
| --------------------------- | ------------------------ |
| API Keys                    | `.env`                   |
| Active Provider             | `settings.py`            |
| Provider Priority           | `settings.py`            |
| Model Mapping               | `settings.py`            |
| Retry Policy                | `settings.py`            |
| DeltaDirective Instructions | Database                 |
| DeltaDirective Constraints  | Database                 |
| SDK Clients                 | Provider Implementations |

Each configuration value has a single owner.

---

# Provider Independence

The remainder of Aurora should never reference:

* OpenAI SDK
* Gemini SDK
* Anthropic SDK
* Vendor model names

These details are isolated entirely within the AI Execution Platform.

---

# Provider Failover

The router attempts providers according to configured priority.

Example:

```text
OpenAI

↓

Failure (503)

↓

Anthropic

↓

Success

↓

Return Response
```

The application receives a successful response without knowing a failover occurred.

---

# Normalized Response

Every provider returns a common response object.

Conceptually:

```text
AIResponse

text

provider

model

usage

metadata
```

This guarantees a stable interface regardless of provider.

---

# Design Principles

The AI Execution Platform follows these principles.

## Vendor Independence

Application code never depends on a specific provider.

---

## High Availability

No single provider failure should unnecessarily interrupt application execution.

---

## Configuration over Hardcoding

Routing policy belongs in configuration rather than application code.

---

## Single Responsibility

Each architectural component owns one clearly defined responsibility.

---

## Extensibility

New providers can be added without modifying application code.

---

## Stable Interfaces

Application code depends only on normalized interfaces.

---

# Future Roadmap

Future enhancements may include:

* provider health scoring;
* cost-aware routing;
* latency-aware routing;
* capability-aware model selection;
* load balancing;
* parallel provider execution;
* local LLM integration;
* execution analytics;
* distributed routing.

These enhancements extend the Provider Router without changing the architectural boundaries established by the current design.

---

# Summary

Aurora's AI Execution Platform separates **application logic**, **execution policy**, and **provider implementations** into independent layers.

This separation provides:

* vendor independence;
* simplified maintenance;
* automatic provider failover;
* centralized execution policy;
* straightforward provider expansion;
* a stable foundation for future AI capabilities.

The architecture is intended to evolve through additional providers and routing strategies while preserving a consistent interface for the remainder of the Aurora application.
