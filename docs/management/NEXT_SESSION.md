# Wu Assisted Refactoring — Clean Reconstruction Plan

## Decision

The former `feature/wu-monaco-diff-slider` implementation will be used only as a behavioral reference.

It will not be merged, checked out over the current branch, or copied wholesale.

The previous implementation coupled:

* Wu response handling
* transaction state
* Monaco lifecycle
* dynamic DOM replacement
* approval controls

That coupling caused repeated rendering failures, damaged review-panel markup, and risked interference with Anamod's separate Monaco editor.

During the Provider Abstraction refactor, the historical command-oriented
transaction system (`WorkspaceTransaction` and `TrackedCommand`) was
completely removed from the codebase.

The Wu-assisted refactoring workflow is now based on a structured,
review-first architecture and will be reconstructed from small,
isolated components.

---

# Current Architecture Status (2026-07-12)

## Completed

✓ Provider abstraction complete

✓ ProviderRouter baseline validated

✓ Wu Chat restored

✓ WorkspaceTransaction removed

✓ TrackedCommand removed

✓ Database migrated successfully

✓ Django system check passes cleanly

✓ Workspace context resolver implemented and integrated

✓ Structured patch parser implemented and integrated

✓ Backend now returns structured patch payloads

## Remaining

* reconnect Wu review UI
* reconnect Monaco diff viewer
* complete PendingCodeChange approval workflow
* validate end-to-end repository patch review

---

# Required User Workflow

The finished workflow should be:

```text
User:
"Refactor aurora/api/content_api.py"

        ↓

Aurora identifies and validates the repository-relative file path

        ↓

Aurora safely reads the repository file

        ↓

Aurora hydrates Wu's prompt with the current source

        ↓

Wu returns

[PATCH_START: aurora/api/content_api.py]
...
[PATCH_END]

        ↓

Aurora validates and parses the structured patch

        ↓

Aurora returns a structured review payload

        ↓

Wu Review Slider opens

        ↓

Dedicated Monaco Diff Viewer displays

Current Code | Proposed Code

        ↓

Developer chooses

Approve

or

Reject

        ↓

Approve creates a PendingCodeChange

        ↓

PendingCodeChange performs one verified repository write

        ↓

Reject performs no repository mutation
```

The user should not normally need to type explicit markers such as

```text
[READ_FILE: ...]
```

Natural repository-relative paths should be recognized automatically.

`[READ_FILE: ...]` remains available only as an explicit compatibility
override.

---

# Architectural Boundaries

## 1. Workspace Context Resolver

Module

```text
aurora/minions/workspace_context.py
```

Status

```text
COMPLETE
```

Responsibilities

* recognize repository-relative paths
* support `[READ_FILE: ...]`
* validate repository boundaries
* reject traversal
* reject directories
* reject missing files
* read local source
* hydrate Wu prompts

Must never

* invoke providers
* modify files
* create PendingCodeChange objects
* know anything about Monaco

---

## 2. Structured Patch Parser

Module

```text
aurora/minions/patch_parser.py
```

Status

```text
COMPLETE
```

Responsibilities

* detect

```text
[PATCH_START]
```

and

```text
[PATCH_END]
```

* validate target path
* reject malformed responses
* reject truncated responses
* reject multiple patch blocks
* produce structured review payloads

Payload

```text
file_path
original_content
proposed_content
language
patch_complete
```

Must never

* manipulate browser state
* write files
* invoke Monaco
* call AI providers

---

## 3. Wu Diff Viewer

Proposed module

```text
aurora/static/aurora/js/wu_diff_viewer.js
```

Status

```text
PENDING
```

Responsibilities

* own one Wu Monaco Diff Editor
* own its lifecycle
* own its models
* own the review slider

Public interface

```javascript
window.WuDiffViewer.show(payload);
window.WuDiffViewer.hide();
```

Must never

* replace parent DOM with innerHTML
* reuse Anamod editor instances
* parse AI output
* submit chat requests

---

## 4. Wu Chat Coordinator

Module

```text
aurora/static/aurora/js/wu_chat.js
```

Status

```text
IN PROGRESS
```

Responsibilities

