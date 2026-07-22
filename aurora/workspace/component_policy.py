# ======================================================================
# FILE: aurora/utils/component_policy.py (PATCH 1 OF 3)
# START: COMPONENT_POLICY_CONSTANTS
# ======================================================================
"""Deterministic policy for classifying repository-relative component paths."""

from pathlib import PurePosixPath


ALLOWED_ROOTS = frozenset(
    {
        "aurora",
        "hopehub",
        "users",
        "core_logic",
        "docs",
    }
)

ALLOWED_ROOT_FILES = frozenset(
    {
        "manage.py",
    }
)

EXCLUDED_DIRECTORY_NAMES = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".venv",
        "__pycache__",
        "build",
        "credentials",
        "dist",
        "htmlcov",
        "logs",
        "media",
        "migrations",
        "monaco",
        "node_modules",
        "secrets",
        "site-packages",
        "staging",
        "staticfiles",
        "tests",
        "vendor",
        "vendors",
        "venv",
    }
)

EXCLUDED_FILE_NAMES = frozenset(
    {
        ".env",
        ".env.local",
        ".env.production",
        ".env.staging",
    }
)

EXCLUDED_FILE_SUFFIXES = (
    ".log",
    ".map",
    ".min.css",
    ".min.js",
    ".pyc",
    ".sqlite",
    ".sqlite3",
)

SUPPORTED_FILE_SUFFIXES = frozenset(
    {
        ".css",
        ".html",
        ".ini",
        ".js",
        ".json",
        ".md",
        ".py",
        ".txt",
        ".yaml",
        ".yml",
    }
)

PERSONA_BY_SUFFIX = {
    ".css": "UI_STYLE",
    ".html": "UI_LAYOUT",
    ".ini": "CONFIGURATION",
    ".js": "UI_LOGIC",
    ".json": "CONFIGURATION",
    ".md": "DOCUMENTATION",
    ".py": "COMPILER_MODULE",
    ".txt": "DOCUMENTATION",
    ".yaml": "CONFIGURATION",
    ".yml": "CONFIGURATION",
}

CLASSIFICATION_KEEP = "KEEP"
CLASSIFICATION_UPDATE = "UPDATE"
CLASSIFICATION_REGISTER = "REGISTER"
CLASSIFICATION_STAGE = "STAGE"
CLASSIFICATION_EXCLUDE = "EXCLUDE"
CLASSIFICATION_REVIEW = "REVIEW"


def _path_parts(path: str) -> tuple[str, ...]:
    """Return normalized POSIX path segments for internal policy checks."""
    return PurePosixPath(path.replace("\\", "/")).parts
# ======================================================================
# END: COMPONENT_POLICY_CONSTANTS (PATCH 1 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/utils/component_policy.py (PATCH 2 OF 3)
# START: PATH_NORMALIZATION_AND_EXCLUSION_POLICY
# ======================================================================
def normalize_repository_path(path: str) -> str:
    """
    Normalize a candidate into a safe repository-relative POSIX path.

    Raises ValueError when the path is empty, absolute, or attempts to
    traverse outside the repository boundary.
    """
    if not isinstance(path, str) or not path.strip():
        raise ValueError("Repository path must be a non-empty string.")

    normalized = path.strip().replace("\\", "/")
    candidate = PurePosixPath(normalized)

    if candidate.is_absolute():
        raise ValueError(f"Absolute repository paths are not permitted: {path}")

    parts = candidate.parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"Unsafe repository-relative path: {path}")

    return candidate.as_posix()


def has_allowed_root(path: str) -> bool:
    """Return whether the path is application-owned or explicitly allowed."""
    normalized = normalize_repository_path(path)
    parts = _path_parts(normalized)

    if len(parts) == 1:
        return normalized in ALLOWED_ROOT_FILES

    return parts[0] in ALLOWED_ROOTS


