# Initiative: Subsystem-Oriented Repository Architecture

**Status:** Planned
**Owner:** Delta
**Priority:** Critical
**Initiative Type:** Architecture and repository refactoring
**Target System:** Aurora
**Created:** 2026-07-24
**Execution Rule:** This initiative becomes part of Aurora’s critical path after the Decision Engine Planning MVP is functional and capable of storing and managing the plan.

---

# Objective

Restructure Aurora into a subsystem-oriented repository composed of small, cohesive, independently understandable files organized within clearly defined Python packages, JavaScript modules, template components, and supporting directories.

The architecture must make the repository easier for both humans and AI systems to inspect, understand, modify, validate, and document without loading large amounts of unrelated code into context.

The desired end state is:

> Just the information needed, when it is needed.

This initiative replaces dependence on a large procedural patch protocol with structural safeguards built directly into the repository.

---

# Problem Statement

Aurora’s current patch workflow was created primarily to:

* reduce human copy-and-paste errors;
* preserve informational boundaries;
* isolate relevant code from unrelated context;
* make AI-generated changes easier to review;
* and prevent accidental replacement of the wrong code.

The protocol works when followed precisely.

However, it becomes less reliable as sessions grow longer. AI systems may gradually stop applying all protocol rules consistently, particularly when the rules themselves consume substantial context.

The repository also contains files that are too large to move safely and efficiently between Delta and an AI assistant.

Current examples include:

```text
aurora/api/planning_api.py                         1048 lines
aurora/static/aurora/js/planning.js               1752 lines
aurora/templates/aurora/snippets/
    planning_console_panel.html                    796 lines
```

These files contain multiple responsibilities and informational regions that are difficult to isolate without an external patch-boundary system.

Directory organization also lacks a sufficiently explicit subsystem model. Files are often placed according to framework type or immediate session convenience rather than according to the subsystem that owns them.

This creates several related problems:

1. Large files require unnecessary context to understand or modify small behaviors.
2. Informational boundaries are not always visible from the filesystem.
3. Future sessions cannot reliably infer why a file was placed in a particular directory.
4. The patch protocol compensates for structural weaknesses instead of eliminating them.
5. Humans must scroll through large files to locate small sections.
6. AI systems must inspect hundreds or thousands of unrelated lines to modify a small feature.
7. Repository organization depends too heavily on memory from previous sessions.
8. Reusable code and subsystem-specific code are not always clearly distinguished.
9. Architectural drift becomes more likely as new features are added.
10. ComponentRegistry cannot provide maximum value while components remain excessively broad.

---

# Core Analysis

## The Patch Protocol Is a Compensating Control

The patch protocol was created because source files did not consistently provide safe, self-contained replacement boundaries.

Anchored regions attempted to simulate modularity inside large files.

A correctly designed anchored patch usually represents one cohesive architectural responsibility. If that responsibility were already stored in its own file, the file itself would become the replacement boundary.

Therefore:

> A well-designed source file should function as its own patch.

The long-term solution is not to make the patch protocol increasingly elaborate.

The solution is to make the repository architecture sufficiently modular that the protocol is no longer required for ordinary work.

A lightweight safety procedure may remain useful for exceptional changes, but it should not carry the primary responsibility for defining architectural boundaries.

---

## Large Files Produce Context Waste

A large file is comparable to carrying an entire suitcase when only one item is needed.

When fifty relevant lines are embedded inside a two-thousand-line file:

* the human must locate and extract them;
* the AI must read or receive unrelated code;
* boundaries must be reconstructed manually;
* dependencies are harder to identify;
* review becomes slower;
* and mistakes become more likely.

Small cohesive files allow both humans and AI systems to retrieve only the component relevant to the current task.

This reduces:

* prompt size;
* session context growth;
* copy-and-paste risk;
* review burden;
* accidental coupling;
* and the amount of repository knowledge required for each change.

---

## Directory Structure Must Express Ownership

Generic framework directories such as:

```text
api/
static/
templates/
utils/
```

describe implementation type but do not necessarily identify architectural ownership.

Subsystem-specific code should live within a directory that identifies the subsystem responsible for it.

