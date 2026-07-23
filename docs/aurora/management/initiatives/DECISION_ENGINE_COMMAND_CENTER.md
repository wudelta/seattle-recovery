# Decision Engine and Command Center Initiative

**Status:** Planned
**Priority:** Critical
**Owner:** Delta
**Target for Planning MVP:** July 28, 2026
**Project:** Aurora
**Initiative Type:** Platform Architecture and Workflow
**Authoritative Engineering Philosophy:** The Delta Way

---

# Initiative Summary

Aurora will introduce a persistent, database-backed system for defining, organizing, discussing, estimating, and tracking engineering work.

The system will be built around three hierarchical planning objects:

```text
Initiative
    Phase
        Step
```

The underlying reasoning and orchestration subsystem will be called the **Decision Engine**.

The integrated Aurora Console workspace through which Delta and other users interact with Wu, project plans, implementation tools, reviews, and metrics will be called the **Command Center**.

This initiative is larger than a conventional project planner.

Its long-term purpose is to transform Aurora from a collection of development tools into an adaptive engineering workspace that can determine:

* what work exists;
* why the work exists;
* what should be done next;
* what dependencies must be satisfied;
* who or what should perform the work;
* whether the work is ready for execution;
* whether the result meets Aurora’s engineering standards;
* and how accurately the work was planned.

The Command Center will provide one persistent conversational workspace. Panels and tools will change according to the current task without forcing the user to navigate between disconnected pages.

Wu will serve as the conversational interface and engineering coordinator.

The Decision Engine will provide the structured project state and decision logic behind Wu.

---

# Problem Statement

Aurora currently distributes planning and execution across several partially overlapping systems.

## Delta Notes

Delta Notes captures ideas and possible future work.

Its current implementation dedicates an entire panel to CRUD operations for what is effectively a collection of sticky notes.

Notes are not reliably connected to project planning or implementation.

## Blueprint

Blueprint was originally intended to evolve into Wu Chat.

Through use, it instead became a direct interface for running slash commands that create views, APIs, and related repository artifacts.

This allows implementation activity to occur independently of an approved project plan.

## Wu Chat

Wu Chat provides the primary conversational interface and supports patch review, but it does not yet maintain a durable hierarchy of initiatives, phases, and implementation steps.

## Project State Documentation

Large project state documents provide valuable strategic continuity but are not appropriate for minute-by-minute planning or execution tracking.

## Resulting Problems

Aurora lacks one authoritative operational answer to these questions:

* What are we building?
* Why are we building it?
* What phase are we in?
* What is the next validated step?
* What work is blocked?
* What work can be completed with the available time?
* What work has been discussed but not approved?
* What work is being implemented outside the plan?
* How accurate were the estimates?
* How well was the work performed?

Without a unified operational planning system, work can be captured, discussed, or executed in several places without becoming part of one coherent project history.

---

# Vision

Aurora should feel like one integrated engineering workspace rather than a collection of web pages.

The user should remain in one persistent interface while Aurora changes the available work surface to meet the demands of the current moment.

The intended interaction is:

```text
Human intent
    ↓
Conversation with Wu
    ↓
Decision Engine
    ↓
Initiative
    ↓
Phase
    ↓
Step
    ↓
Approval
    ↓
Minion or deterministic worker
    ↓
Review
    ↓
Validation
    ↓
Completion
    ↓
Metrics and learning
```

The user should make engineering decisions rather than operate a sequence of forms and buttons.

Aurora should manage the procedural mechanics while keeping every important decision visible, explainable, and reviewable.

The experience should feel coordinated and responsive—almost magical—but never mysterious.

---

# Core Principle

> Every meaningful piece of work must belong to an Initiative, a Phase, and a Step, or be intentionally classified as Miscellaneous work.

Work should not be implemented merely because someone typed a slash command or asked Wu to change something.

Before implementation, Aurora should be able to identify:

* the Initiative that justifies the work;
* the Phase that provides its context;
* the Step that defines its boundaries;
* the expected result;
* the validation method;
* and the current authorization state.

The long-term execution rule will be:

> If work is not represented by an approved Step, Aurora does not execute it.

---

# Terminology

## Decision Engine

