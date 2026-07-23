<!-- ====================================================================== -->
<!-- FILE: docs/hopehub/architecture/adr/ADR-002-django-rest-framework-api-layer.md (PATCH 1 OF 4) -->
<!-- START: ADR_HEADER_CONTEXT_AND_DECISION -->
<!-- ====================================================================== -->

# ADR-002 — Django REST Framework as the HopeHub API Layer

**Status:** Accepted

**Date:** 2026-07-15

**Project:** HopeHub

---

# Context

ADR-001 establishes that HopeHub will adopt an API-first domain architecture.

That architectural decision intentionally separates the long-term system design from the implementation technology used to expose HTTP APIs.

HopeHub is currently implemented as a Django application.

Its authentication system, administrative interface, deployment model, templates, and persistence layer are all built around Django.

Several implementation options exist for the API layer, including:

- Plain Django views with `JsonResponse`
- Django REST Framework
- A custom API framework
- A separate API service

While all of these approaches are technically viable, HopeHub should avoid rebuilding infrastructure that already exists in mature, well-supported software.

An API implementation requires consistent handling of:

- JSON request parsing
- Serialization
- Input validation
- Authentication integration
- Authorization
- Structured error responses
- Testing support
- Future API evolution

Building these capabilities manually would gradually recreate a less mature version of an existing framework.

---

# Decision

HopeHub will adopt **Django REST Framework (DRF)** as its standard HTTP API implementation layer.

Django REST Framework will provide:

- Request parsing
- Serialization
- API-facing validation
- Authentication integration
- Permission enforcement
- Consistent HTTP responses
- Endpoint abstractions
- API testing support

This decision does **not** change the architectural direction established by ADR-001.

Instead, it defines the implementation technology used to realize that architecture.

DRF will be introduced incrementally through complete HopeHub vertical slices rather than by converting the entire application at once.

The first implementation will be the Journal Entry creation workflow.

<!-- ====================================================================== -->
<!-- END: ADR_HEADER_CONTEXT_AND_DECISION (PATCH 1 OF 4) -->
<!-- ====================================================================== -->

<!-- ====================================================================== -->
<!-- FILE: docs/hopehub/architecture/adr/ADR-002-django-rest-framework-api-layer.md (PATCH 2 OF 4) -->
<!-- START: ARCHITECTURAL_BOUNDARY -->
<!-- ====================================================================== -->

# Architectural Boundary

Django REST Framework is the API transport and validation layer.

It is **not** the owner of HopeHub domain behavior.

The intended responsibility boundary is:

```text
Client
    ↓
DRF View
    ↓
DRF Serializer
    ↓
Domain Service
    ↓
Django Model
```

## DRF Views

Views are responsible for:

- Receiving HTTP requests
- Enforcing authentication
- Invoking permissions
- Passing validated requests into the application layer
- Returning HTTP responses

Views must not accumulate business logic.

---

## DRF Serializers

Serializers are responsible for:

- Translating between JSON and Python objects
- Validating request structure
- Validating field-level constraints
- Formatting response representations

Serializers should validate data.

They should **not** become substitutes for domain services.

---

## Domain Services

Domain services are responsible for:

- Applying business rules
- Coordinating model operations
- Enforcing workflow behavior
- Providing reusable behavior independent of HTTP

A domain service should be introduced whenever business behavior extends beyond straightforward validated model persistence.

---

## Django Models

Models remain responsible for:

- Persistence structure
- Database relationships
- Model-level invariants
- Behavior intrinsically associated with the entity

---

# Incremental Adoption

HopeHub will **not** convert every existing Django view before beta.

Instead, API adoption will proceed one complete vertical slice at a time.

The first slice will implement:

```text
POST /api/journal-entries/
```

The existing server-rendered journal list, edit, and delete workflows will remain operational while the create workflow validates the architecture.

Further journal operations will migrate only after the initial slice has been implemented and validated.

<!-- ====================================================================== -->
<!-- END: ARCHITECTURAL_BOUNDARY (PATCH 2 OF 4) -->
<!-- ====================================================================== -->

<!-- ====================================================================== -->
<!-- FILE: docs/hopehub/architecture/adr/ADR-002-django-rest-framework-api-layer.md (PATCH 3 OF 4) -->
<!-- START: AUTHENTICATION_AUTHORIZATION_AND_API_CONSTRAINTS -->
<!-- ====================================================================== -->

# Authentication

The initial browser-based API will use HopeHub's existing Django session authentication.

