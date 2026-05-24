# Project Aurora: Strategic Plan & Workspace State Token
**Target Objectives Matrix for Session Date: 2026-05-25**
*Status: Architecture Verified, Dual-Target Local Persistence Active, Assets Synced to Git*

---

## 1. Active System State Profile (Where We Left Off)
*   **The Brain Core**: Django operates as a Headless JSON Data Engine. Global context initialization is fully insulated via lazy-loading structures inside `core_logic/memory.py` to prevent static verification check freezes.
*   **Morning Handshake (`start_online_session.py`)**: Fully verified via terminal unit tests (`OK`). Upgraded to route payloads straight through the Groq-powered Llama 3.1 8B minion context translation loop. *Status: Disconnected from browser UI.*
*   **Evening Cleanup (`end_session_view.py` / `backup.py`)**: Fully verified via terminal testing (`OK`). Upgraded to dual-target local persistence. Retains real database binary files (`.dump` and `.tar.gz`) inside `core_logic/staging/backups/` and accurately tracks raw file-size footprints on disk before executing background thread pushes to GitHub.
*   **Safe Execution Safeguards (`minion_patcher.py` / `minion_runner.py`)**: Built with a 4-layer file protection matrix. Zero-byte truncation is structurally impossible. Code patches write to a sandboxed `.tmp` file, run automated `TestCase` loops, and execute an AI-driven self-healing routine up to 3 times before rolling back cleanly from a backup copy.
*   **Web Interface Layout (`dashboard.html` / `script.js`)**: Highly optimized. Active buttons, log templates, and manual timing logs are fully consolidated into a responsive single-line footer tray dock, leaving the sidebar dedicated exclusively to status meters and gauges.

---

## 2. Active Backlog Objectives (Tomorrow's Checklist)

### Phase 1: Activate Morning Protocol Handshake (Priority 1)
- [ ] **Task 1.1**: Open `aurora/templates/aurora/dashboard.html` and add the hidden tracking input (`id="aurora-start-session-endpoint"`) using the namespaced URL template path map `{% url 'aurora:start_online_session' %}`.
- [ ] **Task 1.2**: Open `aurora/static/aurora/js/script.js` and add the asynchronous `executeMorningHandshakeSequence()` trigger at the very bottom of the page execution block.
- [ ] **Task 1.3**: Launch the local server and verify that loading the dashboard browser page immediately triggers the 8B minion to parse your plain-English journal entry and load Wu's ultra-dense context instructions envelope right on your screen.

### Phase 2: Live Continuous Sweeper Finalization & Routing
- [ ] **Task 2.1**: Map the namespaced path string for `path('micro-cleanup/', micro_cleanup_view, name='micro_cleanup')` directly inside `aurora/urls.py` to expose the new view engine to the web server.
- [ ] **Task 2.2**: Launch your browser console (F12) and click the newly styled **🧹 Sweep RAM** footer button. Ensure the terminal trace prints out your PostgreSQL EAV micro-summary storage success and rolls your token gauges back to safe baseline capacities.

### Phase 3: Active Subsystem Integration (Connecting Wu to Minions)
- [ ] **Task 3.1**: Connect `SafeMinionPatcher.commit_safe_patch` directly into your main `chat_api` view controller layer. This enables Wu 70B to pass patch specifications to the 8B worker to modify local files on disk natively on target test passes.
- [ ] **Task 3.2**: Execute an end-to-end task run using your natural journaling routine to ensure code additions are handled with zero human text translation required.

### Phase 4: The Automated Rolling Retention Cleaner
- [ ] **Task 4.1**: Create an automated utility sweep inside `core_logic/backup.py` to scan `core_logic/staging/backups/` and automatically delete local archives older than 14 days to preserve laptop hard disk limits over time.

---

## 3. Core Guardrails (Never Disobey)
1. **Never write frontend HTML template code blocks inside your Django backend files.** All data views must return pure, structured JSON payloads.
2. **Never troubleshoot file path parameters or API connection routes inside a web browser.** Always test data streams directly from your command line terminal using independent unit testing suites or `python manage.py test aurora`.
3. **Always offload network-bound operating system commands (such as cloud pushes or database backups) to a detached asynchronous background thread** to keep your development server lightning-fast.
4. **Never pile multiple features into a single workspace session.** Maintain a strict One-Task-Per-Session boundary layer, clearing chat context arrays frequently via micro-sweeps to keep active tokens under the Groq free-tier ceiling.