The Decision Engine is the architectural subsystem that stores and reasons about project work.

It is responsible for:

* maintaining Initiatives, Phases, and Steps;
* determining current and next work;
* tracking status and dependencies;
* managing estimates and actual effort;
* preserving planning rationale;
* supporting prioritization;
* identifying blocked and available work;
* and eventually recommending execution assignments.

The Decision Engine is not itself the primary user interface.

## Command Center

The Command Center is the integrated Aurora Console workspace used to interact with Wu and the Decision Engine.

It will assimilate the useful capabilities of Wu Chat and eventually replace or absorb the responsibilities of Delta Notes and Blueprint.

The Command Center should provide:

* persistent conversation with Wu;
* project and initiative context;
* initiative outline views;
* step details;
* planning controls;
* execution status;
* telemetry;
* Monaco patch review;
* validation evidence;
* metrics;
* and architectural context.

## Wu

Wu is the human-facing engineering coordinator.

Wu will:

* discuss ideas and requirements;
* identify missing information;
* apply The Delta Way;
* propose Initiatives, Phases, and Steps;
* explain planning decisions;
* create and update planning records;
* recommend the next work;
* and eventually assign approved Steps to minions or deterministic workers.

## Initiative

An Initiative represents a meaningful outcome or body of work.

Examples:

* Implement the Decision Engine
* Refactor HopeHub Journaling
* Add Component Description Generation
* Prepare HopeHub Cloud Beta

An Initiative may exist in a planned state before all Phases and Steps are known.

## Phase

A Phase represents a coherent stage of an Initiative.

A Phase should group Steps that share a meaningful objective, dependency boundary, or validation milestone.

## Step

A Step is the smallest planned implementation or operational unit that can be individually assigned, executed, validated, and completed.

A Step is the future unit of execution authority.

---

# Status Model

The initial shared lifecycle should include:

```text
planned
active
paused
completed
cancelled
```

Additional Step-specific execution states may be introduced later, such as:

```text
ready
blocked
in_progress
awaiting_review
awaiting_validation
failed
```

Status rules must remain explicit and deterministic.

## Initiative Completion

An Initiative may be completed only when all required Phases are completed or intentionally cancelled.

## Phase Completion

A Phase may be completed only when all required Steps are completed or intentionally cancelled.

## Step Completion

A Step may be completed only after its defined validation requirement has been satisfied.

No object should silently become completed merely because subordinate records happen to exist.

---

# Ownership and Attribution

Each Initiative must identify the user who introduced or owns it.

The initial Initiative ownership field will normally identify Delta, but the architecture must support additional users.

Phases and Steps should retain creation and modification attribution where practical.

Future assignment may distinguish between:

* project owner;
* planner;
* assigned minion;
* human implementer;
* reviewer;
* and validator.

---

# Time and Estimation

Good project management requires both forecasts and observed results.

## Initial Time Fields

Each Step should support:

* estimated effort;
* actual effort;
* estimate confidence;
* start time;
* completion time.

Estimated and actual effort should use a consistent unit suitable for aggregation, most likely decimal hours or minutes stored as a duration.

## Rollups

Phase and Initiative totals should eventually be calculated from subordinate records.

They should not require duplicated manual bookkeeping.

The Decision Engine should eventually be able to report:

* estimated effort;
* actual effort;
* remaining effort;
* variance;
* completion percentage;
* and planning accuracy.

## Estimation Honesty

Early estimates produced by Wu may not be based on sufficient historical evidence.

They must therefore be presented as planning estimates rather than facts.

Wu should express uncertainty rather than hide it.

Example:

```text
Estimated effort: 8 hours
Confidence: 40%

Reason:
The integration boundary has not yet been inspected.
```

As Aurora accumulates estimated and actual effort data, the Decision Engine should use that history to improve future planning.

---

# Grading and Evaluation

Aurora should eventually evaluate more than whether a Step technically completed.

A single grade may be sufficient for the earliest implementation, but the long-term model should support distinct evaluation dimensions.

Potential dimensions include:

* planning quality;
* estimate accuracy;
* implementation quality;
* validation quality;
* architectural compliance;
* maintainability;
* and documentation quality.