Generic directories should contain only genuinely reusable components that may be called by multiple subsystems without depending on any one subsystem’s internal behavior.

A file should answer two questions through its location:

1. Which subsystem owns this?
2. What responsibility does this file perform within that subsystem?

If those questions cannot be answered from the path and filename, the organization is insufficiently explicit.

---

# Architectural Principle

Aurora will adopt the following repository principle:

> Every subsystem owns its implementation, presentation, behavior, and internal supporting components within a clearly named package or directory.

Framework-level categories remain useful inside a subsystem, but the subsystem is the primary ownership boundary.

For example, planning-related components should be organized around the planning subsystem rather than scattered across unrelated global directories solely because one file is Python, another is JavaScript, and another is HTML.

Conceptually:

```text
planning/
    api/
    services/
    selectors/
    models/
    templates/
    static/
        js/
        css/
    tests/
    __init__.py
```

The final structure must respect Django’s discovery and static/template loading requirements, but framework conventions must not prevent subsystem ownership from being visible.

---

# File Responsibility Standard

Every production source file should have one primary responsibility.

A file is probably doing too much when:

* its purpose cannot be described in one clear sentence;
* unrelated functions must be loaded to understand one behavior;
* it contains multiple independent workflows;
* it serves multiple architectural layers;
* its imports span several unrelated concerns;
* it changes frequently for unrelated reasons;
* or a small modification requires reviewing most of the file.

As a default architectural signal:

> A source file approaching or exceeding 200 lines requires review for decomposition.

Two hundred lines is not an automatic failure condition.

Some cohesive files may reasonably exceed that size. Generated files, migrations, schemas, static data, tests, and declarative configuration may require different thresholds.

However, files over 200 lines must not be accepted without considering whether they contain multiple extractable responsibilities.

The standard is cohesion, not line-count compliance.

---

# Package Standard

Related files should be grouped into a package or subsystem directory managed through an `__init__.py` where Python packaging applies.

The package should expose a deliberate public interface rather than requiring callers to know every internal module.

Example:

```text
aurora/planning/
    __init__.py
    api/
        __init__.py
        initiatives.py
        phases.py
        steps.py
    services/
        __init__.py
        initiative_service.py
        phase_service.py
        step_service.py
    selectors/
        __init__.py
        initiative_queries.py
        phase_queries.py
        step_queries.py
```

The package interface should make supported imports clear while allowing internal files to be reorganized without forcing repository-wide import changes.

`__init__.py` must not become a dumping ground for implementation logic.

Its responsibilities should generally be limited to:

* defining the package;
* documenting the package purpose;
* exposing deliberate public imports;
* and supporting stable package-level interfaces.

---

# Reusability Rule

Code belongs in a shared or generic directory only when it is truly reusable across subsystems.

A utility should:

* perform a narrow, context-independent operation;
* avoid depending on one subsystem’s models or internal state;
* have a stable contract;
* and be reasonably useful to more than one subsystem.

Code must not be moved into `utils` merely because its correct owner is unclear.

> Unclear ownership is an architectural problem, not evidence of reusability.

Subsystem-specific helpers remain inside their subsystem.

Premature extraction into shared directories must be avoided because shared utilities create hidden coupling and make later changes harder.

---

# ComponentRegistry Role

ComponentRegistry will provide the repository map for the resulting collection of small files.

Its role becomes increasingly important as the number of files grows.

ComponentRegistry should allow Delta, Wu, and future minions to determine:

* what components exist;
* where each component is located;
* which subsystem owns it;
* what responsibility it performs;
* which components depend on it;
* which components it depends on;
* what public interface it exposes;
* when it was last observed;
* whether its description is current;
* and whether related documentation requires regeneration.

The repository may contain more files after this initiative, but it should become easier to understand because those files will be mapped, described, and connected.

A large collection of well-defined components is preferable to a small collection of opaque, multi-purpose files.

---

# Desired Outcome

At completion, Aurora should exhibit the following characteristics:

* subsystem ownership is visible from directory paths;
* files are small enough to inspect and exchange efficiently;
* each file has one primary responsibility;
* package interfaces define supported entry points;
* shared utilities are genuinely reusable;
* large files are exceptional and explicitly justified;
* ComponentRegistry maps the resulting architecture;
* AI workers can retrieve only the components required for a task;
* humans can locate relevant code without prolonged scrolling;
* architectural decisions survive across sessions through repository structure;
* ordinary changes no longer require a large patch protocol;
* and repository organization itself reduces the likelihood of unsafe edits.

Aurora should begin to function as an engineering operating system whose structure supports reliable collaboration between Delta, Wu, and specialized AI workers.

---

# Scope

## Included

This initiative includes:

* defining a formal subsystem ownership model;
* defining directory-placement rules;
* defining file-responsibility and decomposition rules;
* identifying oversized and multi-responsibility files;
* establishing package public-interface conventions;
* reorganizing planning subsystem files as the first implementation;
* decomposing large Python modules;
* decomposing large JavaScript modules;
* decomposing large template files;
* preserving existing runtime behavior during reorganization;
* updating imports, URLs, template includes, static references, and event wiring;
* updating ComponentRegistry discovery and descriptions as needed;
* documenting subsystem boundaries;
* reducing the patch protocol to a lightweight safety kernel;
* and validating a repeatable process for reorganizing later subsystems.

---

## Excluded

This initiative does not include:

* adding unrelated user-facing features;
* redesigning Aurora Console unless required by decomposition;
* rewriting working behavior solely to change style;
* creating speculative abstractions;
* moving code into shared utilities without demonstrated reuse;
* replacing Django conventions with a custom framework;
* automatically refactoring the entire repository in one operation;
* or allowing deterministic workers to create directories without an approved architectural plan.

Directory creation remains an architectural decision.

Automated workers may create files only inside directories that have already been deliberately established or explicitly approved.

---

# Critical Constraints

## Behavior Preservation

Repository reorganization must preserve existing validated behavior unless a behavior change is explicitly included in an approved step.

Refactoring and feature development should not be mixed unnecessarily.

Each subsystem migration must establish a behavior baseline before structural changes begin.

---

## Small Validated Steps

The initiative must proceed one subsystem and one responsibility boundary at a time.

Every extraction should be:

* understandable;
* reversible;
* testable;
* reviewable;
* and committed after validation.

Large repository-wide moves are prohibited unless they can be mechanically validated and safely reversed.

---

## No Directory Guessing

New directories must not be created ad hoc during implementation.

Every new subsystem directory must have:

* a defined owner;
* a stated purpose;
* an expected content policy;
* a public interface decision;
* and an approved location in the repository hierarchy.

---

## No Utility Dumping Ground

Generic directories may not be used as temporary holding areas for files whose ownership has not been decided.

Every file must have a clear architectural home.

---

## Stable Entry Points

Where practical, external callers should import through stable package interfaces.

Internal file decomposition should not force widespread callers to depend on internal module paths.

---

## ComponentRegistry Synchronization

Repository moves and extractions must be reflected in ComponentRegistry.

Stale component records must not become the cost of improved filesystem organization.

The deterministic synchronizer should identify:

* new files;
* moved files;
* removed files;
* changed hashes;
* and descriptions requiring AI regeneration.

---

# Initial Target: Planning Subsystem

The planning subsystem will serve as the first implementation and validation case because it currently contains several oversized files and represents active critical-path work.

Initial source files include:

```text
aurora/api/planning_api.py
aurora/static/aurora/js/planning.js
aurora/templates/aurora/snippets/planning_console_panel.html
```

These files collectively contain API behavior, client-side state management, event handling, rendering, CRUD operations, modal behavior, form handling, and presentation concerns.

The planning subsystem should be decomposed only after its current CRUD workflow is complete and behavior has been validated.

This prevents an incomplete feature implementation from becoming entangled with a structural migration.

---

# Proposed Planning Subsystem Responsibilities

The exact structure must be determined through inspection, but likely responsibility boundaries include the following.

## Python

Potential API modules:

```text
planning/
    api/
        initiatives.py
        phases.py
        steps.py
        serialization.py
        validation.py
        responses.py
```

Potential service modules:

```text
planning/
    services/
        initiative_service.py
        phase_service.py
        step_service.py
        ordering_service.py
        status_service.py
```

Potential query modules:

```text
planning/
    selectors/
        initiative_queries.py
        phase_queries.py
        step_queries.py
```

These names are provisional and must not be created until current responsibilities and dependencies have been inspected.

---

## JavaScript

Potential client modules:

```text
planning/
    state.js
    api.js
    initiatives.js
    phases.js
    steps.js
    forms.js
    modals.js
    rendering.js
    events.js
    bootstrap.js
```

The final organization should distinguish:

* state;
* network communication;
* DOM rendering;
* event binding;
* form lifecycle;
* entity-specific behavior;
* and initialization.

Global mutable state should be minimized and deliberately exposed where unavoidable.

---

## Templates

Potential template components:

```text
planning/
    planning_console_panel.html
    initiative_list.html
    initiative_detail.html
    phase_list.html
    phase_item.html
    step_list.html
    step_item.html
    initiative_form.html
    phase_form.html
    step_form.html
    empty_states.html
```

Template extraction should follow meaningful presentation boundaries rather than fragmenting markup solely to reduce line count.

A template include should represent a recognizable UI component or presentation responsibility.

---

# Proposed Initiative Phases

## Phase 1: Architecture Standard

Define and document the repository rules that govern:

* subsystem ownership;
* directory creation;
* file placement;
* package interfaces;
* reusable components;
* file-size review;
* dependency direction;
* and ComponentRegistry synchronization.

### Completion Criteria

* A concise repository architecture standard exists.
* Directory-placement decisions no longer depend solely on session memory.
* The standard distinguishes subsystem code from shared code.
* The standard defines when a large file must be reviewed.
* The standard defines the role of `__init__.py`.
* The standard defines how ComponentRegistry participates.

---

## Phase 2: Planning Subsystem Inventory

Inspect the current planning implementation and create a responsibility map.

The inventory must identify:

* all current functions and classes;
* client-side state;
* API endpoints;
* templates and UI regions;
* imports and dependencies;
* event flows;
* reusable code;
* subsystem-specific code;
* and candidate extraction boundaries.

### Completion Criteria

* Every major responsibility in the three large planning files is cataloged.
* Candidate files have clear purposes.
* Dependency direction is understood.
* The proposed package structure is approved before directories are created.
* Existing behavior to preserve is documented.

---

## Phase 3: Planning Python Decomposition

Decompose `planning_api.py` into cohesive modules while preserving public API behavior.

### Completion Criteria

* No planning API module contains unrelated CRUD domains.
* Initiative, Phase, and Step responsibilities are clearly separated.
* Shared planning validation and response behavior is centralized only where genuinely shared.
* Existing URLs continue to function.
* Django system checks pass.
* CRUD behavior remains validated.
* ComponentRegistry reflects the new files.

---

## Phase 4: Planning JavaScript Decomposition

Decompose `planning.js` into focused modules with deliberate state and event ownership.

### Completion Criteria

* Initialization is isolated.
* API communication is isolated.
* DOM rendering is separated from network behavior.
* Entity-specific behavior is separated where practical.
* Event listeners are not duplicated.
* Panel state restoration continues to work.
* CRUD behavior remains validated.
* The browser loads modules in a deterministic order.
* ComponentRegistry reflects the new files.

---

## Phase 5: Planning Template Decomposition

Decompose `planning_console_panel.html` into cohesive template components.

### Completion Criteria

* The primary panel template communicates overall layout clearly.
* Repeated entity markup is isolated appropriately.
* Forms and dialogs have clear component boundaries.
* Template includes do not obscure data flow.
* Existing rendering behavior remains validated.
* ComponentRegistry reflects the new files.

---

## Phase 6: Patch Protocol Reduction

Review the current patch protocol after the planning subsystem migration.

Retain only rules that still provide value after structural boundaries have been established.

The reduced protocol should focus on:

* verifying the source path;
* inspecting the current file before replacement;
* changing one cohesive file or small file set at a time;
* validating behavior;
* avoiding destructive commands;
* and committing known-good states.

### Completion Criteria

* Ordinary file replacements do not require artificial internal anchors.
* The protocol is short enough to remain reliable during long sessions.
* The filesystem carries most informational-boundary responsibility.
* Exceptional large or risky changes may still use explicit patch boundaries.
* Human copy-and-paste risk is no greater than under the previous protocol.

