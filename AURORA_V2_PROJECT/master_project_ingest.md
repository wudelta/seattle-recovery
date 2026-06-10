# ======================================================================
# MASTER AI PROJECT INGEST: SEATTLE RECOVERY (AURORA & HOPEHUB)
# IDENTITY CONTEXT: DELTA (PROJECT ARCHITECT)
# HARDWARE STATUS: OFFLINE-FIRST / LOCAL HOST (2-CORE / 8GB RAM)
# ======================================================================

[SYSTEM_INSTRUCTION: READ AND PARSE THIS CONTEXT BLOCK PRIOR TO EXECUTING ANY REFACTORING, SYNTAX SCALPEL GENERATION, OR SCHEMATIC ARCHITECTURE LAYOUTS. COMMIT ALL BOUNDING INSTRUCTIONS TO LONG-TERM RUNTIME MEMORY.]

## 1. ECOSYSTEM CORE ARCHITECTURE
The "Seattle Recovery" project is a dual-application ecosystem structured using an enterprise-grade, decoupled Relational-Graph Tandem engine. It is optimized to run locally under severe hardware constraints (2 Cores, 8GB RAM, Ubuntu Desktop).

                  +---------------------------------------+

                  |         Web UI (Bootstrap / jQuery)   |
                  +---------------------------+-----------+

                                              | (REST APIs)
                                              v
                  +---------------------------+-----------+
                  |      Django REST Framework (DRF)      |
                  +---+-------------------------------+---+

                      |                               |
                      v (Transactional / Auth)        v (Graph Queries)
                  +---+--------------+            +---+--------------+

                  | PostgreSQL (SQL) |            |  Neo4j (Graph)   |
                  +------------------+            +------------------+

### APP 1: AURORA (The Engine)
* **Purpose**: An AI-assisted application builder that automates software development tasks.
* **Objective**: Rapidly, safely, and deterministically construct the production application (HopeHub).
* **AI Orchestration (Wu)**: Powered by Groq's free tier. Wu functions **strictly online**. 
* **Offline-First Constraint**: Due to strict free-tier token limits and unpredictable local Wi-Fi connectivity, **all core mechanics are architecture-bound to be local and offline-first**. 
* **Execution Boundary**: Code parsing, file assembly, and skeleton layout templates must use zero-token local utilities (`page_skeleton.py`, `api_skeleton.py`). Wu is reserved exclusively for high-level orchestration, complex multi-step reasoning, and systemic structural transformations.

---

### APP 2: HOPEHUB (The Platform)
* **Purpose**: A comprehensive recovery and case management system for individuals experiencing homelessness, substance use disorders, and mental health issues.
* **Objective**: Act as an automated case manager to deliver physical and emotional well-being action plans.
* **Client Interface**: Highly responsive, local-first Bootstrap frontends driven via decoupled jQuery API callbacks.
* **Graph Responsibility**: Maps complex non-linear relationships between real-world community resources, shelter availability, medical services, and specific user needs.

---

## 2. COMPONENT DECOUPLING & BACKEND SPECIFICATION
* **Framework**: Python 3 / Django Web Framework.
* **API Decoupling Layer**: `djangorestframework` (DRF). Every interface component maps to a clean, isolated backend script inside designated `app/api/*_api.py` namespaces. No database records leak directly into raw template variables.
* **Relational Storage Layer**: PostgreSQL. Handles all transactional logic, administrative tracking loops, security credentials, and identity access control. User data must be fully encrypted, sandboxed, and isolated.
* **Graph Network Layer**: Neo4j. Operating via local Docker loopback port mappings password-free. Leverages background Django Post-Save and Post-Delete signals (`signals.py`) to keep the relational and network data models synchronized in real time.

---

## 3. STRICT AI GENERATION RULES & CONSTRAINTS

### CONSTRAINT A: SURGICAL BLOCK ANCHOR ENGINE (FILE EDITS)
To prevent network drops, token bloating, and source file truncation under low-bandwidth/low-spec execution environments, AI engines must **NEVER** dump whole source files if changes are localized. All file modifications must use the exact format below:

```python
# ======================================================================
# FILE: [app_name]/[module_path].py (PATCH X OF Y)
# START: [DESCRIPTIVE_SEGMENT_HEADING]
# ======================================================================
[Fully indented, functional python/html/javascript code block]
# ======================================================================
# END: [DESCRIPTIVE_SEGMENT_HEADING]
# ======================================================================
```

### CONSTRAINT B: TWIN-TRACK TESTING MANDATE (TDD)
* No functional adjustment to business logic, routing channels, or backend endpoints is valid without a simultaneous accompanying verification update.
* Every code module requires its exact matching `test_page_*.py` or `test_api_*.py` test file.
* Framework code generation scripts must write matching test suites out directly into the live development workspace directory structure.

### CONSTRAINT C: TRANSACT-GRAPH ISOLATION LOOP
* Any test suite writing, updating, or wiping records inside the Relational-Graph Tandem system must guarantee state isolation.
* To prevent race conditions, index collisions, or deadlocks over local port structures, the active graph loopback must execute a complete Cypher flush (`MATCH (n) DETACH DELETE n`) during its internal `setUp()` and `tearDown()` execution tasks.

---

## 4. DOCUMENTATION STRATEGY MATRIX
All assets produced under the project lifecycle must maintain multi-audience compliance across a Docs-as-Code markdown strategy:
1. **Developer Track**: Raw API specifications (OpenAPI/Swagger), AST graph schema dependencies, and transactional migrations.
2. **Stakeholder Track**: Functional architectural layout context views (C4 Model layout schemas) establishing systemic scope and project safety.
3. **End-User Track**: Simple, clear, non-technical instructions, flowcharts, and operational guides explaining action-plan workflows.

---

## 5. Incremental Refactoring Protocol (The "Go" Loop)
When Delta feeds the AI a file to refactor, upgrade, or extend, the engine must never return the entire file or multiple patches at once. The engine must strictly parse and deliver the update using the following conversational loop:
1. **The Partition Task**: Break the code updates down into highly localized, un-nested Surgical Block Anchor patches (e.g., `PATCH 1 OF X`, `PATCH 2 OF X`).
2. **The Single-Block Lock**: Deliver exactly **one single block** (e.g., `PATCH 1 OF X`) in the response window.
3. **The Yield Block**: Immediately halt output generation, provide a brief summary of what that specific patch modifies, and wait for Delta's confirmation.
4. **The Step Signal**: The AI must not output the next sequential patch until Delta explicitly enters the text variable keyword: **"go"**.
5. **Numbering Continuity Retention**: When returning patches for a file containing pre-existing numbered blocks, the engine must strictly preserve the file's original master index layout numbering (e.g., matching `PATCH 4 OF 5`) to prevent pipeline parsing offsets.

---

## 6. Refactoring & Code Delivery Standards
1. **Modification Trimming**: When refactoring or delivering codebase updates, only return patches that contain active modifications. Do not output unedited code blocks.
2. **Line Count Limits**: Keep individual code chunks under 100 lines of code whenever possible, with a strict maximum limit ceiling of 200 lines per patch.

---

## 7. Immediate Next Staging Steps (Todays's Vector)
1. **Automated AST Dependency Topography Scanner**: Build the local static file code analyzer to parse import statements inside newly forged modules and dynamically register `DEPENDS_ON` graph links in Neo4j.
2. **Dead Code Isolation Utility**: Build a zero-token `/cleanup` or routing check that walks the Neo4j incoming relationship paths to flag and safely isolate any orphaned, unreferenced components.
3. **Agent Setup Orchestration**: Verify system configurations inside `aurora/agents.py` and activate Wu's 70B model gateway payload parameters to decompose plain English instructions down to targeted 8B Minions.

# ======================================================================
# END OF INGEST PROFILE - RUN TARGET LOGIC NOW
# ======================================================================
