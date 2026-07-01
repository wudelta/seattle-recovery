# Monorepo State Log & Next-Action Roadmap

## 🎯 Current System Architecture (What is Done)
The combined monolith has been successfully decoupled into a dual-container architecture running natively on a single Postgres volume. Both apps share a single code tree but run in absolute logical isolation.

### 1. Active Infrastructure Matrix
* **Gateway Entry Link**: Nginx (`seattle_web`) is fully operational on port `3000`.
* **Track A (Aurora Builder)**: Daphne container live on port `8000`, mapped strictly to `aurora_db`.
* **Track B (HopeHub Production)**: Daphne container live on port `8001`, mapped strictly to `hopehub_db`.
* **Shared Data Store**: PostgreSQL live on port `5432` with fully distinct logical targets.

### 2. Verified Data Integrity Milestones
* **UUID Overhaul Complete**: Legacy integer IDs (`id = 1`) have been purged across both databases.
* **Master User Link**: All business records are populated and foreign-key bound onto your permanent security token: `d72473bc-b25b-45d8-aaad-aed1a5416dcd`.
* **Dynamic App Selectors**: `core_logic/settings.py` and `core_logic/urls.py` automatically filter app manifests and routing trees based on the container's active environment variables.
* **Developer Shell Shortcuts**: Your local `~/.bashrc` aliases have been fully updated to isolate logs (`dlog-aurora`, `dlog-hopehub`) and trigger clean snapshot runs (`dbackup`).

---

## 🛠️ Tomorrow's Work Plan (What is Left to Do)

When you boot up the next session, we skip all database configuration and initialization tasks. We have exactly two objectives left to make this a production-hardened environment:

### Task 1: Complete Test Suite Rewrite
Our previous test suite is broken because it expects a single app with sequential IDs. We need to write the new tests into three highly targeted tracks:
* `users/tests.py`: Validate string UUID enforcement on user generation.
* `aurora/tests.py`: Validate component profiles and AI minion configurations.
* `hopehub/tests.py`: Validate Fernet cryptographic fields and clinical record isolation boundaries.

### Task 2: Fix Remaining Edge Broken Things
* Verify the Neo4j graph cluster handshakes cleanly with the newly decoupled containers at boot.
* Audit Nginx's static file delivery if asset paths shift during multi-container compilation loops.