---

## Phase 7: Repository-Wide Migration Strategy

Use lessons from the planning subsystem to define a prioritized sequence for other Aurora subsystems.

Prioritization should consider:

* file size;
* change frequency;
* architectural importance;
* current development activity;
* coupling;
* and context cost.

### Completion Criteria

* Oversized and multi-responsibility files are ranked.
* Subsystems are identified and named.
* Each future migration can be entered as its own initiative or phase.
* No repository-wide refactor is attempted without incremental planning.

---

# SMART Goals

## Goal 1: Establish the Standard

Create and approve a concise subsystem-oriented repository standard before the first planning directory reorganization begins.

**Specific:** Define ownership, placement, package, utility, and decomposition rules.
**Measurable:** One authoritative standard is committed to the repository.
**Achievable:** The standard will consolidate decisions already emerging during Aurora development.
**Relevant:** It prevents ad hoc organization and session-dependent architecture.
**Time-bound:** Complete during Phase 1 of this initiative.

---

## Goal 2: Map the Planning Subsystem

Catalog all major responsibilities in the current planning Python, JavaScript, and template files before extracting code.

**Specific:** Produce a responsibility and dependency map.
**Measurable:** Every major function, UI region, event flow, and endpoint has an identified owner.
**Achievable:** The current planning implementation is already known and actively developed.
**Relevant:** Safe decomposition requires understanding before movement.
**Time-bound:** Complete before any new planning subsystem directories are created.

---

## Goal 3: Eliminate the Three Initial Oversized Files

Replace the three current oversized planning files with cohesive components while preserving behavior.

**Specific:** Decompose the API, JavaScript, and template implementation.
**Measurable:** The original large files are removed or reduced to clear orchestration entry points.
**Achievable:** Responsibilities can be extracted incrementally.
**Relevant:** These files are the immediate proof of the architectural problem.
**Time-bound:** Complete before beginning migration of a second subsystem.

---

## Goal 4: Preserve Functional Behavior

Maintain the validated planning CRUD workflow throughout the migration.

**Specific:** Preserve create, read, update, delete, ordering, status, panel switching, and state behavior.
**Measurable:** Every validated operation works after each phase.
**Achievable:** Structural changes will be separated from feature changes.
**Relevant:** Architectural improvement must not destabilize the Decision Engine.
**Time-bound:** Validate after every extraction and before each commit.

---

## Goal 5: Reduce Context Requirements

Ensure future planning changes can normally be completed by inspecting a small set of responsibility-specific files rather than the complete subsystem implementation.

**Specific:** Organize components around narrow responsibilities.
**Measurable:** A typical isolated planning change should require fewer than 200 lines of primary implementation context, excluding directly related tests or interfaces.
**Achievable:** Large files will be decomposed into focused modules.
**Relevant:** Reduced context is a primary reason for the initiative.
**Time-bound:** Evaluate after the planning migration is complete.

---

## Goal 6: Replace the Large Patch Protocol

Produce a substantially smaller safety procedure after repository boundaries have been validated.

**Specific:** Remove rules made unnecessary by file-level architectural boundaries.
**Measurable:** The replacement safety kernel is concise enough to load routinely without meaningful context burden.
**Achievable:** Many existing rules are compensating for large-file structure.
**Relevant:** Long-session protocol degradation is a core problem.
**Time-bound:** Complete during Phase 6.

---

# Success Metrics

This initiative will be considered successful when:

* the planning subsystem is visibly owned by a coherent package or directory structure;
* the three initial oversized files no longer contain multiple unrelated responsibilities;
* ordinary modifications can use complete-file replacement without internal patch anchors;
* the replacement safety protocol is significantly shorter;
* no planning CRUD behavior is lost;
* no duplicate event binding or client initialization is introduced;
* Django checks and relevant validation commands succeed;
* ComponentRegistry discovers and maps the new components;
* component descriptions clearly explain each file’s responsibility;
* future sessions can infer architectural placement from repository structure;
* and Delta can locate and transfer relevant code without prolonged scrolling.

---

