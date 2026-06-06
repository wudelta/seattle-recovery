# ======================================================================
# MASTER DIRECTIVES: THE SURGICAL ANCHOR & LIFECYCLE TESTING PARADIGM
# ======================================================================

## 1. File Modification Protocols (Anti-Truncation)
All future code generations, automated refinements, and file edits must adhere strictly to the **Surgical Block Anchor** pattern. Under no circumstances should complete files exceeding 100 lines be dumped or completely rewritten if modifications are localized.

### Explicit Syntax Rules:
*   Every critical logical segment (imports, core view setups, sub-routes, database transactions) must be explicitly bounded by high-visibility uppercase headers and footers.
*   **The Content Contract**: Code updates must only output the precise section requiring modification, enabling the architect to select from anchor-to-anchor in their IDE for seamless replacement.

```python
# ======================================================================
# FILE: [app_name]/[module_path].py (PATCH X OF Y)
# START: [DESCRIPTIVE_SEGMENT_HEADING]
# ======================================================================
[Fully indented, functional code block]
# ======================================================================
# END: [DESCRIPTIVE_SEGMENT_HEADING]
# ======================================================================
```

## 2. Code Generation Engine Mandates
The `PageSkeletonBuilder` and `ApiSkeletonBuilder` must natively write these exact visual anchors into the files they forge. 
*   **HTML Templates**: Must include structured structural comment tags bounding content regions.
*   **Python Modules**: Must write explicit anchor comments wrapping imports, core execution functions, and payload format blocks on initialization.

## 3. Mandatory Testing Lifecycle Parity
No modification to system mechanics or routing blocks is complete without immediate test alignment. 
*   **The Twin-Track Rule**: Every functional code adjustment requires an immediate corresponding audit of its standalone `test_page_*.py` or `test_api_*.py` suite.
*   **Database Isolation Rules**: All test configurations executing data writes against the Relational-Graph Tandem engine must explicitly issue a clean Cypher disconnect and wipe (`MATCH (n) DETACH DELETE n`) during `setUp()` and `tearDown()` cycles to prevent transactional state leakage in the Neo4j loopback port mappings.

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
* [x] Upgraded both skeleton engines to write comprehensive lifecycle tests that validate physical code files alongside real-time Postgres and Neo4j data footprints out of the box.
* [x] Implemented Relational-Graph Tandem Data Logging Engine mapping application assets simultaneously.
* [x] Connected Neo4j Docker Loopback Cluster running password-free natively over local host port mappings.
* [x] Deployed background Django Post-Save and Post-Delete Signals (`signals.py`) automating real-time graph node syncs.

## 5. Immediate Next Staging Steps (Tomorrow's Vector)
1. **Automated AST Dependency Topography Scanner:** Build the local static file code analyzer to parse import statements inside newly forged modules and dynamically register `DEPENDS_ON` graph links in Neo4j.
2. **Dead Code Isolation Utility:** Build a zero-token `/cleanup` or routing check that walks the Neo4j incoming relationship paths to flag and safely isolate any orphaned, unreferenced components.
3. **Agent Setup Orchestration:** Verify system configurations inside `aurora/agents.py` and activate Wu's 70B model gateway payload parameters to decompose plain English instructions down to targeted 8B Minions.
