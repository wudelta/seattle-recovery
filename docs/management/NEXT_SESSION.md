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

That coupling caused repeated rendering failures, damaged review-panel markup, and risked interference with Anamod’s separate Monaco editor.

The Wu-assisted refactoring workflow will therefore be reconstructed from small, isolated components.

---

## Required User Workflow

The finished workflow should be:

```text
User:
“Refactor aurora/api/content_api.py”

    ↓

Aurora identifies and validates the repository-relative file path

    ↓

Aurora reads the file locally and adds its contents to Wu’s prompt

    ↓

Wu returns a structured patch wrapped in:

[PATCH_START: aurora/api/content_api.py]
...
[PATCH_END]

    ↓

Aurora parses the response and creates a pending code-change transaction

    ↓

The Wu-specific review slider opens

    ↓

A dedicated Monaco diff editor displays:

Current Code | Proposed Code

    ↓

User chooses:

Approve & Write
or
Reject Change
```

The user should not normally need to enter cryptic markers such as:

```text
[READ_FILE: ...]
```

Natural repository paths should be recognized from ordinary instructions.

---

## Architectural Boundaries

### 1. Workspace Context Resolver

Proposed module:

```text
aurora/minions/workspace_context.py
```

Responsibilities:

* recognize a repository-relative file path in the user request;
* optionally retain internal compatibility with `[READ_FILE: ...]`;
* resolve paths beneath `settings.BASE_DIR`;
* reject path traversal;
* reject directories;
* reject missing or unreadable files;
* read the current source locally;
* create a clearly delimited hydrated prompt for Wu.

It must not:

* call an AI provider;
* modify files;
* create transactions;
* know anything about Monaco.

---

### 2. Patch Response Parser

Proposed module:

```text
aurora/minions/patch_parser.py
```

Responsibilities:

* detect `[PATCH_START: path]`;
* detect the matching `[PATCH_END]`;
* extract the proposed replacement content;
* validate that the returned path matches the hydrated source target;
* reject incomplete or truncated patch responses;
* produce a structured diff payload.

Example payload:

```text
file_path
original_content
proposed_content
language
patch_complete
```

It must not:

* manipulate browser state;
* write to disk;
* invoke Monaco;
* contain provider-specific behavior.

---

### 3. Wu Diff Viewer

Proposed file:

```text
aurora/static/aurora/js/wu_diff_viewer.js
```

Responsibilities:

* own one Wu-specific Monaco diff editor;
* use a permanent, dedicated viewport;
* load original and proposed models;
* open and close the review slider;
* dispose replaced Monaco models safely;
* expose a small public interface.

Conceptual interface:

```javascript
window.WuDiffViewer.show(payload);
window.WuDiffViewer.hide();
```

It must never:

* replace parent containers with `innerHTML`;
* manipulate Anamod’s viewport;
* reuse Anamod’s editor instance;
* parse AI output;
* send chat requests.

---

### 4. Wu Chat Coordinator

Existing file:

```text
aurora/static/aurora/js/wu_chat.js
```

Responsibilities:

* submit chat requests;
* display conversational responses;
* pass structured diff payloads to `WuDiffViewer`;
* submit approval or rejection actions;
* maintain the active Wu transaction ID.

It should not own Monaco initialization or construct editor models directly.

---

### 5. Backend Orchestration

Existing file:

```text
aurora/api/wu_chat_api.py
```

Responsibilities:

1. receive the user instruction;
2. hydrate the instruction with safely loaded file contents;
3. send the hydrated prompt through `MinionRunner`;
4. parse a complete Wu patch response;
5. create a pending code-change transaction;
6. return structured review data to the browser.

Conversational responses must continue without creating code-change transactions.

---

## Isolation from Anamod

Anamod remains a standalone lightweight manual editor:

```text
File tree
    ↓
Select file
    ↓
Manual Monaco editor
    ↓
Save or discard
```

Wu’s diff viewer is a separate subsystem.

The two may share the globally loaded Monaco library, but they must not share:

* editor instances;
* models;
* DOM containers;
* lifecycle controls;
* save/discard state.

No Wu code may replace, clear, or traverse through Anamod’s DOM.

---

## Reconstruction Sequence

### Checkpoint 1 — Static Slider

Restore only the Wu review-slider markup.

Confirm:

* Wu Chat still loads;
* Anamod still loads;
* the hidden slider does not affect layout;
* the slider can be opened and closed manually.

### Checkpoint 2 — Isolated Monaco Diff Viewer

Create the dedicated Wu diff viewer.

Feed it hard-coded original and proposed strings.

Confirm:

* the diff appears;
* repeated open/close cycles work;
* Monaco models are cleaned up;
* Anamod remains operational.

### Checkpoint 3 — Structured Backend Payload

Implement patch parsing and return a hard-coded or manually supplied patch as structured JSON.

Confirm that `wu_chat.js` opens the viewer using only the returned payload.

### Checkpoint 4 — Workspace File Hydration

Implement safe natural-language file loading.

Confirm Wu receives the actual file contents and no longer requests a path that was already provided.

### Checkpoint 5 — Approval and Write

Create a code-change transaction containing:

* validated path;
* original content or checksum;
* proposed content.

On approval:

* verify the file has not changed since review;
* write the proposed content once;
* mark the transaction executed.

On rejection:

* write nothing;
* mark the transaction rejected or rolled back.

### Checkpoint 6 — Protocol Alignment

Update the `minion_wu` `DeltaDirectives` prompt to match the current refactoring protocol.

Remove or revise stale instructions involving:

* Gemini-only identity;
* the previous external-only patch protocol;
* obsolete TDD requirements;
* complete-file rewriting where surgical anchored patches are required;
* nonexistent automated file-fetch assumptions.

---

## Explicitly Rejected Techniques

Do not restore these behaviors from the previous branch:

```javascript
container.innerHTML = ...
```

Do not reconstruct the Monaco viewport on every response.

Do not put the complete slider, transaction, parser, and Monaco lifecycle inside `wu_chat.js`.

Do not merge `feature/wu-monaco-diff-slider` into `feature/provider-abstraction`.

Do not modify Anamod to support Wu-assisted refactoring.

Do not attempt file writes until the review UI works reliably with hard-coded content.

---

## Immediate Next Task

Begin with Checkpoint 1:

> Restore a static, isolated Wu review slider without connecting it to Wu, transactions, or backend parsing.

Required source inspection before modification:

```text
aurora/templates/aurora/snippets/wu_chat_console_panel.html
aurora/templates/aurora/aurora_console.html
```

The old branch’s slider markup may be used as a visual reference, but it should be cleaned and reconstructed rather than copied blindly.

Current branch:

```text
feature/provider-abstraction
```

Reference branch:

```text
origin/feature/wu-monaco-diff-slider
```

Stable provider-abstraction checkpoint:

```text
14ac790
```