An example evaluation might be:

```text
Planning: C
Implementation: A
Validation: A
```

This makes it possible to distinguish excellent implementation from poor planning or inaccurate estimation.

The grading system must not become a decorative score.

Each grade should be backed by defined criteria or supporting evidence.

The exact grading rubric is outside the one-week Planning MVP.

---

# Miscellaneous Work

Aurora must support small, independent tasks that do not justify a dedicated Initiative.

Examples include:

* correct a typo;
* rename a misleading field;
* update a short document;
* remove an obsolete import;
* investigate a minor warning;
* perform a small maintenance task.

These tasks will belong to a normal Initiative named **Miscellaneous** rather than requiring special-case planning logic.

Possible Phases within the Miscellaneous Initiative include:

```text
Quick Wins
Maintenance
Documentation
Investigation
```

The Miscellaneous Initiative will provide a backlog of bounded work that can be selected when:

* insufficient time remains to begin a major Phase;
* another Initiative is blocked;
* an hour remains in the workday;
* or a small maintenance task provides immediate value.

The Decision Engine should eventually support questions such as:

> What useful unblocked tasks can be completed in under one hour?

---

# Delta Notes Integration

Delta Notes will no longer serve as a parallel project planning system.

Its long-term purpose will be reduced to rapid idea capture.

A captured note may later be:

* promoted into a new Initiative;
* added to an existing Initiative;
* converted into a Phase or Step;
* placed in the Miscellaneous Initiative;
* archived;
* or rejected.

The initial Command Center may retain a compact quick-capture interface when space allows.

Full CRUD management of Delta Notes does not justify a permanent primary panel.

Delta Notes should remain available until its capture and promotion workflow has been safely replaced.

---

# Blueprint Integration

Blueprint’s direct slash-command functionality should eventually be absorbed into the planned execution pipeline.

Slash commands will remain useful as deterministic implementation mechanisms.

Their primary caller, however, should become Wu or an assigned minion rather than a human manually initiating unrelated implementation.

The intended progression is:

```text
Approved Step
    ↓
Wu selects an execution strategy
    ↓
Wu or a minion invokes a slash command
    ↓
Generated work enters review and validation
    ↓
Step completion is recorded
```

Blueprint should not be retired until equivalent functionality is available through the Command Center.

---

# Anamod Integration

Anamod will remain part of Aurora.

Its role is expected to shift gradually from primary code mutation toward code inspection, investigation, debugging, and occasional manual intervention.

The long-term workflow should not require Delta to edit most routine implementation work directly.

Anamod should remain available for:

* inspecting source code;
* understanding implementation details;
* tracing behavior;
* reviewing architecture;
* investigating unexpected results;
* performing exceptional manual corrections;
* and validating AI-generated changes.

Aurora should never prevent the human architect from seeing or directly inspecting the code.

---

# Command Center Experience

The Command Center should feel like one persistent workspace.

It should not become a collection of loosely connected pages.

## Stable Workspace Elements

Likely persistent elements include:

* Wu conversation;
* current project context;
* current Initiative, Phase, and Step context;
* workspace controls;
* and a dynamic work surface.

## Dynamic Work Surfaces

The active work surface may display:

* initiative outline;
* phase details;
* step details;
* requirements discussion;
* estimates;
* dependencies;
* execution telemetry;
* minion activity;
* Monaco diff review;
* validation results;
* metrics;
* documentation;
* component relationships;
* or historical changes.

## State Preservation

Each surface should retain its state when the user switches away and later returns.

State worth preserving includes:

* selected Initiative, Phase, and Step;
* expanded and collapsed outline nodes;
* form state;
* scroll positions;
* active tabs;
* filters;
* selected files;
* Monaco cursor and review state;
* and conversation context.

Panel switching should preserve continuity rather than forcing the user to reconstruct their work.

## Interface Principle

> One persistent conversational home, with context-sensitive work surfaces.

---

# The Delta Way Integration

The Decision Engine must not merely generate generic project plans.

Every proposed plan must be evaluated through The Delta Way.

Wu should consider at least the following questions:

* Does the plan preserve architectural boundaries?
* Is the work divided into independently verifiable increments?
* Is each Step small enough to understand and validate?
* Can the change be rolled back safely?
* Does the proposal introduce unnecessary coupling?
* Does it create avoidable technical debt?
* Does it preserve long-term maintainability?
* Does it minimize opportunities for human and AI error?
* Is the design cheap and right rather than merely fast?
* Is the plan grounded in the actual repository and operating environment?
* Are assumptions and uncertainties visible?
* Does each implementation Step have a defined validation method?

Wu should push back when a proposed approach conflicts with these principles.

The Decision Engine should not optimize for producing the greatest amount of code.

It should optimize for delivering the smallest safe and valuable validated increment.

---

# SMART Goals

## SMART Goal 1: Establish the Planning Data Model

By **July 28, 2026**, Aurora will have database-backed Initiative, Phase, and Step models with defined parent relationships, ownership, ordering, status, descriptions, and timestamps.

Success will be demonstrated by creating at least:

* one Initiative;
* two Phases within that Initiative;
* and three Steps within each Phase.

The records must survive application restarts and be inspectable through Django administration or another available internal interface.

## SMART Goal 2: Display a Persistent Hierarchical Plan

By **July 28, 2026**, the Aurora Console will display Initiatives, Phases, and Steps in an expandable outline within a stateful panel.

Success will be demonstrated when a user can:

* open the planning surface;
* expand and collapse the hierarchy;
* select an Initiative, Phase, or Step;
* switch to another Aurora panel;
* return to the planning surface;
* and recover the same meaningful selection and outline state.

## SMART Goal 3: Support Complete Planning CRUD

By **July 28, 2026**, Initiative, Phase, and Step records will support creation, reading, updating, ordering, status changes, and deletion or safe cancellation through an internal application interface.

Success will be demonstrated by creating and revising a complete Initiative without directly editing the database.

Direct manual CRUD controls may be utilitarian during the first implementation. Conversational CRUD through Wu is a separate goal.

## SMART Goal 4: Enable Wu to Create a Structured Plan

By **July 28, 2026**, Wu will be able to receive a human-written project description, discuss missing requirements, and create a proposed Initiative containing ordered Phases and Steps.

Success will be demonstrated using a project description that was not originally written for Aurora.

Wu must:

* ask relevant clarifying questions;
* identify assumptions;
* create a coherent Initiative;
* divide it into ordered Phases;
* create concrete Steps;
* and provide preliminary effort estimates with visible uncertainty.

The generated plan does not need to execute code during this milestone.

## SMART Goal 5: Enable Conversational Plan Revision

By **July 28, 2026**, the user will be able to request at least three common planning changes through the normal Wu conversation interface.

Supported changes must include examples such as:

* rename an Initiative, Phase, or Step;
* move or reorder a Step;
* add a Phase;
* split a Step;
* change status;
* or revise an estimate.

Success will be demonstrated when Wu updates the persisted records and the planning outline reflects the changes without requiring direct database administration.

## SMART Goal 6: Demonstrate Third-Party Planning Value

By **July 29, 2026**, Aurora will be ready to conduct a planning demonstration using a project description supplied by Delta’s colleague.

The demonstration will:

1. place the description in an accessible project folder;
2. allow Wu to read it;
3. conduct a short requirements discussion;
4. identify missing information and assumptions;
5. create a structured implementation plan;
6. attach preliminary estimates;
7. and display the result in the Initiative, Phase, and Step hierarchy.

The demonstration is successful if the resulting plan is sufficiently concrete for Delta and the colleague to review scope, sequencing, dependencies, major risks, and rough effort.

The estimates may be provisional but must not be presented as established facts.

## SMART Goal 7: Preserve Planning and Execution Separation

Throughout the one-week Planning MVP, Wu and the Decision Engine will not automatically modify repository code as a consequence of creating or editing a plan.

Success will be demonstrated when:

* planning records can be created and revised;
* no slash command is executed automatically;
* no repository patch is applied automatically;
* and no Step is treated as implementation authorization.

This boundary must remain in place until the approval and execution phase is intentionally designed.

---

# One-Week Planning MVP

The first implementation must remain deliberately bounded.

## Included

The Planning MVP includes:

* Initiative model;
* Phase model;
* Step model;
* ownership at the Initiative level;
* hierarchical relationships;
* ordering;
* basic statuses;
* descriptions;
* timestamps;
* estimated effort;
* estimate confidence or uncertainty;
* hierarchical outline display;
* internal CRUD operations;
* Wu-assisted plan creation;
* Wu-assisted plan revision;
* persistent database storage;
* basic Miscellaneous Initiative support;
* and a third-party planning demonstration.

## Excluded

The Planning MVP does not include:

* automatic repository implementation;
* step approval workflow;
* minion task assignment;
* slash-command execution by Wu;
* automatic patch generation;
* automatic patch application;
* grading rubrics;
* historical estimation models;
* advanced analytics;
* dependency graph visualization;
* Gantt charts;
* resource scheduling;
* calendar integration;
* multi-user permissions beyond basic ownership;
* complete Blueprint retirement;
* complete Delta Notes retirement;
* or complete Anamod integration.

These exclusions are intentional.

The first milestone proves that Aurora can convert conversation into a durable, editable, disciplined engineering plan.

---

# Proposed Planning MVP Phases

## Phase 1: Domain Model and Rules

Define and implement:

* Initiative;
* Phase;
* Step;
* status choices;
* ordering behavior;
* ownership;
* estimated effort;
* estimate uncertainty;
* timestamps;
* hierarchy rules;
* and completion constraints.

The models should remain minimal enough to complete within one week.

Fields without a clear immediate use should be deferred.

## Phase 2: Planning Services and API

Create the application services or APIs required to:

* list the hierarchy;
* create records;
* update records;
* reorder records;
* change statuses;
* and safely remove or cancel records.

Planning rules should not be buried entirely in UI code.

## Phase 3: Command Center Planning Surface

Create the stateful outline surface within Aurora Console.

The surface should display:

* Initiative;
* Phase;
* Step;
* status;
* estimate;
* and selection state.

The first version should prioritize clarity and continuity over visual sophistication.

## Phase 4: Wu Planning Integration

Extend Wu so that conversation can:

* create an Initiative;
* add Phases;
* add Steps;
* revise the hierarchy;
* change descriptions;
* revise estimates;
* and explain planning decisions.

Wu must use structured application operations rather than fabricating apparent updates only in conversation text.

## Phase 5: External Planning Demonstration

Use the colleague’s project description to validate:

* file ingestion;
* requirements discussion;
* plan generation;
* estimates;
* plan persistence;
* and human review.

Record any failures or missing capabilities as future Steps rather than expanding the MVP uncontrollably during the demonstration.

---

# Future Phase: Approval and Execution

After the Planning MVP is validated, Aurora will add controlled execution.

The future workflow will include:

```text
Planned Step
    ↓
Ready for approval
    ↓
Approved
    ↓
Assigned to Wu, minion, human, or deterministic worker
    ↓
In progress
    ↓
Review
    ↓
Validation
    ↓
Completed
```

Future capabilities may include:

* explicit Step approval;
* execution strategy;
* minion assignment;
* deterministic slash-command assignment;
* human assignment;
* repository patch generation;
* Monaco review;
* validation evidence;
* actual time tracking;
* completion grading;
* and automatic Phase and Initiative rollups.

No execution capability should bypass the Step authorization model.

---

# Future Phase: Decision Support

After enough planning and execution history exists, the Decision Engine should support recommendations.

Examples include:

* the next highest-value unblocked Step;
* useful work that fits the remaining time in the day;
* small Miscellaneous tasks under one hour;
* phases trending over estimate;
* work blocked by unresolved decisions;
* initiatives at risk;
* estimates with low confidence;
* and areas where historical actual effort differs consistently from Wu’s estimates.

The Decision Engine should eventually reduce or eliminate the recurring uncertainty:

> What do we need to work on next?

---

# Architectural Constraints

## Single Source of Operational Truth

Initiatives, Phases, and Steps must become the authoritative source for active project execution state.

Strategic documents may summarize project direction, but they must not become competing minute-by-minute task systems.

## Conversation Is an Interface, Not the Database

Wu’s conversational statements must correspond to persisted state.

A plan described only in chat is not an Aurora project plan.

