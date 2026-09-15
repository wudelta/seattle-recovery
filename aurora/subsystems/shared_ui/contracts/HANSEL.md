# ======================================================================
# FILE: aurora/subsystems/shared_ui/contracts/HANSEL.md
# START: SHARED_UI_HANSEL_CONTRACT
# ======================================================================

# Shared UI — Hansel Catalogue

**Knowledge State: VERIFIED**

**Subsystem:** shared_ui

---

## Purpose

Shared UI owns reusable Aurora user-interface capabilities whose presentation
and interaction lifecycle is shared across consuming subsystems rather than
owned by one domain subsystem.

Its first concrete capability is `ActionDialog`.

Shared UI does not own the domain content or business behavior placed inside a
shared UI component.

---

## Ownership Boundary

Shared UI owns reusable presentation and interaction mechanics such as:

```text
layout
visibility lifecycle
shared visual structure
scrolling behavior
focus behavior
keyboard interaction
accessibility mechanics
generic status presentation
generic action controls
```

Consuming subsystems retain ownership of:

```text
domain content
domain data
authorization
domain validation
API calls
CSRF handling
persistence
business workflow
success and error semantics
```

A shared UI component must not become a second authority for the subsystem that
consumes it.

---

## Dialog Families

Aurora currently recognizes three dialog families.

### ActionDialog

**Knowledge State: VERIFIED**

Use for forms, confirmations, or consequential user actions that require a
focused interaction surface without permanently consuming workspace space.

Current authority:

```text
aurora/subsystems/shared_ui/contracts/ACTION_DIALOG.md
```

`ActionDialog` is the only dialog family currently approved for implementation.

### HelpDialog

**Knowledge State: DEFERRED**

Intended for contextual explanatory or help content that should be available on
demand without permanently consuming workspace space.

No HelpDialog behavior or implementation is currently defined.

Do not infer ActionDialog behavior as HelpDialog behavior.

### DetailDialog

**Knowledge State: DEFERRED**

Intended for persisted or database-backed information that a user may need to
inspect but which does not justify dedicated permanent workspace space.

No DetailDialog behavior or implementation is currently defined.

Do not infer ActionDialog behavior as DetailDialog behavior.

---

## Repository Map

Current subsystem-owned authorities:

```text
aurora/subsystems/shared_ui/contracts/HANSEL.md
aurora/subsystems/shared_ui/contracts/ACTION_DIALOG.md
```

ActionDialog runtime assets will use Aurora application-level frontend
integration surfaces because Aurora's current static and template structure is
rooted under the Aurora application.

The planned runtime placement is defined by the ActionDialog authority:

```text
aurora/subsystems/shared_ui/contracts/ACTION_DIALOG.md
```

Runtime paths do not become Hansel breadcrumbs until those repository
authorities actually exist.

Ownership remains with the `shared_ui` subsystem.

---

## Knowledge Catalogue

### Define or change ActionDialog behavior

Go to:

```text
aurora/subsystems/shared_ui/contracts/ACTION_DIALOG.md
```

Use this authority when the task concerns:

```text
ActionDialog ownership
dialog lifecycle
shared dialog structure
content injection
status presentation
Cancel / Close behavior
primary-action mechanics
responsive layout
scrolling
focus
keyboard interaction
accessibility
```

### Implement ActionDialog runtime mechanics

Read first:

```text
aurora/subsystems/shared_ui/contracts/ACTION_DIALOG.md
```

Then use the runtime surfaces declared there.

Do not place consuming-subsystem business behavior into Shared UI.

### Add HelpDialog behavior

**Knowledge State: DEFERRED**

Do not implement HelpDialog merely because the dialog family is known.

A concrete consumer must establish the required behavior before its contract or
implementation is designed.

### Add DetailDialog behavior

**Knowledge State: DEFERRED**

Do not implement DetailDialog merely because the dialog family is known.

A concrete consumer must establish the required behavior before its contract or
implementation is designed.

---

## Dependencies

Shared UI depends on Aurora's browser runtime and existing application frontend
integration surfaces.

ActionDialog may consume Bootstrap-compatible styling already loaded by Aurora,
but Shared UI must not require a consuming subsystem to duplicate dialog
mechanics.

Shared UI does not depend on a consuming subsystem's domain services.

---

## Consumers

The first concrete ActionDialog consumer is Decision Engine.

Decision Engine owns its own Review and Commit workflow.

Shared UI owns only the reusable dialog presentation and interaction mechanics
extracted from that concrete need.

Additional consumers are added only when real subsystem requirements appear.

---

## AI Usage

Shared UI contains no AI-owned runtime behavior.

Its UI mechanics must remain deterministic.

---

## Validation

Shared UI changes must prove:

1. the canonical `contracts/HANSEL.md` remains valid;
2. declared deeper contracts resolve;
3. shared behavior remains free of consuming-subsystem business logic;
4. application-level static and template surfaces remain attributable to
   Shared UI;
5. the concrete consuming workflow used for validation still behaves correctly.

Validation must target the architectural claim being changed.

---

## Known Gaps

`ActionDialog` runtime implementation is PLANNED until its implementation Step
is executed.

`HelpDialog` is DEFERRED.

`DetailDialog` is DEFERRED.

A generic modal framework, dialog registry, or universal dialog abstraction is
not planned.

---

## Unknown Territory

If the catalogue does not identify sufficient authority for a Shared UI task:

1. do not invent component behavior or architecture;
2. inspect the narrowest concrete consumer that exposed the requirement;
3. distinguish reusable mechanics from consumer-owned behavior;
4. add shared behavior only when a real cross-subsystem responsibility exists;
5. add a breadcrumb only when discovery reveals a durable authority future
   workers should not have to rediscover.

---

## Sufficient Authority

Stop following breadcrumbs when all four are known:

1. who owns the behavior;
2. what must change;
3. what must remain unchanged;
4. how the change will be validated.

Do not design neighboring shared UI capabilities merely because they are known.

---

## Catalogue Reconciliation

After completing Shared UI work, ask:

> Has this change made a Shared UI breadcrumb, ownership boundary, dialog-family
> state, or runtime integration path stale?

If no, no Hansel change is required.

If yes:

1. update the affected breadcrumb;
2. remove obsolete routing;
3. add routing only for durable knowledge destinations;
4. verify changed breadcrumbs resolve to repository authorities.

Keep this catalogue navigational.

# ======================================================================
# END: SHARED_UI_HANSEL_CONTRACT
# ======================================================================
