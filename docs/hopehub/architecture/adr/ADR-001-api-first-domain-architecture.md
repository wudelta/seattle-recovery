<!-- ====================================================================== -->
<!-- FILE: docs/hopehub/architecture/adr/ADR-001-api-first-domain-architecture.md (PATCH 1 OF 4) -->
<!-- START: ADR_HEADER_CONTEXT_AND_DECISION -->
<!-- ====================================================================== -->

# ADR-001 — API-First Domain Architecture

**Status:** Accepted

**Date:** 2026-07-15

**Project:** HopeHub

---

# Context

HopeHub is intended to begin as a responsive web application while preserving the ability to evolve naturally into native mobile applications, AI-assisted workflows, and external integrations without requiring architectural redesign.

Traditional Django applications commonly bind business workflows directly to:

- ModelForms
- Generic Class-Based Views
- HTML templates
- Redirect-based request/response cycles

While this approach is appropriate for many server-rendered applications, it tightly couples presentation, validation, business behavior, and navigation into a single implementation.

As HopeHub grows, multiple clients will require access to the same domain capabilities, including:

- Responsive web browsers
- Future Android and iOS applications
- AI assistants operating on behalf of users
- Administrative tooling
- Background automation
- Potential third-party integrations

These clients should consume the same domain behavior rather than requiring independent implementations.

---

# Decision

HopeHub adopts an **API-First Domain Architecture**.

Business capabilities will be implemented behind stable application APIs.

User interfaces become consumers of those APIs rather than the location where business behavior is implemented.

The API becomes the long-term contract of the system.

The browser is the first client of that contract.

Future clients become additional consumers rather than requiring architectural redesign.

<!-- ====================================================================== -->
<!-- END: ADR_HEADER_CONTEXT_AND_DECISION (PATCH 1 OF 4) -->
<!-- ====================================================================== -->

<!-- ====================================================================== -->
<!-- FILE: docs/hopehub/architecture/adr/ADR-001-api-first-domain-architecture.md (PATCH 2 OF 4) -->
<!-- START: ARCHITECTURAL_PRINCIPLES_PART_1 -->
<!-- ====================================================================== -->

# Architectural Principles

## 1. Business Logic is UI Independent

Business rules must not depend upon:

- HTML templates
- Django forms
- JavaScript
- Redirect behavior

Presentation layers may validate user experience but must not own domain rules.

---

## 2. APIs Define System Behavior

Each major HopeHub capability should expose an explicit API contract.

Examples include:

- Journal
- Resources
- Case Management
- Messaging
- Notifications

The API represents the supported behavior of the system.

---

## 3. User Interfaces Consume APIs

The browser interface should communicate through APIs whenever practical.

This enables:

- asynchronous interactions
- responsive mobile experiences
- reduced page refreshes
- reusable backend services

Server-rendered pages remain acceptable when they improve simplicity or operational reliability.

API-first does **not** require eliminating server-rendered HTML.

<!-- ====================================================================== -->
<!-- END: ARCHITECTURAL_PRINCIPLES_PART_1 (PATCH 2 OF 4) -->
<!-- ====================================================================== -->

<!-- ====================================================================== -->
<!-- FILE: docs/hopehub/architecture/adr/ADR-001-api-first-domain-architecture.md (PATCH 3 OF 4) -->
<!-- START: ARCHITECTURAL_PRINCIPLES_PART_2_AND_INITIAL_APPLICATION -->
<!-- ====================================================================== -->

## 4. Authentication Remains Centralized

Authentication and authorization continue to be enforced by the server.

Ownership validation must remain independent of the consuming client.

Every API endpoint must validate:

- authenticated user
- object ownership
- permissions
- business constraints

Clients are never trusted.

---

## 5. Domain Logic Lives Outside Transport Layers

HTTP is a transport mechanism.

Business behavior belongs in reusable domain services rather than:

- UpdateView
- CreateView
- DeleteView
- JavaScript
- Mobile client code

Future transports should reuse the same business implementation.

A separate domain service should be introduced when meaningful business behavior exists beyond straightforward validated persistence.

