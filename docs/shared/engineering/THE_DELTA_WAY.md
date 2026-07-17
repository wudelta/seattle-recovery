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

Engineering is constrained by three finite resources:

* time
* money
* attention

Attention is often the most valuable of the three.

Every debugging loop, unnecessary context switch, repeated explanation, or avoidable investigation consumes attention that could have been invested in better architecture.

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

# Separate Thinking from Building

Architecture should be decided before implementation begins.

Implementation should execute an approved plan rather than discover one.

Questions, challenges, alternatives, and design discussions belong before coding.

Once implementation begins, engineering should proceed through small, deterministic steps whose purpose has already been agreed upon.

Planning is creative.

Implementation is disciplined.

Both deserve their own time.

---

# Baseline Before Optimization

Architecture earns the right to expand by first proving that it works.

Complete the baseline.

Validate the baseline.

Only then introduce additional abstractions, automation, or optimization.

Ideas are never lost.

Premature implementation is avoided.

---

# Deterministic Before Intelligent

Whenever software can solve a problem deterministically, software should solve it.

AI should augment deterministic systems rather than replace them.

Repository discovery, validation, workflow execution, context selection, and engineering automation should be implemented as repeatable software systems whenever practical.

Intelligence should be reserved for problems that genuinely require interpretation, reasoning, creativity, or communication.

Aurora should not ask AI to remember what software can record.

Aurora should not ask AI to infer what software can compute.

Aurora should not ask AI to discover what software can index.

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

# Validate Continuously

Engineering confidence should be built incrementally.

Every completed step should demonstrate one additional property of the system before the next step begins.

Small validations prevent large debugging sessions.

The objective is not simply to discover defects quickly.

The objective is to prevent uncertainty from accumulating.

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

Aurora should become easier to engineer with every completed engineering session.

Every improvement to the platform should reduce future effort, reduce uncertainty, or increase the reliability of the engineering process itself.

The platform is not only the product being built.

It is also the means by which future products will be built.

---

# In Practice

The Delta Way is reflected in every engineering session.

The workflow is intentionally divided into distinct phases:

1. Define the problem.
2. Establish the architectural objective.
3. Design an implementation strategy.
4. Challenge assumptions and refine the plan.
5. Implement in small, bounded steps.
6. Validate continuously.
7. Reach a stable milestone.
8. Document immediately.
9. Commit only proven work.
10. Extract general principles that improve future engineering.

Planning and implementation are different disciplines.

Architecture should be deliberate.

Implementation should be disciplined.

Validation should be continuous.

Documentation should preserve both decisions and their rationale.

Every completed session should improve not only the software, but also the process used to build it.

That is the essence of The Delta Way.
