# ======================================================================
# FILE: project.md (PATCH 1 OF 1)
# START: MINION_FLEET_DEVELOPMENT_BACKLOG
# ======================================================================
## Current Progress & Finished Milestones (June 2026)
* [x] **Step 1: Database Schema Expansion**
  * Implemented `StaticContent` and `DeltaDirectives` with cascading relational rules.
  * Added `DeltaDirectives.provision_standard_minions(parent)` factory to seed the core fleet (`minion_wu`, `minion_UI_layout`, `minion_UI_style`, `minion_UI_logic`, `minion_anamod`, `minion_AI_writer`).
  * Automated migrations applied; unit tests are passing perfectly.
* [x] **Step 2: Universal Execution Engine Construction**
  * Created `aurora/minions/engine.py` with the `MinionRunner` engine.
  * Configured engine for the Groq Cloud API gateway (`llama-3.3-70b-versatile` and `llama-3.1-8b-instant`).
  * Enforced mock test environment coverage inside `test_minion_engine.py` to prevent local API key leaks.

---

## Roadmap & Pick-Up Plan for Next Session

### Task A: Construct the Automated Workspace Crawler Documenter
Create the dedicated utility script inside `aurora/utils/documenter.py`. This script will replace the old `minion_documenter.py` file to handle filesystem operations separate from the AI engine core.
* [ ] Implement an active directory walker loop using `ComponentRegistry.objects.filter(status="ACTIVE")`.
* [ ] Read raw target code modules cleanly into memory from disk paths.
* [ ] Invoke the `MinionRunner().run_minion_task("minion_AI_writer", prompt)` loop to generate high-quality summaries.
* [ ] Call `asset.update_audience_docs()` to write documentation blocks back to PostgreSQL columns.
* [ ] Write a matching `test_workspace_documenter.py` test suite with graph isolation blocks.

### Task B: Hook `minion_wu` into the Slash Command Router
Integrate the 70B orchestrator directly into your Command Pattern routing logic to coordinate complex, multi-step player inputs.
* [ ] Open `aurora/api/blueprint.py`.
* [ ] Modify the plain-English fallback gateway (`else:` block inside `execute_blueprint_api`) to pass unmapped execution requests to `minion_wu`.
* [ ] Instruct Wu to parse complex developer text commands, return a structured list of operations, and delegate code generation steps to the 8B minion modules.
# ======================================================================
# END: MINION_FLEET_DEVELOPMENT_BACKLOG (PATCH 1 OF 1)
# ======================================================================
