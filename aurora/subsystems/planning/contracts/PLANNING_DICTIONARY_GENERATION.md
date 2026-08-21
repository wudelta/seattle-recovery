# Decision Engine Planning Dictionary Generation

Version: 1.1

---

# Purpose

This playbook teaches a human engineer or AI worker how to convert an
architectural discussion into a Decision Engine planning dictionary.

The resulting dictionary must be directly consumable by:

```text
import_planning_dictionary
```

without manual modification.

This document intentionally explains the engineering workflow rather than the
implementation of the importer.

This document is a Hansel breadcrumb. It must identify the next repository-owned
authority whenever this playbook no longer contains enough information to
continue safely.

---

# Task

Given:

* an architectural discussion;
* a target Project slug;
* and, when the Project does not yet exist, the Project definition;

produce:

* one valid planning dictionary.

The planning dictionary becomes the authoritative implementation plan for the
Decision Engine.

---

# Expected Output

The final deliverable is one Python-literal dictionary matching the canonical
template.

Example filename:

```text
hopehub_001_resource_finder.plan
```

The file must contain exactly one Python-literal dictionary.

Do not include:

* imports;
* assignments;
* function definitions;
* executable Python;
* Markdown fences;
* commentary outside the dictionary.

---

# Required Inputs

Before beginning, obtain:

* architectural discussion;
* target Project slug.

When the target Project does not exist, also obtain or derive from the
architectural discussion:

* Project title;
* Project description;
* initial Project status.

Nothing else should be requested unless required by this playbook.

Do not ask the human to remember importer fields, repository paths, or payload
shapes. Follow the authority chain defined below.

---

# Decision Engine Hierarchy

Planning follows one hierarchy.

```text
Project
    Initiative
        Phase
            Step
```

Every planning dictionary ultimately creates or extends this hierarchy.

A planning dictionary may:

* create one new Project and its nested hierarchy;
* add Initiatives to an existing Project;
* add Phases to an existing Initiative;
* add Steps to an existing Phase.

It must not update, delete, merge, or reorder existing records.

---

# Project Creation

The target is always declared through:

```python
"target": {
    "project_slug": "hopehub",
}
```

When the Project already exists:

```python
"add_projects": [],
```

When the Project does not exist, `add_projects` must contain exactly one Project:

```python
"add_projects": [
    {
        "title": "HopeHub",
        "slug": "hopehub",
        "description": (
            "Describe the product, application, or engineering domain."
        ),
        "status": "ACTIVE",
        "active": True,
    },
],
```

Rules:

* the Project slug must match `target.project_slug`;
* no more than one Project may be created by one dictionary;
* Project creation and all nested additions are applied transactionally;
* a dictionary must not attempt to recreate an existing Project.

---

# Initiative Design

An Initiative represents one durable engineering outcome.

An Initiative should answer:

> "When this work is complete, what lasting capability exists that did not
> exist before?"

An Initiative should not describe implementation details.

Normally an Initiative contains multiple independently verifiable Phases.

## Active Initiative Decision

A developer may have at most one current `ACTIVE` Initiative.

Before generating a new Initiative with:

```python
"status": "ACTIVE",
```

inspect current Planning lifecycle state for the target developer.

If no Initiative is currently `ACTIVE`, the new Initiative may be proposed as
`ACTIVE` when that matches the architectural discussion.

If another Initiative is already `ACTIVE`, do not silently pause it and do not
emit a conflicting planning dictionary.

Request one human decision:

```text
Keep the existing Initiative ACTIVE
    → generate the new Initiative as PLANNED

Activate the new Initiative
    → resolve the existing Initiative through Planning lifecycle authority
    → then generate/apply the new Initiative as ACTIVE
```

The authoritative lifecycle contract is:

```text
aurora/subsystems/planning/contracts/
LIFECYCLE_AND_RECONCILIATION.md
```

The authoritative Initiative transition service is:

```text
aurora/subsystems/planning/services/lifecycle/initiative.py
```

The importer must reject a dictionary that would create a second concurrent
`ACTIVE` Initiative for the importing developer.

---

# Phase Design

A Phase represents one architectural milestone.

Completion of a Phase should demonstrate meaningful progress independent of
later work.

Phases should normally be sequential.

Examples:

* Journal API
* Mobile Client
* Resource Synchronization

Avoid Phases that merely describe time.

Poor:

```text
Week One
```

Better:

```text
Journal Backend API
```

---

# Step Design

A Step represents one bounded engineering task.

A Step should normally require one implementation effort followed by
validation.

Every Step must contain:

* title;
* description;
* validation requirement.

Additional planning metadata should be supplied whenever it can be determined
from the discussion.

Supported Step planning metadata includes:

* status;
* estimated_minutes;
* estimate_confidence;
* risk_level;
* risk_description;
* validation_description;
* document;
* validation;
* planned_files;
* actual_files.

