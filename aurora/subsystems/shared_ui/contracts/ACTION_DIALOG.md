# ======================================================================
# FILE: aurora/subsystems/shared_ui/contracts/ACTION_DIALOG.md
# START: SHARED_UI_ACTION_DIALOG_CONTRACT
# ======================================================================

# Shared UI ActionDialog Contract

**Contract State: VERIFIED**

**Runtime State: VERIFIED**

---

## Purpose

`ActionDialog` is Aurora's reusable focused interaction surface for forms,
confirmations, and consequential actions that should not permanently consume
workspace space.

The capability originates from the concrete Decision Engine Review and Commit
workflow.

The shared implementation extracts only reusable presentation and interaction
mechanics.

It does not absorb Decision Engine or other consumer business behavior.

---

## Dialog Taxonomy Boundary

Aurora currently recognizes:

```text
ActionDialog
HelpDialog
DetailDialog
```

This contract governs only:

```text
ActionDialog
```

`HelpDialog` and `DetailDialog` are intentionally deferred.

Their future behavior must not be inferred from this contract.

A generic modal framework, modal registry, dialog registry, or universal dialog
base class is explicitly out of scope.

---

## Ownership Boundary

ActionDialog owns:

```text
full-screen modal presentation layer
bounded responsive dialog surface
header region
optional summary region
consumer-content region
generic status region
action footer
Cancel / Close control
primary-action control
open and close lifecycle
visibility and aria state
initial focus
focus containment
focus restoration
keyboard close behavior
body scrolling with reachable actions
generic busy / disabled interaction mechanics
```

The consuming subsystem owns:

```text
all domain-specific fields and content
domain data
selection state
authorization
domain validation
CSRF handling
API endpoints
request payload construction
persistence
business workflow
success semantics
error semantics
domain-specific labels and messages
```

The shared component must never determine whether a domain action is valid or
authorized.

---

## Repository Placement

Shared UI owns ActionDialog.

Runtime implementation belongs at these Aurora application frontend integration
surfaces:

```text
aurora/static/aurora/js/shared_ui/action_dialog.js
aurora/static/aurora/css/shared_ui/action_dialog.css
aurora/templates/aurora/shared_ui/action_dialog.html
```

These paths do not transfer ownership to the Aurora application shell.

They are framework integration surfaces for the `shared_ui` subsystem.

---

## Shared Structure

The reusable dialog surface must provide these conceptual regions:

```text
overlay
    dialog surface
        header
            title
            optional summary
            Cancel / Close
        scrollable body
            consumer-owned content
            generic status region
        footer
            primary action
```

The shared template must not contain Decision Engine-specific form fields,
messages, endpoint knowledge, or persistence semantics.

Consumer content must be injected into the shared body region.

---

## Responsive Layout and Scrolling

ActionDialog must:

```text
cover the active viewport with a modal overlay
center a bounded dialog surface
remain usable on smaller viewports
limit dialog height to the viewport
keep header and action footer reachable
allow the body to scroll independently when content exceeds available height
avoid forcing the entire Aurora console to scroll merely to reach dialog actions
```

The existing Decision Engine Review and Commit dialog is the concrete source of
these required mechanics.

Shared styling should generalize those mechanics rather than redesign the
consumer workflow.

---

## Open Lifecycle

Opening an ActionDialog must:

1. accept or already contain consumer-owned content;
2. populate shared title, summary, labels, and status presentation as requested
   by the consumer;
3. remember the element that held focus before opening;
4. expose the dialog;
5. set modal accessibility state consistently;
6. move focus into the dialog.

When the consumer identifies an initial-focus target, use it.

Otherwise focus the first appropriate focusable control inside the dialog.

Opening the dialog must not execute the primary domain action.

---

## Close Lifecycle

Cancel and Close use the same shared close lifecycle.

Closing must:

1. hide the dialog;
2. update accessibility visibility state;
3. clear transient shared presentation state that must not leak to the next use;
4. restore focus to the element that invoked or previously held focus before the
   dialog opened.

Closing the shared dialog must not independently mutate consumer domain state.

The consumer determines whether its own transient form or workflow state should
be preserved or reset.

---

## Keyboard and Focus Behavior

While open, ActionDialog must behave as a modal interaction surface.

At minimum:

```text
Escape
    closes through the shared close lifecycle

Tab / Shift+Tab
    remain within the dialog's focusable controls

initial focus
    enters the dialog

close
    restores prior focus
```

