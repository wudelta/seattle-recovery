<!-- ====================================================================== -->
<!-- FILE: docs/aurora/architecture/adr/ADR-004-development-automation-over-runtime-complexity.md (PATCH 1 OF 1) -->
<!-- START: ADR -->
<!-- ====================================================================== -->

# ADR-004: Development Automation Over Runtime Complexity

**Status:** Accepted

**Date:** 2026-07-09

---

## Context

As Aurora grows, repetitive engineering tasks increasingly require coordinated
changes across multiple files. Examples include adding AI providers, pages,
APIs, workflows, and other architectural components.

Several approaches were considered.

One approach was to make the runtime architecture increasingly dynamic through
automatic discovery, reflection, or implicit registration.

Another was to keep the runtime architecture explicit while automating
deterministic development tasks through scaffolding and slash commands.

---

## Decision

Aurora will favor explicit runtime architecture.

When repetitive engineering work follows a well-defined, deterministic pattern,
the preferred solution is to automate the development workflow rather than add
complexity to the production runtime.

Slash commands are considered part of Aurora's development platform.

They encode established project conventions and generate consistent scaffolding,
allowing developers to focus on implementation rather than boilerplate.

Automation should be considered when a task:

- requires coordinated changes across multiple repository files;
- typically takes approximately one hour or more to perform manually;
- is expected to be repeated multiple times;
- has a canonical implementation pattern.

---

## Consequences

### Benefits

- Runtime behavior remains explicit and easy to understand.
- Boilerplate is generated consistently.
- Project conventions become executable rather than tribal knowledge.
- Token consumption is reduced by replacing repeated reasoning with deterministic workflows.
- New contributors can produce Aurora-consistent code without memorizing project structure.

### Tradeoffs

- Aurora must maintain its scaffolding commands alongside the project.
- Generated scaffolding may occasionally require updates as architectural conventions evolve.

---

## Guiding Principle

Prefer simple runtime behavior and powerful development tooling.

The objective is not to eliminate boilerplate through hidden runtime behavior,
but to eliminate repetitive manual work through deterministic automation.

Aurora exists to accelerate the delivery of software—not to become an end in
itself.

<!-- ====================================================================== -->
<!-- END: ADR -->
<!-- ====================================================================== -->