# Non-Goals

This initiative does not attempt to achieve a repository in which every file is under exactly 200 lines.

It does not optimize for the smallest possible files.

It does not require a separate file for every function.

It does not assume that more files automatically produce better architecture.

The objective is cohesive informational boundaries.

A fragmented collection of tightly coupled files would merely replace one form of complexity with another.

The correct unit is:

> The smallest file that completely expresses one meaningful responsibility.

---

# Risks

## Excessive Fragmentation

Breaking files apart without defining stable responsibilities could create navigation overhead and hidden coupling.

**Mitigation:** Require every proposed file to have a one-sentence responsibility and a clear owner.

---

## Circular Dependencies

Poor extraction order could create circular imports or JavaScript module cycles.

**Mitigation:** Map dependency direction before creating files and preserve layered boundaries.

---

## Premature Shared Utilities

Common-looking code may be moved into shared directories before true reuse is established.

**Mitigation:** Keep code within its owning subsystem until at least two legitimate consumers require a shared abstraction.

---

## Behavioral Regression

Reorganization may accidentally alter event handling, data serialization, template context, or API behavior.

**Mitigation:** Separate refactoring from feature changes and validate after every extraction.

---

## Too Many Simultaneous Moves

Moving Python, JavaScript, and templates at once could make failures difficult to isolate.

**Mitigation:** Complete and validate one architectural layer at a time.

---

## Registry Drift

ComponentRegistry descriptions or dependency records may become stale after moves.

**Mitigation:** Include registry synchronization and AI description regeneration in every migration phase.

---

## Framework Resistance

Django template and static discovery conventions may complicate subsystem-local organization.

**Mitigation:** Preserve framework-compatible paths while making ownership explicit through naming, namespaces, and package structure.

---

# Architectural Decisions to Preserve

1. Repository structure is part of Aurora’s persistent memory.
2. Directory creation is an architectural act.
3. Deterministic workers may create files but must not independently create directories.
4. ComponentRegistry is the map for the componentized repository.
5. Subsystem ownership takes precedence over generic file-type grouping.
6. Shared directories contain only genuinely reusable components.
7. File size is a review signal, not an arbitrary compliance target.
8. Refactoring proceeds in small validated steps.
9. Existing behavior is preserved unless a behavior change is explicitly approved.
10. A cohesive file should normally be safe to replace as a complete unit.
11. Package interfaces should shield callers from internal reorganization.
12. Repository architecture should reduce dependence on session memory.
13. The planning subsystem is the first proof case, not a special exception.
14. The final structure must serve both human maintainability and AI context efficiency.

---

# Dependency on the Decision Engine

This initiative should initially exist as a repository Markdown document.

Once the Decision Engine planning interface is functional, this document should be converted into structured records containing:

```text
Initiative
    Phase
        Step
```

The imported plan should preserve:

* the objective;
* problem statement;
* architectural decisions;
* phases;
* measurable completion criteria;
* risks;
* assumptions;
* constraints;
* and validation requirements.

The Markdown file remains the authoritative source until the structured import is reviewed and accepted.

After import, authority may transfer to the Decision Engine according to a separately defined documentation and synchronization policy.

---

# Immediate Next Step

Complete and validate the current Decision Engine Planning MVP CRUD implementation.

Do not begin structural decomposition of the planning subsystem while its active feature behavior remains incomplete.

Once CRUD behavior is validated:

1. freeze unrelated planning feature development;
2. inventory the existing planning files;
3. define the approved planning package structure;
4. enter this initiative into the Decision Engine;
5. and begin Phase 1 in small validated steps.

---

# Completion Definition

This initiative is complete when Aurora’s planning subsystem demonstrates that repository structure can replace most procedural patch boundaries.

The resulting architecture must allow Delta, Wu, and future minions to retrieve, understand, modify, and validate narrowly scoped components without loading entire multi-thousand-line implementations.

The initiative succeeds when the repository itself communicates:

* where a component belongs;
* what it owns;
* what it may depend on;
* how it is accessed;
* and what must be inspected to change it safely.

At that point, Aurora will no longer rely primarily on a protocol to simulate modular engineering.

It will embody modular engineering in its structure.
