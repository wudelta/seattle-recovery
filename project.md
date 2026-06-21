# ======================================================================
# PROJECT MILESTONE RECORD: SEATTLE RECOVERY ARCHITECTURE UPDATES
# TIMESTAMP: 2026-06-17 (DELTA-ARCHITECT SESSION CONFIRMATION)
# ======================================================================

## 1. COMPLETED ACCOMPLISHMENTS (CURRENT IMMACULATE BASELINE)
* [x] **Standalone /bind Architecture**: Implemented a pure, decoupled `/bind` workflow that maps frontend card views to backend JSON content streams using domain-agnostic, absolute app-root URLs.
* [x] **Zero-Dependency Native Fetch UI**: Migrated the front-end injection engine from jQuery dependent `$.ajax` syntax to an offline-first browser native `fetch()` layout. This eliminates CDN internet lookup loops and completely satisfies the local hardware constraint loop.
* [x] **Decoupled System Telemetry**: Built a stateless, thread-safe `TelemetryLogger` module utility (`aurora/utils/telemetry.py`) running on localized thread storage blocks.
* [x] **Utility Core Refactoring**: Overhauled both `page_skeleton.py` and `api_skeleton.py` core forge engines to scrub out old cross-coupled references and route status logs safely through the thread-isolated `TelemetryLogger`.
* [x] **Ironclad Test Suite Sandboxing**: Audited and refactored the entire test suite backlog (`test_api_ast_scanner.py`, `test_api_commands.py`, `test_api_dead_code.py`, `test_nodes.py`, and `test_page_skeleton.py`). Every suite now executes within randomized UUID file paths under `settings.BASE_DIR`.
* [x] **Defused Production Graph Pollution**: Eliminated dangerous global `DETACH DELETE` queries. Implemented a surgical, parameterized Cypher tracking sweep (`IN $paths` and signature constraints) to shield the live Neo4j production graph from data corruption.
* [x] **Modular Test Suite Partitioning**: Fragmented the high-density `test_api_commands.py` file into un-nested, highly focused Surgical Block Anchor patches under line limits.
* [x] **Minion Architecture Blueprinting**: Established the prompt definitions, structural markdown instructions, model targets (`llama-3.3-70b-specdec`), and JSON constraints (`thou_shalt` / `thou_shalt_not`) for `minion_test_writer` and `minion_AI_writer`.

## 2. ACTIVE BACKLOG (PENDING WORKSPACE DIRECTIVES)
* [ ] **Deploy Minion UI Creation Dashboard**: Build out the Django `MinionForgeForm`, views, and AJAX controller pipeline to sanitize, preview via regex parsing, and commit custom minion configurations to the `DeltaDirectives` PostgreSQL database.
* [ ] **Assemble Interactive QA Test Dashboard**: Implement the `test_minion_dashboard.html` template and connect the `scan_test_suite_violations` view route to enable one-click visual test suite auditing and dynamic auto-healing pipelines.
* [ ] **Production API Integration**: Populate the core database querying functions inside `hopehub/api/get_content_api.py` to replace placeholder arrays with relational-graph tandem lookups mapping live physical and mental well-being recovery action resources.

# ======================================================================
# END OF FILE: project.md (CURRENT STATE IMMUTABLE SNAPSHOT)
# ======================================================================


## Backlog Export Session Cluster (2026-06-21 21:26:27)
* [ ] in the aurora_console the pause button in the SESSION_TIME box is pink on pink so you can't read it. make it mimic the start session. leave it pink and don't change the style, just make it muted transparent until hover over. then change it to white on pink exactly like the Log Out button in aurora_base.html
* [ ] aurora/static/aurora/js/console.js has to be split up. snippets must have their own .js file and console.js is just for aurora_console.html. it also needs to be renamed aurora_console.js
* [ ] review the /bind command aurora/api/handlers/bind.py to see what it's currently doing and make sure it's ready for production.
* [ ] i can only see what /slash commands are available right now by looking in aurora/api/blueprint.py. i need a help view tied to the blueprint console that tells me the list of commands, a general description and the syntax for use. this needs to be updated by minion_slash_command when new ones are created.
* [ ] add a priority field to DeltaNotesEntry (1-10) to help prioritize tasks and make it required. then add a slide selector to DELTA_NOTES_CONSOLE_PANEL right below the text box, before the Add to Active Queue button.
* [ ] change the edit button on the UNPROCESSED_LOG to be more functional. right now its just a message box. it will no longer work once we add the priority field anyway.
* [ ] create a project_dashboard view in the console and a model. this view will be the next step in the project pipeline. it will take the unprocessed DeltaNotes entries and process them into AI instructions, assign to a minion and allow me to click an execute button. then they attempt to implement and submit for approval.
* [ ] i love this hover-over help text that pops up when i mouse over this text box in the CAPTURE_INTENTION dashboard. add that to the landing page vis graph in aurora first, and then hopehub.
* [ ] the SESSION_TIME needs to go somewhere and do something. add a time log table to the models and start logging active time spent in the console by user.
