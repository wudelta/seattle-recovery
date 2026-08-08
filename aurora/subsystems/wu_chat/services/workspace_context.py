# ======================================================================
# FILE: aurora/subsystems/wu_chat/services/workspace_context.py
# START: SAFE_WORKSPACE_CONTEXT_RESOLUTION
# ======================================================================
import re
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings


_READ_FILE_PATTERN = re.compile(
    r"\[READ_FILE:\s*(?P<path>[^\]\r\n]+?)\s*\]",
    re.IGNORECASE,
)

_REPOSITORY_PATH_PATTERN = re.compile(
    r"""
    (?<![\w./-])
    (?P<path>
        (?:[A-Za-z0-9_.-]+/)
        [A-Za-z0-9_./-]+
        \.[A-Za-z0-9]+
    )
    """,
    re.VERBOSE,
)


class WorkspaceContextError(ValueError):
    """Raised when repository context cannot be resolved safely."""


@dataclass(frozen=True)
class WorkspaceContext:
    file_path: str
    absolute_path: Path
    original_content: str
    hydrated_prompt: str


def _extract_requested_path(instruction: str) -> str | None:
    marker_match = _READ_FILE_PATTERN.search(instruction)

    if marker_match:
        return marker_match.group("path").strip()

    path_match = _REPOSITORY_PATH_PATTERN.search(instruction)

    if path_match:
        return path_match.group("path").strip()

    return None


def _resolve_repository_path(requested_path: str) -> tuple[str, Path]:
    repository_root = Path(settings.BASE_DIR).resolve()
    normalized_path = requested_path.strip().replace("\\", "/")
    relative_path = Path(normalized_path)

    if relative_path.is_absolute():
        raise WorkspaceContextError(
            "Absolute file paths are not permitted."
        )

    resolved_path = (repository_root / relative_path).resolve()

    try:
        repository_path = resolved_path.relative_to(repository_root)
    except ValueError as exc:
        raise WorkspaceContextError(
            "The requested file path escapes the repository root."
        ) from exc

    if not resolved_path.exists():
        raise WorkspaceContextError(
            f"Repository file does not exist: {repository_path.as_posix()}"
        )

    if not resolved_path.is_file():
        raise WorkspaceContextError(
            f"Repository path is not a file: {repository_path.as_posix()}"
        )

    return repository_path.as_posix(), resolved_path


def _read_source_file(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise WorkspaceContextError(
            "The requested file is not valid UTF-8 text."
        ) from exc
    except OSError as exc:
        raise WorkspaceContextError(
            "The requested file could not be read."
        ) from exc


def _build_hydrated_prompt(
    instruction: str,
    file_path: str,
    original_content: str,
) -> str:
    return (
        f"{instruction.strip()}\n\n"
        "[AURORA_WORKSPACE_CONTEXT]\n"
        f"FILE_PATH: {file_path}\n"
        "[CURRENT_FILE_START]\n"
        f"{original_content}"
        f"{'' if original_content.endswith(chr(10)) else chr(10)}"
        "[CURRENT_FILE_END]\n"
        "[/AURORA_WORKSPACE_CONTEXT]\n\n"
        "Return any proposed replacement inside exactly one matching block:\n"
        f"[PATCH_START: {file_path}]\n"
        "<proposed replacement content>\n"
        "[PATCH_END]"
    )


def resolve_workspace_context(
    instruction: str,
) -> WorkspaceContext | None:
    """
    Resolve and hydrate repository context referenced by a user instruction.

    Returns None when the instruction contains no recognizable repository
    file path. Raises WorkspaceContextError when a path is present but unsafe
    or unreadable.
    """
    requested_path = _extract_requested_path(instruction)

    if requested_path is None:
        return None

    file_path, absolute_path = _resolve_repository_path(requested_path)
    original_content = _read_source_file(absolute_path)
    hydrated_prompt = _build_hydrated_prompt(
        instruction=instruction,
        file_path=file_path,
        original_content=original_content,
    )

    return WorkspaceContext(
        file_path=file_path,
        absolute_path=absolute_path,
        original_content=original_content,
        hydrated_prompt=hydrated_prompt,
    )
# ======================================================================
# END: SAFE_WORKSPACE_CONTEXT_RESOLUTION
# ======================================================================