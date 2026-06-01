# Aurora Forge: Human-in-the-Loop Pipeline Control Center (Reseed Sync)

## 1. Core Objective & Intent
We are running a transactional, relational automation toolchain inside the **Aurora** platform to orchestrate system file mutations for **HopeHub**. Instead of manual, error-prone file writing, the platform runs a structured Test-Driven Development (TDD) cycle. Each phase is managed via real-time browser text modifications, validated through local terminal subprocess execution loops, and sealed by manual operator visual sign-off gates. As a proof-of-concept, we are building a model-free modular page tracking loop named **`under_construction_page`**.

The master criteria for this engine are to act as a development force multiplier, enforce strict standards, adhere to change protocols, and provide immutable audit trails **without ever destabilizing or crashing the local development server context.**


## 2. Settled Architectural Decisions & Constraints
* **Directory Path Isolation Enforcement**: Root application packages (`hopehub/`) and view packages (`hopehub/views/`) must remain completely distinct target vectors. Top-level configurations (`hopehub/`) are frozen initialization contexts and must never be scanned or appended to by automated directory interception hooks to prevent premature URL loading locks.
* **Modular Views as Packages**: Both `aurora` and `hopehub` use modular directory layouts (`views/` subdirectories housing individual standalone `.py` files and an active `__init__.py` package manager constructor facade) rather than monolithic `views.py` files. All new views must be registered in the `__init__.py` file's `__all__` whitelist to prevent namespace collisions.
* **Embedded Form Layout Pattern**: Form validation structures (like `AutomatedBuildStepForm`) are embedded directly into their calling modular view files (e.g., `aurora/views/automation_dashboard.py`) to keep the codebase compact and prevent file sprawl.
* **Crispy Form Native Structure Override**: To honor the specific post destinations declared across our custom HTML files, `self.helper.form_tag = False` is explicitly set within form initializers to suppress duplicate, nested form layouts and prevent route deflection.
* **Smart Directory Interception**: The core file mutation engine (`file_mutator.py`) automatically handles package directory paths. If a path targets a folder housing an `__init__.py` module file, the mutation safely appends an explicit wildcard import context (`from .[module] import *`) into that package file dynamically, rather than treating the directory as a flat file.
* **Persistent Backup Snapshot Strategy**: Backup snapshots (`.bak` files) are strictly preserved during successful validation runs to allow for bidirectional multi-step backward sequence navigation and reliable historical rollbacks.
* **Localhost URL Alignment**: All workspace panels, control panel links, and redirect lookups use `localhost:8000` rather than raw IP interfaces.
* **Lean Dashboard Interface & Isolated Routing**: The control panel drops standard landing page back-links to enforce strict interface isolation during active code mutations. Post-finalization redirects route explicitly back to the centralized control hub (`aurora_dashboard`), which maps to `/aurora/dashboard/`.


## 3. Upgraded Debugging & State Navigation Framework
The control center contains three immediate platform engineering upgrades to prevent silent failures and streamline browser-based modifications:
1. **Live Browser Debugging**: The left code payload textarea is fully editable. If a validation check fails, the operator can tweak code strings directly in the browser and re-run the pipeline without leaving the window.
2. **1-Click Rollback Engine (`RollbackMinionStepView`)**: A safety actuator button next to the terminal console instantly wipes away experimental code mutations, cleans up accidental package declarations inside `__init__.py` files, and completely restores the file system using background `.bak` snapshots.
3. **Bidirectional Sequence Navigation (`StepBackwardNavigationView`)**: A global, persistent header button (`⏮️ Re-open Previous Step`) allows operators to manually force the database tracking state backward to overwrite or re-review completed files.


## 4. Hardened Protection Against Server Instability (Post-Mortem Fixes)
To prevent front-end text mutations and automated file rollbacks from causing fatal Python import traps (`AppRegistryNotReady: Apps aren't loaded yet.`), the system enforces the following safety invariants:

* **Non-Reload Operational Architecture**: During active workspace mutation sequences, the development server is run with the `--noreload` flag (`python manage.py runserver --noreload`). This completely freezes file system monitoring hooks in memory, allowing code modules to be written step-by-step without dropping active network sockets mid-request or throwing `ERR_EMPTY_RESPONSE` errors.
* **Safe Parsing Rollback Sequence**: When rolling back or deleting a newly created view module file, the engine must actively scan and clean up any package constructor trackers (`__init__.py`) **first**. The explicit import statement (`from .under_construction import *`) must be completely scrubbed out *before* the corresponding file content is cleared. This guarantees Django never encounters a dangling pointer that chokes its app registry boot sequence.
* **Preservation of File Targets**: If a file must be cleared during a rollback, the engine truncates or clears its content to a baseline comment (`# Module baseline cleared by Aurora Rollback Engine`) instead of deleting the file entirely from the disk, preventing path resolution crashes during live hot-reloads.


## 5. Active Seeded Pipeline Steps (PostgreSQL Layout Map)
The pipeline database contains the following four corrected steps, structurally aligned with the maximum column size limitations (`max_length=150` on titles) and explicit enum choices declared within the active `aurora/models.py` state table:

1. **Step 1: SETUP_TEST**
   * *Stage Registry Token:* `SETUP_TEST`
   * *Minion Worker:* Test-Architect Minion
   * *Target File Path:* `hopehub/tests/test_views.py`
   * *Code Payload:* Injects the `TestUnderConstructionView` class checking for status code `200` on the namespaced `/hopehub/under-construction/` routing.
   * *Verification Command:* `python manage.py test hopehub.tests.test_views`
   * *Expected Exit Code:* `1` (TDD Enforced Failure Gate)

2. **Step 2: BUILD_HTML**
   * *Stage Registry Token:* `BUILD_HTML`
   * *Minion Worker:* Frontend Forge Minion
   * *Target File Path:* `hopehub/templates/hopehub/construction.html`
   * *Code Payload:* Generates an `aurora_base.html`-compatible container panel banner stating `"FEATURE UNDER CONSTRUCTION"`.
   * *Verification Command:* `test -f hopehub/templates/hopehub/construction.html`
   * *Expected Exit Code:* `0`

3. **Step 3: BUILD_VIEW**
   * *Stage Registry Token:* `BUILD_VIEW`
   * *Minion Worker:* Logic-Engine Minion
   * *Target File Path:* `hopehub/views/under_construction.py` (Enforced views subdirectory partition target)
   * *Code Payload:* Writes a clean `UnderConstructionView(TemplateView)` subclass targeting the page from Step 2.
   * *Verification Command:* `python manage.py check` (Enforces Django Framework Lifecycle initialization)
   * *Expected Exit Code:* `0`

4. **Step 4: BUILD_ROUTER**
   * *Stage Registry Token:* `BUILD_ROUTER`
   * *Minion Worker:* Network Routing Minion
   * *Target File Path:* `hopehub/urls.py`
   * *Code Payload:* Registers `path('under-construction/', views.UnderConstructionView.as_view(), name='under_construction'),`
   * *Anchor Signature:* `urlpatterns = [`
   * *Verification Command:* `python manage.py test hopehub.tests.test_views`
   * *Expected Exit Code:* `0` (TDD Turns Solid Green)


## 6. Operational Recovery & Disaster Rollback Plan
If you need to instantly clean up or reset the environment back to baseline parameters, execute this teardown sequence:

```bash
# 1. Clear PostgreSQL database records cleanly using Django's connection layer
python manage.py shell -c "from aurora.models import AutomatedBuildStep; AutomatedBuildStep.objects.filter(feature_name='under_construction_page').delete(); print('✅ PostgreSQL database cleared!')"

# 2. Delete generated views and template file modules off your local disk space
rm -f hopehub/views/under_construction.py
rm -f hopehub/templates/hopehub/construction.html

# 3. Pull your clean committed versions from Git HEAD and clear bytecode cache layers
git checkout HEAD -- hopehub/__init__.py hopehub/views/__init__.py hopehub/urls.py
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# 4. Re-run your custom management seeder script to populate clean tracking records
python manage.py seed_pipeline

# 5. Launch the stable, frozen server loop to eliminate socket dropouts completely
python manage.py runserver 127.0.0.1:8000 --noreload
```