## No Silent Mutations

Every material planning change must be visible in the project hierarchy and attributable to an initiating user or operation.

## No Premature Automation

Planning creation must not imply execution approval.

## Deterministic Boundaries

Deterministic operations should remain deterministic.

AI should decide or propose what should happen.

Application services should perform validated record mutations.

## Human Authority

Delta remains the final architectural authority.

Wu must be able to recommend, explain, and challenge, but not silently override human decisions.

## Repository Reality

Plans for existing projects must eventually be grounded in:

* actual source files;
* ComponentRegistry records;
* architecture documentation;
* dependencies;
* and current project state.

A plausible plan that ignores repository reality is not sufficient.

---

# Risks

## Scope Expansion

This initiative can easily grow into a complete project management platform.

Mitigation:

* enforce the one-week Planning MVP boundary;
* record new ideas as future Steps;
* exclude approval, execution, grading, and analytics from the initial milestone.

## Overbuilt Data Model

Adding every conceivable planning field now could delay the useful workflow.

Mitigation:

* implement fields required for the Planning MVP;
* add advanced evaluation and execution data only when their workflow exists.

## Duplicate Interfaces

Building another chat interface would create unnecessary duplication.

Mitigation:

* assimilate Wu Chat into the Command Center;
* preserve working conversation and Monaco review capabilities;
* make the surrounding work surface adaptable.

## Fake Conversational CRUD

Wu may claim to have changed a plan without modifying persisted records.

Mitigation:

* require structured planning operations;
* return saved records;
* refresh the hierarchy from authoritative database state.

## Unreliable Estimates

Initial AI estimates may appear more authoritative than they are.

Mitigation:

* require confidence or uncertainty;
* display assumptions;
* compare estimates with actual effort later;
* never present early estimates as historical evidence.

## Loss of Interface State

Dynamic panel swapping may disrupt continuity.

Mitigation:

* make state preservation an explicit acceptance criterion;
* preserve selection, expansion, scroll, and relevant work-surface state.

## Premature Retirement of Existing Tools

Delta Notes or Blueprint may still contain useful capabilities.

Mitigation:

* assimilate functionality before retirement;
* remove a panel only after its workflow has a verified replacement.

---

# Acceptance Criteria for the Planning MVP

The Planning MVP is complete when all of the following are true:

* Initiative, Phase, and Step records exist in PostgreSQL.
* Their hierarchy and ordering are enforced.
* Initiative ownership is recorded.
* Basic statuses are supported.
* Steps support preliminary effort estimates.
* The hierarchy appears in an Aurora Console planning surface.
* The planning surface preserves meaningful state when switching panels.
* A user can perform complete internal CRUD operations.
* Wu can create a persisted Initiative from a human project description.
* Wu can create ordered Phases and Steps.
* Wu can identify assumptions and request missing information.
* Wu can revise persisted planning records through conversation.
* The Miscellaneous Initiative can hold small independent tasks.
* No planning action automatically executes repository changes.
* A third-party application concept can be converted into a reviewable implementation plan.
* Delta confirms that the resulting plan follows The Delta Way closely enough to guide future implementation.

---

# Definition of Success

This initiative is successful when Aurora no longer treats project planning as a document or isolated panel.

Instead, project planning becomes a persistent operational system that connects:

* human intent;
* architectural discussion;
* structured planning;
* future implementation;
* validation;
* and eventual learning from results.

At the end of the first week, Aurora does not need to build the planned project.

It must be able to understand the proposed project well enough to discuss it, structure it, estimate it honestly, preserve it, revise it, and present it as an actionable engineering plan.

That is the foundation required before Wu can safely execute approved work.

---

# Long-Term Outcome

The final system should make this interaction possible:

> **Delta:** We have about an hour left today. What should we work on?

> **Wu:** The active Phase is blocked pending validation. There are three unblocked Miscellaneous Steps estimated under one hour. The highest-value option is updating the ComponentRegistry exclusion rules. Its estimate is 45 minutes with 80% confidence.

Delta makes the decision.

Aurora handles the mechanics.

That is the intended role of the Decision Engine and Command Center within Aurora’s adaptive engineering workspace.
