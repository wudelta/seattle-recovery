# ======================================================================
# FILE: aurora/workspace/workspace_reconciler.py (PATCH 1 OF 4)
# START: RECONCILIATION_TYPES_AND_INITIALIZATION
# ======================================================================
"""Read-only comparison of repository files against ComponentRegistry."""

import hashlib
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings

from aurora.models import ComponentRegistry
from aurora.workspace.component_policy import (
    CLASSIFICATION_EXCLUDE,
    CLASSIFICATION_KEEP,
    CLASSIFICATION_REGISTER,
    CLASSIFICATION_REVIEW,
    CLASSIFICATION_STAGE,
    CLASSIFICATION_UPDATE,
)


def calculate_source_hash(path: Path) -> str:
    """
    Return the SHA-256 digest of a repository file's exact contents.

    Hashing is deterministic and independent of AI analysis.
    """
    digest = hashlib.sha256()

    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)

    return digest.hexdigest()


@dataclass(frozen=True)
class ReconciliationItem:
    """One deterministic workspace reconciliation result."""

    path: str
    classification: str
    reason: str
    name: str | None = None
    persona: str | None = None
    source_hash: str | None = None
    registry_id: str | None = None


class WorkspaceReconciler:
    """
    Compare application-owned repository files with ComponentRegistry.

    This service performs no repository, PostgreSQL, Neo4j, or AI mutations.
    """

    def __init__(self, repository_root: str | Path | None = None):
        configured_root = repository_root or settings.BASE_DIR
        self.repository_root = Path(configured_root).resolve()

    def load_registry_snapshot(self) -> dict[str, ComponentRegistry]:
        """
        Load registry rows keyed by normalized repository-relative path.

        The queryset is evaluated once to avoid repeated database queries
        during workspace traversal.
        """
        snapshot: dict[str, ComponentRegistry] = {}

        for component in ComponentRegistry.objects.all():
            normalized_path = component.file_path.strip().replace("\\", "/")
            snapshot[normalized_path] = component

        return snapshot
# ======================================================================
# END: RECONCILIATION_TYPES_AND_INITIALIZATION (PATCH 1 OF 4)
# ======================================================================

# ======================================================================
# FILE: aurora/workspace/workspace_reconciler.py (PATCH 2 OF 4)
# START: READ_ONLY_REPOSITORY_DISCOVERY
# ======================================================================
    def discover_workspace_files(self) -> dict[str, dict[str, str | None]]:
        """
        Discover repository files under allowed roots and explicit root files.

        Excluded directories are pruned before traversal. Eligible files receive
        an exact SHA-256 content hash after path policy has approved inspection.
        """
        import ast
        import os

        from aurora.workspace.component_policy import (
            ALLOWED_ROOT_FILES,
            ALLOWED_ROOTS,
            CLASSIFICATION_EXCLUDE,
            CLASSIFICATION_REGISTER,
            EXCLUDED_DIRECTORY_NAMES,
            classify_component_path,
        )

        discovered: dict[str, dict[str, str | None]] = {}

        def classify_candidate(candidate_path: Path) -> None:
            try:
                relative_path = candidate_path.relative_to(
                    self.repository_root
                ).as_posix()
                classification = classify_component_path(relative_path)
            except (OSError, ValueError):
                return

            if classification["classification"] == CLASSIFICATION_EXCLUDE:
                discovered[relative_path] = classification
                return

            if candidate_path.name == "__init__.py":
                try:
                    source = candidate_path.read_text(encoding="utf-8")
                    module = ast.parse(source, filename=relative_path)
                    meaningful_nodes = list(module.body)

                    if (
                        meaningful_nodes
                        and isinstance(meaningful_nodes[0], ast.Expr)
                        and isinstance(meaningful_nodes[0].value, ast.Constant)
                        and isinstance(meaningful_nodes[0].value.value, str)
                    ):
                        meaningful_nodes = meaningful_nodes[1:]

                    if meaningful_nodes:
                        classification["classification"] = (
                            CLASSIFICATION_REGISTER
                        )
                        classification["reason"] = (
                            "package_initializer_contains_behavior"
                        )
                    else:
                        classification["classification"] = (
                            CLASSIFICATION_EXCLUDE
                        )
                        classification["reason"] = "empty_package_marker"
                except (OSError, SyntaxError, UnicodeDecodeError):
                    classification["reason"] = (
                        "package_initializer_requires_review"
                    )

            if classification["classification"] != CLASSIFICATION_EXCLUDE:
                try:
                    classification["source_hash"] = calculate_source_hash(
                        candidate_path
                    )
                except OSError:
                    classification["source_hash"] = None
                    classification["reason"] = "source_hash_unavailable"

            discovered[relative_path] = classification

        for file_name in sorted(ALLOWED_ROOT_FILES):
            candidate_path = self.repository_root / file_name
            if candidate_path.is_file():
                classify_candidate(candidate_path)

        for root_name in sorted(ALLOWED_ROOTS):
            root_path = self.repository_root / root_name

            if not root_path.exists() or not root_path.is_dir():
                continue

            for current_root, directory_names, file_names in os.walk(root_path):
                directory_names[:] = sorted(
                    directory_name
                    for directory_name in directory_names
                    if directory_name.lower() not in EXCLUDED_DIRECTORY_NAMES
                )

                current_path = Path(current_root)

                for file_name in sorted(file_names):
                    classify_candidate(current_path / file_name)

        return discovered
