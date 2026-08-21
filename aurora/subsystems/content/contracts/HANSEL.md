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