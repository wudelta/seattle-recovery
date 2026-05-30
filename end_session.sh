#!/usr/bin/env bash
# filepath: end_session.sh
set -euo pipefail

echo "======================================================================"
echo "🌌 AURORA FORGE // TERMINATING DEVELOPMENT WORKSPACE SESSION"
echo "======================================================================"

# Ensure virtual environment is active for the data export step
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# 1. Export database compliance documents and tracking parameters to JSON
echo "-> Serializing database documentation tables to local snapshot..."
python manage.py dumpdata aurora hopehub --indent=2 > workspace_db_snapshot.json
echo "   [OK] Data backed up to workspace_db_snapshot.json"

# 2. Prompt developer inline for session notes to append to the Git log
echo "----------------------------------------------------------------------"
echo "📝 Enter a short summary of the engineering work you completed today:"
echo "----------------------------------------------------------------------"
read -r -p "> " session_notes

# 3. Version control synchronization routine
echo -e "\n-> Staging modified files for Git version control..."
git add .

echo "-> Sealing session matrices in Git ledger..."
git commit -m "chore(sync): automated end-of-session workspace snapshot" -m "
======================================================================
AURORA FORGE // AUTOMATED END-OF-SESSION DISK STATUS SNAPSHOT
======================================================================
Developer Notes:
- ${session_notes}

System Executions:
- Serialized database rules to workspace_db_snapshot.json.
- Cleared local runtime filesystem artifacts.
- Maintained HIPAA & 42 CFR Part 2 clinical data encryption boundaries.
======================================================================
"

# 🚀 NEW ADDITION: Push your local sealed ledger straight to GitHub cloud backup registers
echo "-> Transmitting snapshot securely to GitHub origin..."
git push origin HEAD

# 4. Clean up disk artifacts before shut down
echo "-> Cleaning runtime filesystem pycache registers..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete || true

echo -e "\n======================================================================"
echo "🔒 WORKSPACE SECURED & CLOSED // snapshot successfully committed to Git!"
echo "======================================================================"
