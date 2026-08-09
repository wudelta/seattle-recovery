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
* Content Django administration.

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
```

No service layer currently exists.

That is appropriate while Content remains a simple persistence-and-delivery
capability.

---

## Public Entry Points

Primary API entry point:

```text
aurora/subsystems/content/api/endpoint.py
```

Persistent content authority:

```text
aurora/subsystems/content/models.py
```

Administrative interface:

```text
aurora/subsystems/content/admin.py
```

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
```

The exact page-routing consumers are not established by this contract.

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

These are Django integration surfaces.

Domain ownership remains:

```text
aurora/subsystems/content/
```

---

## Validation Protocol

### Consumer Mapping

Before moving, renaming, or deleting Content models, fields, API symbols, or
content-routing integrations, identify consumers first.

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

The exact current routes and templates consuming `StaticContent` are not
enumerated here.

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

No additional Content contracts are currently authoritative.

A deeper contract should be created only if content lifecycle, publication,
security, or delivery complexity justifies it.

`HANSEL.md` remains the canonical discovery entry point.

---

## Hansel Rules for This Subsystem

A worker modifying Content must:

1. begin with this contract;
2. preserve Content as a lightweight persistence-and-delivery capability unless
   architecture explicitly expands its scope;
3. map consumers before moving or deleting assets;
4. perform tombstone validation after rename or removal;
5. preserve Django model identity during source-only moves;
6. validate content persistence and delivery behavior when those invariants
   change;
7. avoid introducing service layers or deeper contracts without a real
   responsibility;
8. update this contract when ownership, interfaces, consumers, or lifecycle
   change.

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

For unresolved consumer mapping:

```text
grep consumers of StaticContent and content API paths
```

# ======================================================================
# END: CONTENT_HANSEL_CONTRACT
# ======================================================================
