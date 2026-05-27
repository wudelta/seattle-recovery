# ARCHITECTURAL COMPONENT BLUEPRINT: AUTOMATED APP BUILDER

## 1. PROJECT META & CORE PARADIGM

* **Project Name:** Aurora / HopeHub
* **System Vision:** Fully automated, AI-assisted, web-based application builder.
* **Core Philosophy:** High-density context mapping, zero cloud dependency, token-optimized local pipelines.
* **Development Constraints:** 2 Cores, 8GB RAM, Groq Free-Tier API Limits.
* **The Core Meta-Loop:** Aurora is the AI-assisted engine built to automatically construct, test, and deploy HopeHub.

### 1.1 HOPEHUB MISSION STATEMENT & ETHICAL CORE

> "We provide practical, life-changing aid by solving the daily challenges that stand in the way of recovery. From housing and food to financial security and emotional support, our goal is to break the chains of substance use and despair. We replace hopelessness with a roadmap for growth, connection, and a well-being that lasts."

### 1.2 UX/UI DESIGN PRINCIPLES FOR RECOVERY MAPPING

* **Low Cognitive Load:** Interface must avoid cluttered data tables. Users under chronic stress require high-contrast, simple, step-by-step interactive workflows.
* **Immediate Utility First:** Practical aid (housing, food, crisis routing) must sit at the root level, requiring the absolute minimum number of clicks.
* **Visual Progression:** Layout must visually emphasize progress via node-based, graphical step trackers powered by Neo4j relationships.

---

## 2. PURGATORY ENGINE PROTOCOL: ZERO-QUICKSAND DEVELOPMENT MATRIX
**[DESCRIPTOR: STANDALONE DATA INFRASTRUCTURE & TERMINAL TEST PIPELINES]**

### 2.1 MANDATORY OPERATIONAL PHILOSOPHY
You are strictly forbidden from writing or modifying any code within monolithic, coupled systems where data processing and visual UI layouts fight for state control.
* **Decoupled Architecture:** All application layers must remain strictly decoupled.
* **Backend Boundaries:** Backend engine handles ONLY deterministic JSON data packages, database transactions, session boundaries, and system file manipulation.
* **Frontend Boundaries:** Interface presentation, visual formatting wrappers, loading spin-states, and visual empty-states are handled EXCLUSIVELY by the frontend client view layer.
* **Session Boundaries:** Enforce a strict One-Task-Per-Session boundary layer. Clear chat context arrays frequently via micro-sweeps to keep active tokens under the Groq free-tier ceiling.

### 2.2 THE THREE-STAGE PIPELINE CHECKLIST (REQUIRED EVERY STEP)

#### STAGE 1: PRINT-HEAVY, EXPLICIT TRACE ENGINE
Every view, function, loop, and file operation generated MUST contain sequential, alphanumeric stdout terminal `print()` statements tracking data progress milestones.
* **Tracking Prefix:** `print("🔍 [STAGE X] Description of active transaction metric payload...")`
* **Success Marker:** `print("✅ [STAGE X] Explicit confirmation of successful module completion.")`
* **Error Intercept:** `print("❌ [STAGE X CRASH] Anomaly captured: " + str(err))_`

#### STAGE 2: DEFENSIVE ERROR TRAPPING & SILENT CRASH PROTECTION
* **Strict Try/Except:** Wrap all network, database, file-handling, and subprocess execution code blocks inside strict `try/except` closures.
* **No Thread Freezes:** Never let an internal error freeze an application thread. Implement clear, localized safety fallbacks.
* **Asynchronous I/O:** Never write blocking external operating system executions. All network bound or I/O bound commands (such as `git push`, backups, or file exports) MUST be offloaded to an asynchronous background worker thread using `threading.Thread(daemon=True)`.

#### STAGE 3: BROWSER-FREE PIPELINE AUTOMATION TESTING
* **Terminal Suites:** Every feature module built must be accompanied by an independent, automated integration or unit testing script (`django.test.TestCase` framework) executable via `python manage.py test`.
* **Dynamic Lookup:** All URL testing endpoints must pull from native path naming maps using absolute dynamic lookups (e.g., `reverse('namespace:view_name')`) to eliminate relative string pathing mismatches.

### 2.3 CORE EXECUTABLE MINION ARRAY INTERFACE PROTOCOLS
When delegating mechanical file modification tasks to 8B Minion worker scripts:
1. **Trace Arrays:** Minions must output strict terminal trace arrays indicating precisely which files are targeted.
2. **Zero Chatter:** Minions are strictly limited to code generation, modification, and execution tasks. They must NEVER generate or write conversational chatter or human-centric filler notes to disk.
3. **Catastrophic Loss Prevention:** Every single file manipulation requires an explicit sanity check execution step to safeguard files against silent truncation or catastrophic data loss.

