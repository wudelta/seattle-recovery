#!/usr/bin/env bash
# filepath: start_session.sh
set -euo pipefail

echo "======================================================================"
echo "🌅 AURORA FORGE // INITIALIZING ACTIVE DEVELOPMENT WORKSPACE"
echo "======================================================================"

# 1. Activate localized python virtual environment
if [ -f ".venv/bin/activate" ]; then
    echo "-> Activating local virtual environment..."
    source .venv/bin/activate
else
    echo "❌ ERROR: Virtual environment (.venv) not found!"
    exit 1
fi

# 2. Hardened Security Invariant Check
echo "-> Verifying HIPAA & 42 CFR Part 2 environment registers..."
if [ -z "${HOPEHUB_FIELD_ENCRYPTION_KEY:-}" ]; then
    # Check if a local .env file can supply it before crashing
    if [ -f ".env" ] && grep -q "HOPEHUB_FIELD_ENCRYPTION_KEY" .env; then
        echo "   [OK] Key located in local .env configuration."
    else
        echo "======================================================================"
        echo "🚨 CRITICAL ERROR: HOPEHUB_FIELD_ENCRYPTION_KEY IS NOT CONFIGURED!"
        echo "   Please ensure your local .env file exists and holds your key."
        echo "======================================================================"
        exit 1
    fi
fi

# 3. Clear out any lingering bytecode compilation cache artifacts
echo "-> Scrubbing Python runtime bytecode registers..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete || true

# 4. Ingest database-driven documentation, rules, and states
if [ -f "workspace_db_snapshot.json" ]; then
    echo "-> Loading master database snapshot registry into PostgreSQL..."
    python manage.py loaddata workspace_db_snapshot.json
else
    echo "⚠️  WARNING: 'workspace_db_snapshot.json' not found. Skipping data load."
fi

# 5. Run framework configuration lifecycle verification scan
echo "-> Executing system configuration pre-flight sanity checks..."
python manage.py check

echo -e "\n======================================================================"
echo "🚀 WORKSPACE PRISTINE // SERVER INITIALIZING"
echo "   1. Run 'python manage.py ai_sync' to copy your AI Reseed Pack."
echo "   2. Keep this window open for your stable, frozen server loop."
echo "======================================================================"

# Launch server loop with the strict non-reload flag to stop app registry traps
python manage.py runserver localhost:8000 --noreload