---

## 6. Vertical Slice Development

Features are implemented as complete vertical slices.

Each slice includes:

- user workflow
- API contract
- authentication
- authorization
- business logic
- persistence
- user experience
- validation criteria

The first implementation should be the smallest complete slice capable of validating the architecture.

---

# Initial Application

The first implementation of this architecture will be the Journal feature.

Current implementation:

```text
Browser
    ↓
ModelForm
    ↓
UpdateView
    ↓
JournalEntry
```

Target direction:

```text
Browser
    ↓
Journal API
    ↓
Journal Domain Behavior
    ↓
JournalEntry
```

The initial migration will focus on Journal Entry creation while preserving the existing list, edit, and delete workflows until the API architecture has been validated.

The first vertical slice will demonstrate:

- authenticated API access
- CSRF-protected browser submission
- server-controlled ownership
- structured validation errors
- responsive asynchronous interaction
- preservation of existing journal behavior

<!-- ====================================================================== -->
<!-- END: ARCHITECTURAL_PRINCIPLES_PART_2_AND_INITIAL_APPLICATION (PATCH 3 OF 4) -->
<!-- ====================================================================== -->

<!-- ====================================================================== -->
<!-- FILE: docs/hopehub/architecture/adr/ADR-001-api-first-domain-architecture.md (PATCH 4 OF 4) -->
<!-- START: CONSEQUENCES_NON_GOALS_AND_RATIONALE -->
<!-- ====================================================================== -->

# Consequences

## Benefits

- Mobile-ready architecture from the beginning.
- Stable contracts between clients and server.
- Separation of presentation from business behavior.
- Reusable backend capabilities across browser, mobile, AI, and integration clients.
- Reduced duplication as additional clients are introduced.
- Easier automated testing of API contracts and domain behavior.
- Lower risk of the web interface becoming the permanent architectural boundary.

---

## Tradeoffs

- Requires more design discipline than direct form-to-model workflows.
- Introduces API contracts that must remain stable and intentional.
- Some features may temporarily exist in both server-rendered and API-driven forms during migration.
- Adds implementation work before visible user-interface changes appear.
- Creates a risk of unnecessary abstraction if APIs and services are designed beyond current requirements.

These tradeoffs will be controlled through narrow vertical slices and The Delta Way.

---

# Non-Goals

This ADR does **not** require:

- elimination of server-rendered pages
- immediate conversion of every HopeHub workflow
- immediate creation of a mobile application
- immediate token-based authentication
- microservices
- a separate API deployment
- speculative abstractions for unimplemented clients
- domain services where straightforward validated persistence is sufficient

The objective is to establish architectural direction while preserving incremental delivery.

Framework selection is documented separately so the API-first principle remains independent of its implementation technology.

---

# Future Considerations

Subsequent architectural decisions may define:

- API implementation framework
- endpoint and resource conventions
- API versioning strategy
- domain service boundaries
- standard error response formats
- authentication for mobile and external clients
- offline synchronization behavior
- AI integration boundaries
- audit and privacy requirements

These decisions should be made only when demanded by a concrete HopeHub vertical slice.

---

# Validation

This decision will be considered validated when the first Journal Entry vertical slice demonstrates that:

- the browser can create an entry through an API
- the server derives ownership from the authenticated user
- authentication and CSRF protections remain active
- invalid input produces structured and usable errors
- the interface works without a full-page form submission
- existing journal behavior remains operational
- domain rules are not duplicated in client code
- the implementation remains small enough to support the beta deadline

---

# Rationale

HopeHub is intended to become more than a traditional website.

Its capabilities may eventually be consumed by responsive browsers, native mobile applications, AI collaborators, background processes, administrative tools, and external integrations.

Those clients should share one authoritative implementation of HopeHub behavior.

The browser is the first client.

It should not become the architecture.

<!-- ====================================================================== -->
<!-- END: CONSEQUENCES_NON_GOALS_AND_RATIONALE (PATCH 4 OF 4) -->
<!-- ====================================================================== -->