---

## 3. SYSTEM ENVIRONMENT & TECHNOLOGY INTEGRATION

### 3.1 Relational State Layer (PostgreSQL)
* **Role:** Multi-tenant user authentication, core transactional data, permission matrices, and token context tracking.
* **Optimization Component:** PostgreSQL Entity-Attribute-Value (EAV) micro-summary engine tracks and flushes active chat context histories to preserve RAM and Groq API token capacity.

### 3.2 Connected Knowledge Layer (Neo4j)
* **Role:** Dynamic application scaffolding mapping, UI element dependency graphs, and AI worker routing logic.
* **Driver Location:** `core_logic/neo4j_driver.py` (`Neo4jManager`)

### 3.3 Framework Dependencies
* **Core Backend:** Django 6.0.4 (Headless JSON Data Engine mode), Django REST Framework
* **Global Context Architecture:** `core_logic/memory.py` maps lazy-loading structures to prevent static verification check freezes.
* **Frontend Presentation:** Crispy Forms (Bootstrap 5), Bootswatch template themes, structured single-line footer tray dock containing active status gauges.

---

## 4. COMPRESSED APP INVENTORY & RESPONSIBILITY MATRIX

### 4.1 `aurora` App
* **Core Function:** The scaffolding forge. It holds the AI worker orchestration loops, code parsing utilities, and the developer interface you use to prompt Wu.
* **Key Targets:** Successful authentication forces a routing redirect to `aurora:landing` (the builder dashboard).

### 4.2 `hopehub` App
* **Core Function:** The production application. It manages recovery client intake, local resource tracking (housing networks, food distributions, support groups), and dynamic individual progress roadmaps.

### 4.3 `core_logic` App (System Engine)
* **Core Function:** Root URLs routing, global settings orchestration, shared driver instances.
* **Staging Directory:** `core_logic/staging/backups/` handles local dual-target persistence for `.dump` and `.tar.gz` binary rollbacks.

---

## 5. AI WORKER PARTITIONS & REGISTRATION SPECS

* **`NONE`**: Structural changes, global schema adjustments, cross-app architectural routing.
* **`CORE_PY`**: Execution of backend views, form validators, middleware development, and pure Python logic.
* **`UI_CSS`**: Layout aesthetics, Bootswatch theme custom modifications, styling scaffolding.
* **`DOM_JS`**: Single-page-app dynamic browser behaviors, local state handling, event triggers.
* **`DB_SQL`**: Relational tables migration scripts, raw Cypher syntax execution pipelines.
* **`SYS_GIT`**: Pipeline isolation protocols, local code version branch protection, safety tracking.
* **`MINION_ADD`**: Automated scripts dedicated to spinning up and registering brand new worker profiles.

---

## 6. SYSTEM FILES & SCRIPTS DIRECTORY

### 6.1 Session & Context Automation
* `start_online_session.py`: Handles the morning handshake protocol. Routes raw journal text inputs through Llama 3.1 8B minion context translation loops to construct Wu's active context envelope.
* `end_session_view.py` / `backup.py`: Triggers evening cleanup sequences, measures binary file sizes, and spins up a background thread for safe GitHub synchronization.
* Retention Rule: `backup.py` scans the backup staging folder and auto-deletes local archives older than 14 days to preserve disk limits.

### 6.2 Self-Healing Patch Pipeline
* `minion_patcher.py` / `minion_runner.py`: Controls a 4-layer sandboxed code patch matrix. Writes patches to `.tmp` scripts, triggers local `TestCase` validation, runs an AI self-healing retry block up to 3 times, and rolls back cleanly on terminal failures to prevent file truncation.
* Integration Hook: `SafeMinionPatcher.commit_safe_patch` connects directly to the core `chat_api` controller, allowing Wu (70B) to feed modifications straight down to the 8B minion file workers.

---

## 7. RE-SEED DATA PACKETS (CURRENT STATE WORKSPACE)

* **Active Working Models / Nodes:** None listed yet.
* **Active Routing Endpoints:**
  * `aurora:start_online_session` -> Wired to hidden layout input `id="aurora-start-session-endpoint"`
  * `aurora:micro_cleanup` -> Triggered via frontend footer button `🧹 Sweep RAM`