Requests that modify data must continue to use Django's CSRF protection.

Future mobile or external clients may require token-based authentication.

That decision will be documented separately when those clients exist.

This ADR does **not** authorize bypassing or weakening Django's existing authentication model.

---

# Authorization

Every journal API operation must enforce ownership on the server.

A client-provided user identifier must never determine ownership.

For journal creation:

```text
request.user
      ↓
JournalEntry.user
```

For retrieval, modification, and deletion, queries must always be restricted to objects owned by the authenticated user.

Client behavior must never be treated as an authorization mechanism.

---

# API Design Constraints

HopeHub APIs should:

- expose explicit resource-oriented endpoints
- return predictable HTTP status codes
- return structured validation errors
- avoid exposing internal implementation details
- preserve authentication and ownership boundaries
- remain only as large as required for the current vertical slice
- avoid speculative abstractions for future clients

The initial journal implementation does **not** require:

- ViewSets
- Routers
- Pagination
- Filtering
- Full CRUD conversion
- Versioning infrastructure

unless implementation demonstrates an immediate need.

The goal is to validate the architectural direction while keeping implementation as small as practical.

<!-- ====================================================================== -->
<!-- END: AUTHENTICATION_AUTHORIZATION_AND_API_CONSTRAINTS (PATCH 3 OF 4) -->
<!-- ====================================================================== -->

<!-- ====================================================================== -->
<!-- FILE: docs/hopehub/architecture/adr/ADR-002-django-rest-framework-api-layer.md (PATCH 4 OF 4) -->
<!-- START: CONSEQUENCES_AND_RATIONALE -->
<!-- ====================================================================== -->

# Consequences

## Benefits

- Integrates naturally with the existing Django application.
- Avoids custom serialization and validation infrastructure.
- Provides established authentication and permission mechanisms.
- Supports future browser, mobile, AI, and integration clients.
- Provides mature API testing capabilities.
- Reduces the risk of inconsistent endpoint behavior.
- Allows HopeHub to evolve without prematurely separating the API into another service.

---

## Tradeoffs

- Introduces another framework dependency.
- Adds DRF-specific concepts and conventions.
- Creates the temptation to place business logic inside serializers or ViewSets.
- Can encourage premature abstraction if the entire DRF feature set is adopted indiscriminately.

These risks will be controlled by implementing complete vertical slices and maintaining explicit architectural boundaries.

---

# Rejected Alternatives

## Plain Django JSON Views

Plain Django views can implement JSON endpoints, but HopeHub would gradually recreate mature functionality already provided by Django REST Framework.

That would increase custom code and long-term maintenance without creating meaningful product value.

---

## Separate API Service

A separate API service would introduce deployment, authentication, operational, and data-access complexity that is not justified for the HopeHub beta.

HopeHub will remain a Django application with an integrated DRF layer.

---

## Immediate Full CRUD Conversion

Converting every existing journal workflow before validating the first API slice would unnecessarily increase implementation scope and regression risk.

Journal Entry creation will validate the architecture before expanding to additional operations.

---

# Non-Goals

This ADR does **not** require:

- Immediate conversion of every Django view.
- Immediate development of a mobile application.
- Token authentication before non-browser clients exist.
- ViewSets for every resource.
- Routers for every endpoint.
- Generic repository abstractions.
- Microservices.
- Premature API versioning infrastructure.
- Domain services where no meaningful business behavior exists.

---

# Validation

This decision will be considered validated when the Journal Entry creation slice demonstrates that:

- An authenticated user can successfully create a journal entry through the API.
- Ownership is assigned exclusively from `request.user`.
- Invalid payloads return structured validation errors.
- CSRF protection remains active.
- The browser interface submits without requiring a full-page redirect.
- Existing journal list, edit, and delete functionality continues to operate.
- No business rules are duplicated in browser JavaScript.

---

# Rationale

Django REST Framework provides the mature API infrastructure HopeHub needs while remaining fully integrated with the existing Django architecture.

The decision favors proven engineering over custom plumbing while deliberately avoiding unnecessary complexity.

The guiding implementation philosophy is:

> Use Django REST Framework where HopeHub exposes APIs, but introduce only the amount of framework required by the current vertical slice.

HopeHub's architecture should evolve through working software rather than speculative infrastructure.

<!-- ====================================================================== -->
<!-- END: CONSEQUENCES_AND_RATIONALE (PATCH 4 OF 4) -->
<!-- ====================================================================== -->

