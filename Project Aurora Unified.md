# Project Aurora: Unified Architecture Blueprint
**System Specification & Verified Workflow Matrix**
*Status: Verified and Operational via Asynchronous Testing Core*

---

## 1. System Philosophy: The Decoupled Data Core
Project Aurora eliminates the architectural friction of monolithic web engines by separating data processing from layout presentation. 
* **The Brain (Django Backend)**: Functions strictly as a Headless JSON Data API Engine. It handles token caching, context retrieval, Neo4j memory writing, and automated OS automation tasks. It does not parse UI assets or execute layout scripts.
* **The Interface Layer (Frontend)**: Consumes raw JSON packets natively. Visual states, loader toggles, and formatting loops occur on the client viewport, keeping backend python scripts completely isolated from browser memory crashes.

---

## 2. Verified Operational State Machine (Daily Routine)

```text
 🌅 MORNING INITIALIZATION        ⚙️ ACTIVE CONSOLE CONTROL          🌙 EVENING CLEANUP
┌──────────────────────────┐     ┌──────────────────────────┐     ┌──────────────────────────┐
│ • Ingest Staging Brief   │     │ • 70B Core Handles Code  │     │ • Generate Day Summary   │
│ • Compute Planning Delta │ ──> │ • 8B Minions Modify Files│ ──> │ • Wipe Raw Chatter RAM   │
│ • Inject 5-Day Summaries │     │ • Graph Memory Captures  │     │ • Detach Off-Thread Git  │
│ • Build System Envelope  │     │ • Zero Minion Chatter    │     │ • Push to Upstream Git   │
└──────────────────────────┘     └──────────────────────────┘     └──────────────────────────┘
```

### Phase 1: The Morning Handshake Protocol
* **Endpoint Mapped**: `POST /aurora/api/session/start/` (`aurora:start_online_session`)
* **Execution Sequence**:
  1. Captures system clock timestamp metrics to calculate offline planning duration against file metadata on disk (`core_logic/staging/daily_brief.txt`).
  2. Routes raw text blocks into the local **Llama 8B translation worker** (`run_8b_translation`) to condense requirements into compact abstract strings and explicit JSON objectives.
  3. Commits structured logging tables data into PostgreSQL using the explicit Document/Content EAV targets.
  4. Automatically extracts historical entries from the **previous 5 days** of development, formatting them chronologically to build out baseline session context maps.
  5. Packages these metrics into a self-contained **System Prompt Envelope**, setting a strict boundary environment for Wu before development begins.

### Phase 2: Active Workspace & Token Mitigation
* **Endpoint Mapped**: `POST /aurora/api/v1/stream/` (`aurora:wu_data_stream`)
* **The Token Saver Directive**: 
  * All primary architectural prompts and engineering decisions run through **Llama 3.3 70B (The Brain)**, writing conversational nodes directly into your Neo4j memory graph space.
  * Mechanical utility tasks (running file modifications, scanning directories) are delegated headlessly to **Llama 3.1 8B (The Minions)**. Minion worker operations execute silently in the background, bypass conversational memory graph logging entirely to conserve daily Groq free-tier tokens, and require your explicit safety confirmation before running text modifications.

### Phase 3: The Evening Automated Cleanup
* **Endpoint Mapped**: `POST /aurora/end_session/` (`aurora:end_session`)
* **Execution Sequence**:
  1. Invokes internal graph logic routines to generate a structured project **Day Summary** node, updating the main project log index.
  2. Sweeps the graph database, **deleting the raw conversational chatter nodes** to preserve optimal tracking workspace performance.
  3. Closes out the active session row in PostgreSQL and registers the final tracking duration metrics.
  4. Spawns an isolated, asynchronous background thread (`asynchronous_git_pipeline`) to handle file snapshots, instantly disconnecting the web request loop in **0.01 seconds** to prevent browser freezes.
  5. The detached background worker thread runs `git add -A`, executes a staged differential check, runs your automated timestamp commit, and dispatches your codebase straight to your upstream **GitHub** repository.

---

## 3. Automation Guardrails & Test Matrix
* **Browser-Free Validation**: Changes to core APIs must be verified independently in the terminal using native Django testing mechanisms. This shields development metrics from browser caches and layout overrides.
* **Cache-Proof Execution**: Off-thread background workers are wrapped inside fail-safe handlers, guaranteeing that network I/O blockages or server timeouts can never crash your live development session interface.

```bash
# Command to execute your independent terminal integration suite
python manage.py test aurora.tests
```
