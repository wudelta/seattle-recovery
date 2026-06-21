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

