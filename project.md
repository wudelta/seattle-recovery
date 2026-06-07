# ======================================================================
# FILE: project.md (PATCH 1 OF 3)
# START: RESTORE_INCREMENTAL_REFACTOR_PROTOCOL
# ======================================================================
## 6. Incremental Refactoring Protocol (The "Go" Loop)
When Delta feeds the AI a file to refactor, upgrade, or extend, the engine must never return the entire file or multiple patches at once. The engine must strictly parse and deliver the update using the following conversational loop:

1. **The Partition Task**: Break the code updates down into highly localized, un-nested Surgical Block Anchor patches (e.g., `PATCH 1 OF X`, `PATCH 2 OF X`).
2. **The Single-Block Lock**: Deliver exactly **one single block** (e.g., `PATCH 1 OF X`) in the response window.
3. **The Yield Block**: Immediately halt output generation, provide a brief summary of what that specific patch modifies, and wait for Delta's confirmation.
4. **The Step Signal**: The AI must not output the next sequential patch until Delta explicitly enters the text variable keyword: **"go"**.
# ======================================================================
# END: RESTORE_INCREMENTAL_REFACTOR_PROTOCOL
# ======================================================================

# ======================================================================
# FILE: project.md (PATCH 2 OF 3)
# START: UPDATE_OPERATIONAL_BASELINE_TIMER_POSITION
# ======================================================================
## 4. Current Operational Baseline (Where We Are At)
* [x] Core user login/logout modules configured using native Django authentication logic.
* [x] High-density fluid 4-panel terminal console cockpit successfully built (`templates/aurora/aurora_console.html`).
* [x] Dual-Tier View Stream Router finalized inside `views/api_views.py` supporting `/page`, `/api`, and `/destroy` commands.
* [x] Overhauled API scaffolding generation to route components directly into clean, isolated `app/api/` directories using the `*_api.py` paradigm.
* [x] Integrated local-first frontend `console.js` data variables securely with backend parameter keys.
* [x] Converted the `ComponentRegistry.created_by` field from open text to a strict Django Auth User ForeignKey, locking down immutable developer accountability tracking.
* [x] Purged all heavy environment configurations (`venv/`) permanently from repository tracking history.
* [x] Background execution engine (`inspector.py`) operational natively offline via Python subprocess tracking.
* [x] Core Zero-Token multi-app template disk generation engine fully locked in (`page_skeleton.py`).
* [x] Core Zero-Token functional API endpoint generation engine fully locked in (`api_skeleton.py`).
* [x] Upgraded both skeleton engines to write visual block comments natively into generated templates, class views, and verification tests.
* [x] Shifted generated unit test architecture from self-destruction routines to non-destructive production verification checking against the active workspace folder tree.
* [x] Connected targeted Cypher isolation blocks into sandboxed test setup loops, preventing duplicate key database constraints.
* [x] Resolved list index slicing argument evaluation failures inside core endpoint action routes.
* [x] Modified the universal infrastructure obliterator (`/destroy`) to run real-time Cypher detach drops directly against Neo4j, avoiding bypassed row signals.
* [x] Implemented Relational-Graph Tandem Data Logging Engine mapping application assets simultaneously.
* [x] Connected Neo4j Docker Loopback Cluster running password-free natively over local host port mappings.
* [x] Deployed background Django Post-Save and Post-Delete Signals (`signals.py`) automating real-time graph node syncs.
* [x] Built the `DeltaNotesEntry` tracking model with full database migration protocols.
* [x] Decoupled DeltaNotes interface logic completely into an app-scoped static script (`aurora/static/aurora/js/delta_notes.js`).
* [x] Extracted DeltaNotes styling layer completely into an app-scoped static stylesheet (`aurora/static/aurora/css/delta_notes.css`) for a tightened console layout.
* [x] Centralized task focus timers from row-level scopes into a single global dashboard control clock.
* [x] Migrated session focus timer controls onto the right boundary of the main workspace utility header box.
# ======================================================================
# END: UPDATE_OPERATIONAL_BASELINE_TIMER_POSITION
# ======================================================================

# ======================================================================
# FILE: project.md (PATCH 3 OF 3)
# START: CLEAN_COMPLETED_VECTORS
# ======================================================================
## 5. Immediate Next Staging Steps (Tomorrow's Vector)
1. **Automated AST Dependency Topography Scanner:** Build the local static file code analyzer to parse import statements inside newly forged modules and dynamically register `DEPENDS_ON` graph links in Neo4j.
2. **Dead Code Isolation Utility:** Build a zero-token `/cleanup` or routing check that walks the Neo4j incoming relationship paths to flag and safely isolate any orphaned, unreferenced components.
3. **Agent Setup Orchestration:** Verify system configurations inside `aurora/agents.py` and activate Wu's 70B model gateway payload parameters to decompose plain English instructions down to targeted 8B Minions.

## 6. Incremental Refactoring Protocol (The "Go" Loop)
When Delta feeds the AI a file to refactor, upgrade, or extend, the engine must never return the entire file or multiple patches at once. The engine must strictly parse and deliver the update using the following conversational loop:
1. **The Partition Task**: Break the code updates down into highly localized, un-nested Surgical Block Anchor patches (e.g., `PATCH 1 OF X`, `PATCH 2 OF X`).
2. **The Single-Block Lock**: Deliver exactly **one single block** (e.g., `PATCH 1 OF X`) in the response window.
3. **The Yield Block**: Immediately halt output generation, provide a brief summary of what that specific patch modifies, and wait for Delta's confirmation.
4. **The Step Signal**: The AI must not output the next sequential patch until Delta explicitly enters the text variable keyword: **"go"**.
# ======================================================================
# END: CLEAN_COMPLETED_VECTORS
# ======================================================================