Do not add unsupported Step fields.

---

# Step Document

Use `document` to preserve technical intent and the architectural discussion
needed by future workers.

```python
"document": {
    "technical_design": "",
    "dependencies": "",
    "assumptions": "",
    "implementation_notes": "",
    "discussion": "",
},
```

Supported fields:

```text
technical_design
dependencies
assumptions
implementation_notes
discussion
```

Guidance:

* `technical_design` records the intended implementation approach;
* `dependencies` records required components, services, decisions, or prior work;
* `assumptions` records facts accepted for planning purposes;
* `implementation_notes` is normally empty during initial planning and may be
  populated later;
* `discussion` preserves important reasoning and decisions from the source
  architectural discussion.

Do not duplicate the entire Initiative document into every Step. Preserve only
the information needed to implement that Step safely.

---

# Step Validation

The core Step field remains:

```python
"validation_description": (
    "Describe deterministic evidence that proves this Step is complete."
),
```

The supporting validation object is:

```python
"validation": {
    "description": (
        "Describe deterministic evidence that proves this Step is complete."
    ),
    "notes": "",
},
```

During planning:

* `validation.description` should match or refine
  `validation_description`;
* `validation.notes` should normally be empty.

Observed results belong in `validation.notes` after implementation.

Validation must describe observable evidence.

Good:

```text
The command reports every candidate dataset with its title, row count,
field definitions, and verification status.
```

Poor:

```text
Looks correct.
```

---

# Planned and Actual Files

The Decision Engine records repository file impact through Step files.

## Planned Files

Use `planned_files` when the architectural discussion or repository authority
identifies files expected to be created or modified.

```python
"planned_files": [
    {
        "file_path": (
            "hopehub/management/commands/"
            "probe_king_county_datasets.py"
        ),
        "reason": (
            "Repository-owned entry point for deterministic metadata probing."
        ),
    },
],
```

Rules:

* use repository-relative paths;
* provide a reason for each path whenever known;
* do not invent paths;
* do not use array indexes or conversational descriptions as file identity;
* do not repeat the same path within one Step role.

When the file path cannot be determined safely:

```python
"planned_files": [],
```

and preserve the unresolved file decision in the Step document.

## Actual Files

`actual_files` records observed implementation evidence.

Initial planning dictionaries should normally use:

```python
"actual_files": [],
```

Do not predict actual files.

Use populated `actual_files` only when importing known historical or
execution-derived evidence.

---

# Estimates

When enough information exists, provide:

* estimated_minutes;
* estimate_confidence.

If insufficient information exists, use:

```text
estimate_confidence = MEDIUM
```

rather than inventing precision.

Estimates measure expected implementation effort for one bounded Step.

---

# Risk

Assign:

* LOW;
* MEDIUM;
* HIGH.

Risk measures engineering uncertainty rather than project importance.

Include a risk description whenever the reason is not obvious.

---

# Asking Questions

Do not ask for information already contained within the architectural
discussion or repository-owned authorities.

Ask only when a required planning decision cannot be determined safely.

Good questions:

* Which Project receives this Initiative?
* Should this Initiative begin ACTIVE or PLANNED?
* Is this a new Initiative or an addition to an existing Initiative?
* What is the title of the new Project?

Do not ask:

* how the Decision Engine works;
* how the importer works;
* what fields the dictionary supports;
* what shape `planned_files` uses;
* which command validates the dictionary;
* to inspect unrelated repository files.

The answers to importer and payload questions must come from the authority chain.

---

# Unknown Information

When required information is unavailable:

Stop.

Request only the missing fact.

Do not invent:

* Project definitions;
* Initiative titles;
* Phase titles;
* Step titles;
* repository paths;
* estimates;
* risks;
* validation;
* technical designs;
* dependencies;
* assumptions.

Unknown optional information should remain empty rather than being fabricated.

---

# Supported Fields

Use only fields supported by the current planning schema.

Do not construct planning dictionaries from memory.

Read:

```text
aurora/subsystems/planning/io/templates/
planning_update_v1.plan
```

The executable schema remains authoritative:

```text
aurora/subsystems/planning/io/schema.py
```

The interactive Step CRUD contract is the authority for the meaning and
persistence behavior of Step supporting data:

```text
aurora/subsystems/planning/api/steps.py
```

If the template, this playbook, the CRUD contract, and the executable schema
disagree:

1. the executable schema determines what the dictionary accepts;
2. the updater determines what the importer persists;
3. the CRUD implementation determines the established Step payload semantics;
4. the template and this playbook must be corrected.

---

# Canonical Template

Planning dictionaries begin from:

```text
aurora/subsystems/planning/io/templates/
planning_update_v1.plan
```

Do not construct planning dictionaries from memory.

The canonical top-level shape is:

