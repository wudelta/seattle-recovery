# The Delta Way

> *Done fast. Done cheap. Done right. Pick any two.*
>
> **Aurora chooses cheap and right.**

---

# Purpose

The Delta Way defines the engineering philosophy behind Aurora.

It is not a coding standard, an architecture document, or a project plan.

It is the collection of principles that govern how engineering decisions are made throughout the project.

Technology will change.

Frameworks will change.

AI models will change.

The philosophy should remain stable.

---

# Build for the Long Term

Aurora is not being built as a demonstration project.

Every subsystem should be capable of remaining in production for years.

Temporary shortcuts that create long-term maintenance costs are discouraged.

A feature delivered one week later is acceptable.

A fragile architecture that requires continual repair is not.

---

# Cheap and Right

Engineering is constrained by two finite resources:

* time
* money

AI usage has a direct cost.

Developer time has an even greater cost.

Whenever possible:

Choose the solution that is correct and sustainable, even if implementation takes longer.

Speed should emerge from accumulated engineering quality rather than rushed implementation.

---

# Small Failures Are Valuable

Failure is expected.

Large failures are not.

Every experiment should be small enough that failure teaches something specific.

Losing an hour is acceptable.

Losing two days because too many unrelated changes were attempted simultaneously is not.

The objective is not to eliminate failure.

The objective is to minimize the cost of failure.

---

# Limit the Blast Radius

Every change should disturb as little of the system as possible.

When modifying complex subsystems:

* isolate the change
* verify the result
* create a checkpoint
* continue

Large changes should be decomposed into independently verifiable steps.

---

# Understand Before Modifying

Code should not be changed until its purpose is understood.

When working in unfamiliar areas:

* inspect existing implementation
* understand responsibilities
* identify subsystem boundaries
* ask questions when intent is unclear

Implementation follows understanding.

Never the reverse.

---

# Baseline Before Optimization

Architecture earns the right to expand by first proving that it works.

Complete the baseline.

Validate the baseline.

Only then introduce additional abstractions, automation, or optimization.

Ideas are never lost.

Premature implementation is avoided.

---

# The Repository Is the Source of Truth

Conversations are temporary.

Documentation is durable.

Architectural knowledge belongs inside the repository.

Important decisions should survive both AI sessions and human memory.

---

# Context Is Loaded on Demand

Neither humans nor AI should carry unnecessary context.

Only the information required for the current task should be loaded.

This reduces complexity, improves focus, lowers AI costs, and encourages modular design.

---

# Every Change Needs a Recovery Path

Before making significant modifications, there should be a practical path back to a known good state.

Git checkpoints are part of the engineering process, not an afterthought.

Recovery is a feature.

---

# Engineering Over Heroics

Aurora should never depend upon extraordinary effort.

The project should advance through repeatable engineering practices rather than heroic debugging sessions.

Consistent progress is preferred over dramatic progress.

---

# Continuous Learning

Every difficult debugging session should improve Aurora itself.

When a recurring lesson is discovered:

* improve the architecture
* improve the documentation
* improve the workflow

The project should become easier to develop over time.

---

# The Goal

Aurora is intended to become an engineering platform.

The quality of the platform is determined as much by the way it is built as by the features it contains.

The Delta Way exists to ensure that every engineering decision moves the project toward a system that is understandable, maintainable, resilient, and capable of evolving for many years.