Backdrop clicks must not implicitly execute or approve an action.

Backdrop-close behavior is not required by this contract.

---

## Content Injection

The consumer owns the content displayed in the body region.

Shared UI may provide the container and lifecycle required to mount that content.

Shared UI must not require domain-specific markup inside the shared template.

Consumer content may include:

```text
form fields
review information
confirmation controls
domain guidance
domain-specific validation messages
```

Those elements remain owned by the consumer.

---

## Status Presentation

ActionDialog provides a generic status region suitable for deterministic
presentation of consumer-supplied state.

The consumer determines:

```text
the message
whether it represents validation, progress, success, or error
when it changes
whether the dialog remains open
```

Shared UI may provide presentation states and accessibility mechanics.

It must not interpret domain results.

Successful primary action must not automatically close the dialog unless the
consumer explicitly requests that behavior.

This preserves workflows such as Decision Engine, where successful completion
may leave the result visible and change Cancel to Close.

---

## Cancel / Close Semantics

The secondary dialog action is non-destructive shared interaction behavior.

Its label may be supplied or changed by the consumer, including:

```text
Cancel
Close
```

Activating it always follows the shared close lifecycle.

The shared layer must not treat `Cancel` as a domain rollback operation.

Any rollback or state mutation belongs to the consumer.

---

## Primary Action Semantics

ActionDialog provides one primary-action control.

The consumer supplies:

```text
primary label
primary callback
whether the action is currently enabled
domain validation
domain action behavior
```

The shared layer owns invocation mechanics only.

It must prevent accidental duplicate invocation while one asynchronous primary
action is already pending.

The component may present a generic busy/disabled state while that invocation is
pending.

It must not construct domain payloads, call domain endpoints, interpret domain
responses, or decide whether domain validation passed.

---

## Decision Engine Boundary

Decision Engine is the first concrete ActionDialog consumer.

The reusable mechanics currently embedded in its Review and Commit UI include:

```text
fixed full-screen overlay
centered bounded dialog surface
fixed header
independently scrolling body
reachable footer
dialog accessibility attributes
explicit open
explicit close
initial field focus
Cancel / Close control
primary action control
status presentation
```

Those mechanics are implemented by Shared UI.

Decision Engine adoption of the shared implementation remains a separate
consumer-migration responsibility.

Decision Engine retains ownership of:

```text
selected intake state
scope confirmations
work title
work description
commit reason
required-field rules
authorization
CSRF
commit API invocation
request construction
DecisionEngineWork persistence
commit success behavior
commit error behavior
```

Migration must preserve that boundary.

---

## Explicit Non-Goals

ActionDialog does not currently provide:

```text
HelpDialog behavior
DetailDialog behavior
dialog registries
modal registries
stacked dialogs
nested dialogs
arbitrary modal plugins
domain form generation
domain validation frameworks
API orchestration
authorization
persistence
generic workflow engines
```

Do not add these capabilities without a concrete consumer requirement and
separate architectural authority.

---

## Validation

The ActionDialog implementation is valid when a concrete consumer proves that:

1. the dialog opens and closes deterministically;
2. modal accessibility attributes reflect visibility;
3. focus enters the dialog and remains contained while open;
4. focus returns to the prior control when closed;
5. Escape follows the shared close lifecycle;
6. responsive bounds keep the dialog usable within the viewport;
7. the body scrolls independently when required;
8. header and action footer remain reachable;
9. generic status presentation remains available to the consumer;
10. primary action cannot be accidentally invoked twice while pending;
11. Cancel / Close performs only shared close mechanics;
12. no consumer-specific authorization, validation, API, persistence, or domain
    workflow exists in Shared UI.

The Shared UI runtime may be validated independently before any consumer is
migrated.

Decision Engine is the first required real consumer for end-to-end adoption
validation.

That later consumer validation must preserve the existing Decision Engine
commit transaction rather than replacing it with synthetic demonstration
behavior.

---

## Deferred Dialog Families

### HelpDialog

**Knowledge State: DEFERRED**

Known purpose:

> contextual help or explanatory content available on demand without permanent
> workspace allocation.

No behavior is specified here.

### DetailDialog

**Knowledge State: DEFERRED**

Known purpose:

> persisted or database-backed information available for inspection without
> permanent workspace allocation.

No behavior is specified here.

A future concrete consumer must establish each family's actual contract.

# ======================================================================
# END: SHARED_UI_ACTION_DIALOG_CONTRACT
# ======================================================================
