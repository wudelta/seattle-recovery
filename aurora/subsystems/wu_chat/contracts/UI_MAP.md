# ======================================================================
# FILE: aurora/subsystems/wu_chat/contracts/UI_MAP.md
# START: WU_CHAT_UI_MAP
# ======================================================================

# Wu Chat UI Map

## Purpose

Route Wu Chat UI tasks to the narrowest authoritative template or browser
module.

This file is a map, not a UI specification.

---

## Workspace Structure and Panel Layout

For Wu Chat workspace structure, column sizing, Session Management layout,
Fleet Telemetry layout, action placement, and code-review slider markup:

```text
aurora/templates/aurora/wu_chat/wu_chat_console_panel.html
```

---

## Core Wu Chat Browser Behavior

For the primary Wu Chat browser workflow, chat interaction, and core
client-side coordination:

```text
aurora/static/aurora/js/wu_chat/wu_chat.js
```

---

## Engineering Session UI

For Engineering Session controls, Session Management workflow status,
Step-work controls, Planning lifecycle review controls, and registry-session
controls:

```text
aurora/static/aurora/js/wu_chat/engineering_session.js
```

This is the first browser authority to inspect for:

```text
⚙ Session Management
Start Step Work
End Step Work
Complete Step
Planning completion review
Refresh Registry
Enrich Registry
```

Engineering Session domain behavior remains owned by:

```text
aurora/subsystems/engineering_session/
```

---

## Delta Notes Session Workflow

For Delta Note processing inside Wu Chat, including supervised Delta Note to
Planning proposal/review behavior:

```text
aurora/static/aurora/js/wu_chat/delta_notes_session.js
```

Known responsibilities include:

```text
Process Delta Notes
Resolve / No Action
Send to Planning
Reject Proposal
Approve Planning Proposal
Delta Note Planning proposal messages
```

Delta Notes persistence remains owned by the Delta Notes subsystem.
Planning generation and mutation remain owned by Planning.

---

## Code Review and Monaco Diff

For Wu-specific current-versus-proposed code review behavior:

```text
aurora/static/aurora/js/wu_chat/wu_diff_viewer.js
```

Known responsibilities include:

```text
Monaco diff creation
current/proposed source display
review slider open/close behavior
target repository path display
```

---

## Operational Pipeline Log Feed

Operational log markup lives in:

```text
aurora/templates/aurora/wu_chat/wu_chat_console_panel.html
```

The output element is:

```text
#wu-telemetry-screen-output
```

The verified browser writer is:

```text
aurora/static/aurora/js/wu_chat/wu_chat.js
```

Known responsibilities include Wu Chat telemetry-stream events, socket
messages, and Wu-specific system alerts for operational visibility.

Normalization target:

```text
label: 🖥️ Operational Pipeline Log Feed
newest message at the top
older history below
viewport remains at the top after a new message
```

This operational log remains distinct from Session Management, which presents
human-facing workflow state and actions.

---

## Session Management Output

Session Management markup lives in:

```text
aurora/templates/aurora/wu_chat/wu_chat_console_panel.html
```

The primary browser workflow authority is:

```text
aurora/static/aurora/js/wu_chat/engineering_session.js
```

The Delta Note workflow may also append Session Management messages through:

```text
aurora/static/aurora/js/wu_chat/delta_notes_session.js
```

Use the narrowest owning module for the specific workflow being changed.

---

## Framework Loading

When the task concerns whether a Wu Chat script is included, loading order, or
initialization wiring, inspect:

```text
aurora/templates/aurora/aurora_console.html
```

Do not treat Aurora Console script inclusion as ownership of Wu Chat behavior.

---

## Unknown UI Territory

If a Wu Chat UI responsibility is not mapped here:

1. do not infer ownership from a filename;
2. inspect the narrowest known template or browser authority first;
3. if ownership remains unresolved, search the exact DOM ID, event name, or
   exported browser symbol;
4. inspect the discovered implementation directly;
5. update this map only when the result is a durable UI route future workers
   should not have to rediscover.

---

## Sufficient Authority

Stop UI discovery when all four are known:

1. which template or browser module owns the presentation behavior;
2. which subsystem owns any underlying domain behavior;
3. what must remain unchanged;
4. how the UI change will be validated.

Do not load every Wu Chat JavaScript module merely because it exists.

---

## Authority Reconciliation

After changing Wu Chat UI structure or module responsibilities, ask:

> Does this UI map still route each affected concern to the correct authority?

If yes, no update is required.

If no:

1. repair stale routes;
2. remove obsolete routes;
3. add new routes only for durable UI authorities;
4. verify every changed path exists.

The objective is accurate UI navigation, not implementation documentation.

# ======================================================================
# END: WU_CHAT_UI_MAP
# ======================================================================