# ======================================================================
# END: READ_ONLY_REPOSITORY_DISCOVERY (PATCH 2 OF 4)
# ======================================================================

# ======================================================================
# FILE: aurora/workspace/workspace_reconciler.py (PATCH 3 OF 4)
# START: REGISTRY_COMPARISON_ENGINE
# ======================================================================
    def reconcile(self) -> list[ReconciliationItem]:
        """Compare discovered paths with the current registry snapshot."""
        from pathlib import PurePosixPath

        from aurora.workspace.component_policy import classify_component_path

        discovered = self.discover_workspace_files()
        registry = self.load_registry_snapshot()
        results: list[ReconciliationItem] = []

        authoritative_persona_files = {
            "manage.py",
            "asgi.py",
            "wsgi.py",
            "settings.py",
        }

        for path in sorted(discovered):
            policy_result = discovered[path]
            existing = registry.pop(path, None)
            policy_classification = policy_result["classification"]
            observed_hash = policy_result.get("source_hash")

            if policy_classification == CLASSIFICATION_EXCLUDE:
                results.append(
                    ReconciliationItem(
                        path=path,
                        classification=CLASSIFICATION_EXCLUDE,
                        reason=str(policy_result["reason"]),
                        registry_id=str(existing.id) if existing else None,
                    )
                )
                continue

            if policy_classification == CLASSIFICATION_REVIEW:
                results.append(
                    ReconciliationItem(
                        path=path,
                        classification=CLASSIFICATION_REVIEW,
                        reason=str(policy_result["reason"]),
                        name=existing.name if existing else policy_result["name"],
                        persona=(
                            existing.persona
                            if existing
                            else policy_result["persona"]
                        ),
                        source_hash=observed_hash,
                        registry_id=str(existing.id) if existing else None,
                    )
                )
                continue

            if existing is None:
                results.append(
                    ReconciliationItem(
                        path=path,
                        classification=CLASSIFICATION_REGISTER,
                        reason="eligible_file_missing_from_registry",
                        name=policy_result["name"],
                        persona=policy_result["persona"],
                        source_hash=observed_hash,
                    )
                )
                continue

            stored_path = existing.file_path.strip().replace("\\", "/")
            filename = PurePosixPath(path).name.lower()
            persona_is_authoritative = (
                filename in authoritative_persona_files
            )
            persona_changed = (
                persona_is_authoritative
                and existing.persona != policy_result["persona"]
            )
            source_changed = (
                observed_hash is not None
                and existing.source_hash != observed_hash
            )

            metadata_changed = any(
                (
                    stored_path != path,
                    existing.status != "ACTIVE",
                    persona_changed,
                    source_changed,
                )
            )

            if source_changed:
                reason = (
                    "source_hash_missing"
                    if not existing.source_hash
                    else "source_content_changed"
                )
            elif metadata_changed:
                reason = "managed_registry_state_is_stale"
            else:
                reason = "registry_record_matches_workspace"

            results.append(
                ReconciliationItem(
                    path=path,
                    classification=(
                        CLASSIFICATION_UPDATE
                        if metadata_changed
                        else CLASSIFICATION_KEEP
                    ),
                    reason=reason,
                    name=existing.name,
                    persona=(
                        policy_result["persona"]
                        if persona_changed
                        else existing.persona
                    ),
                    source_hash=observed_hash,
                    registry_id=str(existing.id),
                )
            )

        for path, existing in sorted(registry.items()):
            try:
                policy_result = classify_component_path(path)
            except ValueError:
                policy_result = {
                    "classification": CLASSIFICATION_EXCLUDE,
                    "reason": "invalid_registry_path",
                }

            is_excluded = (
                policy_result["classification"] == CLASSIFICATION_EXCLUDE
            )

            results.append(
                ReconciliationItem(
                    path=path,
                    classification=(
                        CLASSIFICATION_EXCLUDE
                        if is_excluded
                        else CLASSIFICATION_STAGE
                    ),
                    reason=(
                        str(policy_result["reason"])
                        if is_excluded
                        else "registered_file_missing_from_workspace"
                    ),
                    name=existing.name,
                    persona=existing.persona,
                    source_hash=existing.source_hash or None,
                    registry_id=str(existing.id),
                )
            )

        return results
# ======================================================================
# END: REGISTRY_COMPARISON_ENGINE (PATCH 3 OF 4)
# ======================================================================

# ======================================================================
# FILE: aurora/workspace/workspace_reconciler.py (PATCH 4 OF 4)
# START: RECONCILIATION_REPORT_GENERATION
# ======================================================================
    def build_report(self) -> dict[str, object]:
        """Return deterministic categorized results and summary counts."""
        results = self.reconcile()
        classifications = (
            CLASSIFICATION_KEEP,
            CLASSIFICATION_UPDATE,
            CLASSIFICATION_REGISTER,
            CLASSIFICATION_STAGE,
            CLASSIFICATION_EXCLUDE,
            CLASSIFICATION_REVIEW,
        )

        categorized: dict[str, list[ReconciliationItem]] = {
            classification: []
            for classification in classifications
        }

        for item in results:
            categorized[item.classification].append(item)

        counts = {
            classification: len(categorized[classification])
            for classification in classifications
        }
        counts["TOTAL"] = len(results)

        return {
            "repository_root": str(self.repository_root),
            "dry_run": True,
            "counts": counts,
            "items": categorized,
        }
# ======================================================================
# END: RECONCILIATION_REPORT_GENERATION (PATCH 4 OF 4)
# ======================================================================