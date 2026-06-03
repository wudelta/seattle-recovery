# Aurora Forge Project Blueprint

## 1. Core Vision & Objectives
* **The Mission:** Construct **Aurora**, an automated, token-optimized AI software engineering forge, to rapidly build, test, and maintain **HopeHub** (a low-stress resource navigation platform for substance use recovery).
* **The Workflow:** Shift Delta from manual programming to a solo architect role. Delta inputs plain-English instructions; **Wu (AI Lead, 70B)** coordinates and orchestrates; specialized **Minions (8B)** execute code generation; Aurora automatically inspects output.
* **The Target Environment:** Local-first, 100% network-independent, high-density dashboard workspace running entirely on consumer-grade hardware, completely eliminating the reliance on Spyder.

## 2. Technical Architectural Decisions
* **UI & Palette:** System-wide Bootswatch **Solar** theme (Solarized Dark) paired with high-contrast panel overrides inside `console.css`. Absolute clean separation: zero inline CSS styles or script logic inside template HTML files.
* **Frontend Stack:** Django templates utilizing **jQuery** for asynchronous interface pipeline execution and Bootstrap 5 for fluid viewport layout grid mechanics.
* **View Separation:** All view modules are strictly decoupled into individual, small, task-focused files inside the `aurora/views/` directory, whitelisted and exported securely via `views/__init__.py` to prevent AI namespace collisions.
* **Dependency Management:** Driven strictly by a clean `requirements.in` file, compiled and synchronized locally using `pip-tools` to match the exact developer environment footprints.
* **Quality Assurance Engine:** Spyder/Pyflakes are entirely replaced by **Ruff** (Rust-backed ultra-fast linter). Executed natively offline via Python `subprocess` streams targeting the explicit virtual environment binary path (`venv/bin/ruff`).

## 3. The Multi-Agent Minion Factory (Token Optimization Layer)
To stay safely inside Groq's free-tier rate limits, high-level orchestration is handled by the 70B model (Wu), while specialized, low-overhead code writing tasks are routed to targeted 8B models (Minions) running with strict system prompts:

* **HTML Minion:** Generates structural Django templates using fluid Bootstrap 5 layout grids. Strictly forbidden from writing inline CSS styles or script blocks. Utilizes standard block hooks and static tags.
* **JS Minion:** Writes isolated, specialized frontend script files inside `static/aurora/js/` using jQuery. Captures form inputs and streams requests asynchronously via `$.ajax` calls to backend endpoints.
* **API Minion:** Builds back-end view logic endpoints inside `views/`. Enforces a decoupled architecture by strictly returning `JsonResponse` payloads instead of standard HTML pages.
* **DB Minion:** Manages persistence and schema definitions, routing data based on strict project rules:
    * **Postgres:** Handles tabular transactional records, application accounting logs, user authentication, and system access profiles.
    * **Neo4j:** Maps complex interconnected data, individual user recovery roadmaps, resource network trees, and milestone correlations.

## 4. Current Operational Baseline (Where We Are At)
* [x] Core user login/logout modules configured using native Django authentication logic.
* [x] High-density fluid 4-panel terminal console cockpit successfully built (`templates/aurora/aurora_console.html`).
* [x] Strict view separation layout architecture locked down (`views/console_view.py` and `views/api_views.py`).
* [x] Local static configuration structure mapped natively (`static/aurora/css/console.css` and `static/aurora/js/console.js`).
* [x] Repository tracking securely streamlined: heavy virtual environment files (`venv/`) purged from Git cache history and `.gitignore` updated to block `venv/` and `.venv/` permanently. Remote backup up-to-date on GitHub.
* [x] Background automated execution engine (`inspector.py`) built to intercept code blocks, pass them to the local Ruff tool, and return diagnostic errors or warnings to the console UI.

## 5. Immediate Next Staging Steps (Tomorrow's Vector)
1. **Agent Setup Initialization:** Create `aurora/agents.py` to house the system prompts, temperature balances (0.1–0.2 for low-hallucination code output), and model constraints for the 4 specialized minions.
2. **Groq Interface Gateway View:** Replace the mock string data loop inside `views/api_views.py` with the functional Groq package execution pipeline, letting Wu parse your Blueprint Desk commands.
3. **Task Routing Orchestration:** Write the JSON routing logic where Wu breaks down a single architecture command and dynamically feeds the structured requirements down the minion assembly chain.

