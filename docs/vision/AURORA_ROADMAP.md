<!-- ====================================================================== -->
<!-- FILE: docs/vision/AURORA_ROADMAP.md (PATCH 1 OF 1) -->
<!-- START: AURORA_ROADMAP -->
<!-- ====================================================================== -->

# Aurora Roadmap

Aurora is being developed in deliberate phases. Each phase has a specific purpose and a clear stopping point. The objective is to build only what is needed to accomplish the next milestone while preserving a long-term architectural vision.

---

# Phase 1 — Aurora Baseline

## Goal

Complete a stable, vendor-independent AI Execution Platform.

The immediate objective is to validate and harden the provider abstraction, complete baseline failover, centralize model resolution, rebuild automated tests, and merge the architecture into `main`.

### Completion Criteria

- AI Execution Platform validated
- Provider abstraction complete
- Provider failover operational
- Model resolution centralized
- Automated regression tests restored
- Stable merge into `main`

Target:

**July 15, 2026**

---

# Phase 2 — HopeHub Beta

## Goal

Use Aurora to build and deploy the first public HopeHub beta.

During this phase, Aurora development should be limited to improvements that are:

- required to complete HopeHub;
- reusable by both Aurora and HopeHub through `core_logic`; or
- necessary to maintain developer productivity.

Aurora becomes the internal engineering console used to design, operate, and evolve HopeHub while intentionally avoiding unrelated platform expansion.

## Security & Identity

Before HopeHub enters public production, Aurora and HopeHub must support shared authentication with independent authorization.

Although both applications share the same user database, access to Aurora must be explicitly granted.

Minimum production requirements include:

- Aurora application access restricted by group membership.
- Role-based authorization for privileged operations.
- Separation between application authentication and authorization.
- Administrative capabilities isolated from standard HopeHub users.
- Security review of all Aurora endpoints prior to production deployment.

The mission is to deliver a working product, not expand the platform.

Target:

**August 15, 2026**

---

# Phase 3 — Knowledge Layer

## Goal

Evolve the Project Brain from a collection of Markdown documents into a persistent engineering knowledge system.

Rather than relying exclusively on static documentation, Aurora should retain engineering history as structured knowledge.

Candidate knowledge domains include:

- Session history
- Daily accomplishments
- Decisions
- Experiments
- Failed approaches
- Research notes
- AI conversations
- Design ideas
- TODOs
- Metrics
- Searchable knowledge
- Engineering patterns
- Relationships between artifacts

Repository documentation should continue describing the project's current state.

The Knowledge Layer should preserve how the project arrived there.

### Architectural Direction

Current thinking favors:

- **Neo4j** for highly connected engineering knowledge.
- **PostgreSQL** for operational application data.

This is intentionally **not** an architectural commitment. The final implementation should be informed by real development experience following the HopeHub beta rather than designed prematurely.

Status:

**Planned**

---

# Phase 4 — Decision Engine

## Goal

Teach Aurora the development methodology rather than simply generating code.

The long-term objective is for Aurora to make consistent engineering decisions by combining:

- architectural principles;
- project history;
- documented patterns;
- accumulated engineering knowledge;
- established development protocols; and
- operational feedback from real-world development.

The decision engine is expected to become Aurora's primary differentiator rather than any particular AI model or provider.

Status:

**Vision**

---

# Guiding Principles

- Finish the current mission before expanding the platform.
- Build capabilities when they solve demonstrated problems.
- Keep authentication separate from authorization.
- Automate deterministic engineering work.
- Preserve engineering knowledge.
- Prefer methodology over model-specific intelligence.
- Keep the repository focused on implementation.
- Allow the Knowledge Layer to become Aurora's long-term memory.

> **Technology is not the product. Methodology is the product.**

<!-- ====================================================================== -->
<!-- END: AURORA_ROADMAP (PATCH 1 OF 1) -->
<!-- ====================================================================== -->