```python
{
    "schema_version": 1,

    "target": {
        "project_slug": "project-slug",
    },

    "add_projects": [],

    "add_initiatives": [],

    "add_phases": [],

    "add_steps": [],
}
```

At least one addition list must contain work.

---

# Authority Chain

Load only the next authority required for the current task.

## Architectural Intent

Read the relevant durable Initiative or Planning Handoff.

Example:

```text
docs/hopehub/management/initiatives/CURRENT_INITIATIVE.md
```

## Generation Workflow

Read:

```text
aurora/subsystems/planning/contracts/
PLANNING_DICTIONARY_GENERATION.md
```

## Copyable Dictionary Shape

Read:

```text
aurora/subsystems/planning/io/templates/
planning_update_v1.plan
```

## Accepted Fields and Normalization

Read:

```text
aurora/subsystems/planning/io/schema.py
```

## Transactional Persistence

Read:

```text
aurora/subsystems/planning/io/updater.py
```

## Existing Step Payload Semantics

Read only when Step supporting structures require clarification:

```text
aurora/subsystems/planning/api/steps.py
```

## Command Parsing and Execution

Read:

```text
aurora/management/commands/
import_planning_dictionary.py
```

Do not make the human guess which file comes next.

---

# Planning Workflow

Given an architectural discussion:

1. Identify the target Project slug.
2. Determine whether the Project exists in the Decision Engine.
3. If it does not exist, define one `add_projects` record.
4. Identify one durable Initiative outcome.
5. Inspect the target developer's current ACTIVE Initiative state.
6. If the new Initiative should be ACTIVE and another Initiative is already
   ACTIVE, request the human lifecycle decision before generating the dictionary.
7. Divide the Initiative into independently verifiable Phases.
8. Divide each Phase into bounded Steps.
9. Preserve relevant technical design, dependencies, assumptions, and
   discussion within each Step document.
10. Add planned repository files only when the paths are supported by the
    discussion or repository evidence.
11. Define deterministic validation for every Step.
12. Assign reasonable estimates, confidence, and risk.
13. Generate one Python-literal planning dictionary.
14. Run dry-run validation.
15. Correct every validation error.
16. Apply only after successful validation.
17. Inspect the resulting hierarchy and supporting Step records.
18. Commit the Initiative source, contract changes, template changes, schema
    changes, updater changes, command changes, and validated reference import.

---

# Validation

Before applying, run:

```bash
daurora-cmd import_planning_dictionary \
    <dictionary.plan> \
    --user delta \
    --dry-run
```

Expected success format:

```text
VALIDATED: project=<slug> projects=<count> initiatives=<count> phases=<count> steps=<count>
```

Interpretation:

* `projects=1` means the dictionary will create the target Project;
* `projects=0` means the dictionary will extend an existing Project.

Correct every validation error before continuing.

Dry-run must perform no database writes.

---

# Application

Only after successful validation:

```bash
daurora-cmd import_planning_dictionary \
    <dictionary.plan> \
    --user delta \
    --apply
```

Expected success format:

```text
APPLIED: project=<slug> projects=<count> initiatives=<count> phases=<count> steps=<count>
```

All records must be created inside one database transaction.

A failed apply must not leave a partial Project, hierarchy, Step document,
validation record, or file record.

---

# Fallback Authorities

Load only when required.

Planning template:

```text
aurora/subsystems/planning/io/templates/
planning_update_v1.plan
```

Importer:

```text
aurora/management/commands/
import_planning_dictionary.py
```

Schema:

```text
aurora/subsystems/planning/io/schema.py
```

Updater:

```text
aurora/subsystems/planning/io/updater.py
```

Step CRUD payload and persistence:

```text
aurora/subsystems/planning/api/steps.py
```

Models:

```text
aurora/models.py
```

Load only the authority required to answer the current question.

---

# Hansel Rule

Load only the information required for the current task.

When repository knowledge ends:

Stop.

Request the missing fact.

Never replace missing information with assumptions.

Never ask the human to reconstruct repository paths, importer behavior, or data
shapes already owned by the repository.

The objective is not to minimize questions.

The objective is to eliminate unnecessary questions.

A successful planning session ends with one validated planning dictionary that
can create or extend the target Decision Engine Project without manual
modification.

---

# Completion Standard

The Planning Knowledge Pipeline is complete for one Initiative when:

* a durable Initiative source exists;
* the target Project decision is explicit;
* the dictionary starts from the canonical template;
* only schema-supported fields are present;
* Project creation is included only when required;
* every Phase is independently understandable;
* every Step is bounded;
* every Step has deterministic validation;
* planned files are included only when supported;
* actual files are not predicted;
* relevant discussion and design context are preserved;
* dry-run succeeds;
* apply succeeds transactionally;
* the hierarchy and Step supporting records are inspected;
* the source and resulting planning dictionary are committed;
* a future AI can repeat the workflow by following this authority chain.