* submit chat requests
* display conversation
* receive

```text
patch
patch_error
```

payloads

* invoke WuDiffViewer
* submit approvals
* submit rejections

Must not

* construct Monaco editors
* parse AI responses
* perform repository writes

---

## 5. Backend Orchestration

Module

```text
aurora/api/wu_chat_api.py
```

Status

```text
PARTIALLY COMPLETE
```

Responsibilities

1. receive instruction

2. resolve workspace context

3. hydrate prompt

4. execute MinionRunner

5. parse structured patch

6. return review payload

The backend intentionally performs **no repository mutations**.

Repository writes occur only after explicit user approval.

---

## 6. PendingCodeChange

Status

```text
PARTIALLY IMPLEMENTED
```

Responsibilities

* store validated review
* verify source consistency
* perform one safe write
* record approval status

PendingCodeChange replaces the historical
WorkspaceTransaction architecture.

---

# Isolation from Anamod

Anamod remains a standalone manual editor.

```text
File Tree

↓

Manual Monaco Editor

↓

Save / Discard
```

Wu Review remains an independent subsystem.

Shared

* Monaco library

Never shared

* editor instances
* editor models
* DOM containers
* lifecycle
* save state

Wu code must never manipulate Anamod's DOM.

---

# Reconstruction Sequence

## ✓ Checkpoint 1

Backend cleanup

COMPLETE

* removed WorkspaceTransaction
* removed TrackedCommand
* migrated database

---

## ✓ Checkpoint 2

Workspace Context

COMPLETE

* repository resolution
* safe hydration
* prompt construction

---

## ✓ Checkpoint 3

Structured Patch Parser

COMPLETE

* patch validation
* payload creation
* backend integration

---

## Checkpoint 4

Wu Review Slider

NEXT

Restore an isolated static review slider.

No Monaco.

No backend.

Layout validation only.

---

## Checkpoint 5

Dedicated Monaco Diff Viewer

Load hard-coded

* original
* proposed

Verify

* repeated open/close
* model cleanup
* Anamod unaffected

---

## Checkpoint 6

Frontend Integration

Consume

```text
response.patch
response.patch_error
```

Open WuDiffViewer.

No file writes.

---

## Checkpoint 7

PendingCodeChange Approval

Approve

* verify source
* write once
* complete transaction

Reject

* no write

---

## Checkpoint 8

DeltaDirective Cleanup

Update

`minion_wu`

to align with

Protocol v3.2

Remove

* Gemini-specific assumptions
* obsolete prompt wording
* historical transaction references
* outdated TDD instructions
* complete-file rewrite assumptions

---

# Explicitly Rejected Techniques

Never restore

```javascript
container.innerHTML = ...
```

Never recreate Monaco on every response.

Never combine

* parser
* slider
* Monaco
* chat
* approval

inside

```text
wu_chat.js
```

Never merge

```text
feature/wu-monaco-diff-slider
```

into

```text
feature/provider-abstraction
```

Never modify Anamod to support Wu.

Never perform repository writes before successful review.

---

# Immediate Next Task

Begin Checkpoint 4.

Restore a static, isolated Wu Review Slider.

Connect **no backend**.

Connect **no Monaco**.

Confirm

* Wu Chat still operates
* Anamod still operates
* layout remains stable
* slider opens
* slider closes

After layout validation, proceed incrementally through:

* Monaco viewer
* frontend payload integration
* PendingCodeChange approval

Required inspection

```text
aurora/templates/aurora/snippets/wu_chat_console_panel.html

aurora/templates/aurora/aurora_console.html
```

Reference branch

```text
origin/feature/wu-monaco-diff-slider
```

Behavior reference only.

Never merge directly.

Current branch

```text
feature/provider-abstraction
```

Stable provider abstraction checkpoint

```text
14ac790
```

---

# Engineering Principle

The Wu-assisted development workflow shall remain composed of small,
isolated, independently testable components.

Provider execution, workspace hydration, patch parsing, review UI,
approval, and repository mutation are separate architectural concerns.

Each layer should be replaceable without affecting the others.

Apply The Delta Way:

> Small.
> Reversible.
> Production-safe.
> One checkpoint at a time.