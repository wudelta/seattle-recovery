# ======================================================================
# FILE: aurora/subsystems/component_registry/contracts/HANSEL.md
# START: COMPONENT_REGISTRY_HANSEL_CONTRACT
# ======================================================================

# Component Registry — Hansel Catalogue

## Purpose

Component Registry maintains Aurora's searchable inventory of repository
components.

It owns deterministic repository discovery, registry reconciliation, registry
synchronization, and semantic component enrichment.

Neo4j projection is derived and optional.

---

## Knowledge Catalogue

### Refresh the Component Registry

Run:

```text
daurora-cmd maintain_component_registry
```

This is the normal deterministic maintenance entry point.

It:

```text
reconciles repository state
updates changed components
registers new components
archives missing components
leaves REVIEW items for human decision
queues changed and new components for AI enrichment
```

No human user identity is required.

### Enrich pending Component Registry records

Run:

```text
daurora-cmd enrich_component_registry
```

This is the normal operational AI enrichment entry point.

It processes active `PENDING` components until:

```text
the enrichment queue is exhausted
or
an AI provider failure stops the run
```

Provider failures leave the interrupted component `PENDING` so the same command
can be run again later to resume naturally.

### Preview or test bounded AI enrichment

Go to:

```text
aurora/management/commands/document_component_registry.py
```

Use this precision interface when a bounded `--path`, `--limit`, preview, or
explicit test run is required.

Do not use it as the normal operational enrichment workflow.

### Preview repository and registry differences

Go to:

```text
aurora/management/commands/reconcile_component_registry.py
```

Use this precision interface for bounded inspection, debugging, or targeted
registry operations.

Do not use it as the normal daily maintenance workflow.

### Change routine maintenance behavior

Go to:

```text
aurora/subsystems/component_registry/services/maintenance.py
```

### Change repository reconciliation behavior

Go to:

```text
aurora/subsystems/component_registry/services/reconciler.py
```

### Change registry mutation behavior

Go to:

```text
aurora/subsystems/component_registry/services/synchronizer.py
```

### Change component registration behavior

Go to:

```text
aurora/subsystems/component_registry/services/registry.py
```

### Change repository inclusion or classification policy

Go to:

```text
aurora/subsystems/component_registry/services/component_policy.py
```

### Change AI description generation

Go to:

```text
aurora/subsystems/component_registry/services/documenter.py
```

### Understand or change Component Registry data

Go to:

```text
aurora/subsystems/component_registry/models.py
```

### Understand or change Component Registry administration

Go to:

```text
aurora/subsystems/component_registry/admin.py
```

### Work with repository dependency analysis

Go to:

```text
aurora/subsystems/component_registry/services/dependency_analyzer.py
```

### Work with optional Neo4j graph projection

Go to:

```text
aurora/subsystems/component_registry/services/graph_projection.py
aurora/subsystems/component_registry/nodes.py
```

Neo4j is not part of the current Component Registry maintenance pipeline.

Treat it as a derived projection only when graph capability provides explicit
decision value.

### Perform explicit disaster-recovery reset

Go to:

```text
aurora/management/commands/reset_component_registry.py
```

This command deletes all PostgreSQL Component Registry records and Neo4j
ComponentNode projections.

It is not part of normal maintenance.

After an intentional reset, rebuild with:

```text
daurora-cmd maintain_component_registry
daurora-cmd enrich_component_registry
```

Do not run reset merely to refresh or repair ordinary registry state.

---

## Maintenance Model

Normal Component Registry operation is:

```text
repository
    ↓
daurora-cmd maintain_component_registry
    ↓
deterministic reconciliation
    ↓
UPDATE / REGISTER / ARCHIVE
    ↓
structurally current registry
    ↓
PENDING enrichment queue
    ↓
daurora-cmd enrich_component_registry
    ↓
semantic registry knowledge
```

Repository freshness must not depend on AI availability.

AI enrichment is required for useful semantic registry knowledge, but it may be
deferred until the machine is online and the operation is practical to run.

---

## Unknown Territory

If the task is not covered by this catalogue:

1. do not infer ownership or behavior;
2. inspect the immediate Component Registry subsystem structure for the
   narrowest likely authority;
3. follow another authority only when the task crosses an ownership boundary;
4. add a Hansel breadcrumb only when discovery reveals a durable knowledge
   destination that future workers should not have to rediscover.

---

## Sufficient Authority

Stop following breadcrumbs when all four are known:

1. who owns the behavior;
2. what must change;
3. what must remain unchanged;
4. how the change will be validated.

Do not load additional Component Registry context merely because it exists.

---

## Catalogue Reconciliation

After completing a change, ask:

> Has this change made a Component Registry breadcrumb or maintenance route
> stale?

If no, no Hansel update is required.

If yes:

1. update the affected breadcrumb;
2. remove obsolete routing;
3. add new routing only for durable knowledge destinations;
4. verify changed breadcrumbs resolve to existing authorities.

Do not expand this catalogue with implementation details learned during the
task.

The objective is accurate navigation.

# ======================================================================
# FILE: aurora/subsystems/component_registry/contracts/HANSEL.md
# END: COMPONENT_REGISTRY_HANSEL_CONTRACT
# ======================================================================
