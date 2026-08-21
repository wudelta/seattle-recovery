# ======================================================================
# FILE: aurora/subsystems/content/contracts/HANSEL.md
# START: CONTENT_HANSEL_CONTRACT
# ======================================================================

# Content — Hansel Catalogue

## Purpose

Content owns Aurora's lightweight persisted informational HTML content.

It stores and serves standalone content without acting as a full CMS.

---

## Knowledge Catalogue

### Understand or change Content data

Go to:

```text
aurora/subsystems/content/models.py
```

### Understand or change Content API behavior

Go to:

```text
aurora/subsystems/content/api/endpoint.py
```

### Understand or change Content UI

Go to:

```text
aurora/subsystems/content/contracts/UI_MAP.md
```

Use this authority for:

```text
Content Registry presentation
editor behavior
Workflow Controls
Operational Pipeline Log Feed
Content-specific styling
```

### Understand or change Content administration

Go to:

```text
aurora/subsystems/content/admin.py
```

---

## Ownership Boundary

Content owns:

```text
StaticContent persistence
application classification
stored HTML content
Content API behavior
Content administration
Content-specific browser behavior
```

Content does not own:

```text
full CMS workflow
Planning state
Component Registry metadata
AI execution
Wu Chat behavior
repository documentation
```

---

## Framework Integration

Content model integration is exposed through:

```text
aurora/models.py
```

Content administration is loaded through:

```text
aurora/admin.py
```

Content browser/template integration is routed through:

```text
aurora/subsystems/content/contracts/UI_MAP.md
```

Domain ownership remains:

```text
aurora/subsystems/content/
```

---

## Validation

Validation must match the changed responsibility.

Examples:

```text
content remains readable;
application classification remains intact;
stored HTML persists correctly;
authorized administrative editing still works;
Content UI continues to load and mutate records;
Operational Pipeline Log Feed remains newest-first and visible.
```

For model-source moves, also use:

```text
dmakemigrations --check
daurora-cmd check
```

---

## Unknown Territory

If the requested responsibility is not mapped here:

1. do not infer ownership;
2. inspect the narrowest likely Content authority;
3. cross subsystem boundaries only when required;
4. add a breadcrumb only for a durable route future workers should not have to
   rediscover.

---

## Sufficient Authority

Stop discovery when all four are known:

1. who owns the behavior;
2. what must change;
3. what must remain unchanged;
4. how the change will be validated.

---

## Catalogue Reconciliation

After changing Content, ask whether this catalogue or `UI_MAP.md` still routes
the affected responsibility correctly.

Update only durable ownership routes.

# ======================================================================
# END: CONTENT_HANSEL_CONTRACT
# ======================================================================
