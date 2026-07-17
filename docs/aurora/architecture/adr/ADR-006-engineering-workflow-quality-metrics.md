# ADR-006 — Engineering Workflow Quality Metrics

**Status:** Accepted

**Date:** 2026-07-16

---

## Context

Traditional AI-assisted development measures the capabilities of the language model.

Aurora's objective is different.

The platform should measure the quality and efficiency of the engineering process itself.

Reliable engineering results from deterministic workflows, validation checkpoints, and repeatable execution—not solely from model capability.

Today's implementation session demonstrated this principle.

A substantial subsystem was implemented without:

* syntax errors
* runtime crashes
* migration failures
* copy/paste mistakes
* debugging loops

The improvements resulted from workflow discipline rather than changes in AI capability.

---

## Decision

Aurora shall collect engineering metrics describing development workflow quality.

Metrics should be generated automatically whenever practical.

The objective is continuous improvement of the engineering system rather than evaluation of AI models.

---

## Initial Metrics

### Session Metrics

* Session duration
* Components completed
* Patches generated
* Patches applied
* Commits created

---

### Validation Metrics

* Syntax errors
* Django check failures
* Migration failures
* Runtime exceptions
* Regression failures

---

### Workflow Metrics

* Rollback events
* Manual patch repairs
* Protocol deviations
* Interrupted workflows
* Copy/paste corrections

---

### Engineering Quality Metrics

* Behavioral refinements
* Debugging loops
* Architecture decisions
* Deterministic workflow coverage

---

### AI Utilization Metrics

* AI requests
* Token consumption
* Estimated deterministic work performed
* Estimated AI work avoided

---

## Goals

These metrics are intended to:

* improve engineering throughput
* reduce debugging effort
* lower AI operating costs
* increase workflow reliability
* support grant applications and funding proposals
* demonstrate measurable productivity improvements

---

## Guiding Principle

Aurora measures engineering effectiveness rather than AI intelligence.

The success of the platform is determined by the quality, predictability, and efficiency of software delivery.

---

## Baseline Session

**2026-07-16** is designated as the first baseline deterministic engineering session.

This session demonstrated:

* Zero syntax errors
* Zero runtime crashes
* Zero debugging loops
* Zero protocol deviations
* Successful incremental migration
* Successful deterministic workspace reconciliation implementation
* Localized behavioral refinements instead of emergency defect repair

Future workflow improvements should be measured relative to this baseline.

---

## Long-Term Vision

Engineering metrics should eventually be displayed within Aurora itself, allowing developers to monitor project health, workflow efficiency, deterministic coverage, AI utilization, and engineering quality over time.

The objective is to create a self-improving engineering platform whose effectiveness can be demonstrated quantitatively rather than anecdotally.
