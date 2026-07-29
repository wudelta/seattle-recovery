# ======================================================================
# FILE: aurora/subsystems/planning/io/loader.py
# START: PLANNING_DOCUMENT_LOADER
# ======================================================================
from pathlib import Path
from typing import Any

import yaml

from aurora.subsystems.planning.io.exceptions import PlanningIOError


class PlanningDocumentLoadError(PlanningIOError):
    """Raised when a planning document cannot be loaded from disk."""


def load_planning_document(path: Path | str) -> Any:
    """Load one YAML planning document from a filesystem path."""

    document_path = Path(path)

    if not document_path.exists():
        raise PlanningDocumentLoadError(
            f"Planning document does not exist: {document_path}"
        )

    if not document_path.is_file():
        raise PlanningDocumentLoadError(
            f"Planning document is not a file: {document_path}"
        )

    try:
        raw_document = document_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PlanningDocumentLoadError(
            f"Unable to read planning document: {document_path}"
        ) from exc

    try:
        document = yaml.safe_load(raw_document)
    except yaml.YAMLError as exc:
        raise PlanningDocumentLoadError(
            f"Planning document contains invalid YAML: {document_path}"
        ) from exc

    if document is None:
        raise PlanningDocumentLoadError(
            f"Planning document is empty: {document_path}"
        )

    return document
# ======================================================================
# END: PLANNING_DOCUMENT_LOADER
# ======================================================================