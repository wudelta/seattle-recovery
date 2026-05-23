## Project Aurora: Unified Architecture Blueprint
System Blueprint & Workflow Specification
------------------------------
## 1. Architectural Strategy: The Headless Shift
Project Aurora is moving away from a monolithic structure where Django tries to process data and render HTML interfaces simultaneously. To prevent script path crashes and template caching issues, the platform is adopting a Decoupled System Architecture.

* The AI Data Core (Backend): Django operates strictly as a headless JSON Data API Engine. It manages database graphs, handles session persistence, enforces security tokens, and controls model processing endpoints. It never touches layout code, stylesheets, or interface rendering.
* The Interface Layer (Frontend): The user interface is treated as a separate layout layer. Because it reads raw JSON data packets directly, it manages interface elements natively. Empty states, formatting wrappers, element visibility, and character length counting occur on the frontend without altering backend python scripts.

------------------------------
## 2. The Operational State Machine (Daily Workflow Loop)

 🌅 MORNING PROTOCOL              ⚙️ ACTIVE WORKSPACE               🌙 EVENING PROTOCOL
┌──────────────────────────┐     ┌──────────────────────────┐     ┌──────────────────────────┐
│ • Input Daily Brief      │     │ • 70B Core Handles Code  │     │ • Generate Day Summary   │
│ • Lock Clock Start Time  │ ──> │ • 8B Minions Modify Files│ ──> │ • Wipe Raw Chatter RAM   │
│ • Inject System Prompt   │     │ • Conversational Sync    │     │ • DB Backup to G-Drive   │
│ • Feed 5 Day Summaries   │     │ • Zero Minion Chatter    │     │ • Git Auto Push to GitHub│
└──────────────────────────┘     └──────────────────────────┘     └──────────────────────────┘

## Phase 1: The Morning Handshake Protocol

* The Trigger: The user starts the morning by logging into the terminal interface with a fresh cup of coffee and submitting a text-based Daily Brief.
* The Handshake Execution Sequence:
1. The system captures the request and logs the absolute session start time to activate a tracking clock.
   2. The database manager queries the storage graph to extract historical text summaries from the previous 5 days of development. This establishes context boundaries without overloading daily token quotas.
   3. The system bundles these summaries, today's specific user brief, and your core ecosystem operational instructions into a single System Prompt Envelope.
   4. The system injects this combined prompt directly into the active memory stack, establishing a solid baseline for Wu before development begins.

## Phase 2: Active Workspace & Token Mitigation Protocol

* The Core Brain (Llama 3.3 70B): Processes all primary conversational prompts, addresses structural questions, and manages the architecture. Every statement sent to Wu and each response line generated is written directly into the Neo4j database graph as raw chat history nodes.
* The Minion Array Workers (Llama 3.1 8B): Headless mechanical utility modules called by the system to run repetitive tasks (running text edits, scanning regex filters, or modifying local directory files directly).
* The Token Saver Rule: Minion tasks require your explicit safety confirmation before modifying files on disk. To conserve your daily Groq free-tier tokens, Minions operate silently in the background and do not save conversational chatter to the Neo4j graph database.

## Phase 3: The Evening Automated Cleanup Protocol

* The Trigger: The user ends the day by sending a final confirmation command to activate the close session protocol.
* The Automated Cleanup Sequence:
1. The backend system scans the active session's raw chat history nodes and generates a structured Day Summary text block.
   2. This summary is permanently written to the historical project log graph, and the project plan is updated.
   3. The system sweeps the database workspace, deleting the raw conversational chatter to keep graph memory clear and lightweight.
   4. The system exports an encrypted database backup file and streams it directly to your remote Google Drive folder.
   5. The system triggers local OS commands to run a sequence of git add ., git commit -m "[Automated Summary Data]" and git push origin main to backup your code repository to GitHub.

------------------------------
## 3. Verification & Guardrail Mechanisms

* Zero-Browser Testing: All API modifications and custom logic endpoints must be verified directly from the terminal command line using standard curl or localhost JSON requests. This ensures your code operates correctly without any browser file caches or layout loops interfering.
* Namespace Isolation: URL routes, path strings, and file scripts must adhere strictly to namespaced paths to prevent path tracking collisions across independent applications.

------------------------------
## Next Phase Action Plan
To begin implementing this clean blueprint, we will audit and update your core session management scripts step-by-step.
Whenever you are ready to proceed, choose our first target:

   1. Paste your start_online_session.py script so we can wire up your morning system prompt injection loop and fetch your historical summaries safely.
   2. Or paste your end_session_view.py script so we can configure your evening automated Google Drive backup and GitHub sync routine.