def has_excluded_directory(path: str) -> bool:
    """Return whether any path segment is prohibited by repository policy."""
    normalized = normalize_repository_path(path)
    normalized_parts = tuple(part.lower() for part in _path_parts(normalized))
    return any(part in EXCLUDED_DIRECTORY_NAMES for part in normalized_parts)


def has_excluded_file_pattern(path: str) -> bool:
    """Return whether the filename represents generated or prohibited content."""
    normalized = normalize_repository_path(path)
    filename = PurePosixPath(normalized).name.lower()

    if filename in EXCLUDED_FILE_NAMES:
        return True

    if filename.startswith("."):
        return True

    return filename.endswith(EXCLUDED_FILE_SUFFIXES)


def is_supported_file_type(path: str) -> bool:
    """Return whether the path uses a component type managed by the registry."""
    normalized = normalize_repository_path(path)
    return PurePosixPath(normalized).suffix.lower() in SUPPORTED_FILE_SUFFIXES


def exclusion_reason(path: str) -> str | None:
    """Return the deterministic exclusion reason, or None when not excluded."""
    normalized = normalize_repository_path(path)

    if not has_allowed_root(normalized):
        return "outside_allowed_roots"

    if has_excluded_directory(normalized):
        return "excluded_directory"

    if has_excluded_file_pattern(normalized):
        return "excluded_file_pattern"

    if not is_supported_file_type(normalized):
        return "unsupported_file_type"

    return None
# ======================================================================
# END: PATH_NORMALIZATION_AND_EXCLUSION_POLICY (PATCH 2 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/utils/component_policy.py (PATCH 3 OF 3)
# START: COMPONENT_CLASSIFICATION_AND_PERSONA_INFERENCE
# ======================================================================
def infer_component_persona(path: str) -> str | None:
    """Infer the ComponentRegistry persona from architectural responsibility."""
    normalized = normalize_repository_path(path)
    candidate = PurePosixPath(normalized)
    filename = candidate.name.lower()
    suffix = candidate.suffix.lower()

    if suffix == ".py" and filename in {
        "manage.py",
        "asgi.py",
        "wsgi.py",
    }:
        return "ENTRY_POINT"

    if suffix == ".py" and filename == "settings.py":
        return "CONFIGURATION"

    return PERSONA_BY_SUFFIX.get(suffix)


def infer_component_name(path: str) -> str:
    """Create a concise deterministic registry name from the repository path."""
    normalized = normalize_repository_path(path)
    candidate = PurePosixPath(normalized)

    if candidate.name == "__init__.py":
        return candidate.parent.name

    return candidate.stem


def classify_component_path(path: str) -> dict[str, str | None]:
    """
    Classify one repository-relative path without opening or modifying it.

    REGISTER identifies deterministic business-relevant candidates.
    REVIEW identifies supported but uncertain files requiring human judgment.
    EXCLUDE identifies paths prohibited by repository policy.
    """
    normalized = normalize_repository_path(path)
    reason = exclusion_reason(normalized)

    if reason:
        return {
            "path": normalized,
            "classification": CLASSIFICATION_EXCLUDE,
            "reason": reason,
            "name": None,
            "persona": None,
        }

    candidate = PurePosixPath(normalized)
    suffix = candidate.suffix.lower()
    persona = infer_component_persona(normalized)

    if candidate.name == "__init__.py":
        classification = CLASSIFICATION_REVIEW
        reason = "package_marker_requires_content_inspection"
    elif suffix in {".ini", ".json", ".txt"}:
        classification = CLASSIFICATION_REVIEW
        reason = "uncertain_business_relevance"
    else:
        classification = CLASSIFICATION_REGISTER
        reason = "eligible_application_component"

    return {
        "path": normalized,
        "classification": classification,
        "reason": reason,
        "name": infer_component_name(normalized),
        "persona": persona,
    }
# ======================================================================
# END: COMPONENT_CLASSIFICATION_AND_PERSONA_INFERENCE (PATCH 3 OF 3)
# ======================================================================