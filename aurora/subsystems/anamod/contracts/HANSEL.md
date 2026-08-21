# ======================================================================
# FILE: aurora/subsystems/content/contracts/HANSEL.md
# START: CONTENT_HANSEL_CONTRACT
# ======================================================================

# Content — Hansel Contract

**Knowledge State:** VERIFIED
**Subsystem:** `content`

---

## Purpose

Content stores and serves standalone informational HTML content used by Aurora
and HopeHub.

It provides a lightweight persisted content source for informational pages
without introducing a full CMS.

---

## Ownership Boundary

Content owns:

* persistent `StaticContent` records;
* application-level content classification;
* stored HTML content;
* Content API behavior;
* Content Django administration;
* Content-specific client-side UI behavior.

Content does not own:

* page routing outside its API integration;
* full CMS workflow;
* repository documentation;
* Planning state;
* Component Registry metadata;
* AI execution;
* orchestration;
* Wu Chat behavior.

---

## Canonical Data Authority

Authoritative model:

```text
aurora/subsystems/content/models.py
    StaticContent
```

Current persisted state includes:

```text
application
title
html_content
created_by
date_created
date_modified
```

Supported application values currently include:

```text
aurora
hopehub
```

---

## Repository Map

```text
content/
    admin.py
        Django administration for StaticContent.

    models.py
        Authoritative StaticContent persistence model.

    api/
        endpoint.py
            Content API behavior.

    contracts/
        HANSEL.md
            Canonical Hansel discovery entry point.

        UI_MAP.md
            Routes Content UI work to the owning template, JavaScript,
            and CSS authorities.
```

No service layer currently exists.

That is appropriate while Content remains a simple persistence-and-delivery
capability.

Content also owns browser and template integration surfaces outside the Python
subsystem directory. Those are mapped through `UI_MAP.md`.

---

## Public Entry Points

### Content API

Primary API entry point:

```text
aurora/subsystems/content/api/endpoint.py
```

### Persistent Content Authority

```text
aurora/subsystems/content/models.py
```

### Administrative Interface

```text
aurora/subsystems/content/admin.py
```

### Content UI

Primary UI routing contract:

```text
aurora/subsystems/content/contracts/UI_MAP.md
```

Use this authority when the task concerns Content Console structure, browser
interaction, operational-log behavior, or Content-specific styling.

---

## AI Usage

Content does not currently own AI-assisted behavior.

**Knowledge State:** VERIFIED

If AI-assisted authoring or transformation is introduced later, persisted
content must remain distinguishable from generated drafts or transient AI
output.

---

## Dependencies

### Django

Content depends on:

```text
Django ORM
Django admin
Django API/request handling
Django static/template integration
```

### Aurora User Model

Content authorship references:

```text
settings.AUTH_USER_MODEL
```

No additional subsystem dependency is established by this contract.

---

## Consumers

Known consumers include:

```text
Aurora
    May serve persisted informational content.

HopeHub
    May serve persisted informational content classified for HopeHub.

Django admin
    Provides administrative content management.

Aurora Console
    Hosts the Content management interface.
```

The exact page-routing consumers of persisted Content records are not fully
established by this contract.

**Knowledge State:** UNKNOWN

Next breadcrumb:

```text
aurora/subsystems/content/api/endpoint.py
```

and repository consumers of `StaticContent`.

---

## Framework Integration Surfaces

Content models are re-exported through:

```text
aurora/models.py
```

Content admin registration is loaded through:

```text
aurora/admin.py
```

Content browser and template integration surfaces are routed through:

```text
aurora/subsystems/content/contracts/UI_MAP.md
```

These are framework integration surfaces.

Domain ownership remains:

```text
aurora/subsystems/content/
```

---

## Validation Protocol

### Consumer Mapping

Before moving, renaming, or deleting Content models, fields, API symbols, UI
assets, or content-routing integrations, identify consumers first.

Example:

```bash
grep -RIn <old-path-or-symbol> aurora hopehub core_logic
```

---

### Tombstone Validation

After rename, move, or deletion, verify obsolete references no longer exist.

Expected:

```text
no live references
```

---

### Model Survival Validation

For source-only model moves:

```bash
dmakemigrations --check
daurora-cmd check
```

Expected:

```text
No changes detected
System check identified no issues
```

Where appropriate, also verify:

```text
StaticContent.__module__
StaticContent._meta.app_label
StaticContent._meta.db_table
existing row count
```

---

### Admin Survival Validation

After moving Content admin configuration, verify:

```text
StaticContent in admin.site._registry
```

Expected:

```text
True
```

---

### UI Survival Validation

Content UI changes should prove the affected behavior directly.

For operational-log changes, verify:

```text
🖥️ Operational Pipeline Log Feed is visible
newest message appears at the top
older messages remain below
latest activity is visible without manual scrolling
existing Content actions still emit their existing messages
```

For other UI changes, follow:

```text
aurora/subsystems/content/contracts/UI_MAP.md
```

to identify the narrowest template, JavaScript, or CSS authority.

---

### Behavioral Survival Validation

Changes to Content behavior should prove the affected invariant.

Examples include:

```text
content remains readable;
application classification remains intact;
stored HTML remains persisted;
authorized administrative editing still works.
```

Validation should match the actual claim made by the change.

---

## Known Gaps

### Consumer Map

**State:** UNKNOWN

The exact current routes and templates consuming `StaticContent` records are not
fully enumerated here.

Next breadcrumb:

```text
grep consumers of StaticContent and the Content API
```

Do not infer active consumers from the existence of stored content alone.

---

### CMS Boundary

**State:** VERIFIED

Content is intentionally lightweight.

It is not currently a full content-management system.

If workflow complexity grows enough to justify drafts, publishing states,
versioning, approval, or richer authoring behavior, that should be treated as an
architectural expansion rather than silently embedded into the existing simple
subsystem.

---

## Deeper Contracts

For Content UI ownership:

```text
aurora/subsystems/content/contracts/UI_MAP.md
```

No other deeper Content contracts are currently authoritative.

Additional contracts should be created only if content lifecycle, publication,
security, or delivery complexity justifies them.

`HANSEL.md` remains the canonical discovery entry point.

---

## Hansel Rules for This Subsystem

A worker modifying Content must:

1. begin with this contract;
2. preserve Content as a lightweight persistence-and-delivery capability unless
   architecture explicitly expands its scope;
3. follow `UI_MAP.md` for Content UI work;
4. map consumers before moving or deleting assets;
5. perform tombstone validation after rename or removal;
6. preserve Django model identity during source-only moves;
7. validate content persistence and delivery behavior when those invariants
   change;
8. preserve existing browser behavior unless the task explicitly changes it;
9. avoid introducing service layers or deeper contracts without a real
   responsibility;
10. update this contract when ownership, interfaces, consumers, lifecycle, or
    durable UI routing changes.

---

## Next Hansel Breadcrumb

For the authoritative model:

```text
aurora/subsystems/content/models.py
```

For API behavior:

```text
aurora/subsystems/content/api/endpoint.py
```

For administration:

```text
aurora/subsystems/content/admin.py
```

For Content UI behavior:

```text
aurora/subsystems/content/contracts/UI_MAP.md
```

For unresolved consumer mapping:

```text
grep consumers of StaticContent and content API paths
```

# ======================================================================
# END: CONTENT_HANSEL_CONTRACT
# ======================================================================