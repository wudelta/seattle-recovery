# ======================================================================
# FILE: aurora/minions/patch_parser.py (PATCH 1 OF 1)
# START: STRUCTURED_WU_PATCH_RESPONSE_PARSER
# ======================================================================
import re
from dataclasses import dataclass
from pathlib import Path


_PATCH_PATTERN = re.compile(
    r"""
    \[PATCH_START:\s*(?P<path>[^\]\r\n]+?)\s*\]
    (?P<content>.*?)
    \[PATCH_END\]
    """,
    re.IGNORECASE | re.DOTALL | re.VERBOSE,
)

_PATCH_START_PATTERN = re.compile(
    r"\[PATCH_START:\s*(?P<path>[^\]\r\n]+?)\s*\]",
    re.IGNORECASE,
)

_PATCH_END_PATTERN = re.compile(
    r"\[PATCH_END\]",
    re.IGNORECASE,
)

_LANGUAGE_BY_SUFFIX = {
    ".css": "css",
    ".html": "html",
    ".js": "javascript",
    ".json": "json",
    ".md": "markdown",
    ".py": "python",
    ".sql": "sql",
    ".yaml": "yaml",
    ".yml": "yaml",
}


class PatchParseError(ValueError):
    """Raised when a Wu patch response is malformed or unsafe."""


@dataclass(frozen=True)
class ParsedPatch:
    file_path: str
    original_content: str
    proposed_content: str
    language: str
    patch_complete: bool

    def as_payload(self) -> dict:
        return {
            "file_path": self.file_path,
            "original_content": self.original_content,
            "proposed_content": self.proposed_content,
            "language": self.language,
            "patch_complete": self.patch_complete,
        }


def _normalize_path(file_path: str) -> str:
    normalized_path = file_path.strip().replace("\\", "/")
    path = Path(normalized_path)

    if path.is_absolute():
        raise PatchParseError(
            "Patch responses may not target absolute file paths."
        )

    if ".." in path.parts:
        raise PatchParseError(
            "Patch response path traversal is not permitted."
        )

    normalized = path.as_posix()

    if normalized in {"", "."}:
        raise PatchParseError(
            "Patch response did not include a valid file path."
        )

    return normalized


def _detect_language(file_path: str) -> str:
    return _LANGUAGE_BY_SUFFIX.get(
        Path(file_path).suffix.lower(),
        "plaintext",
    )


def response_contains_patch_markers(response_text: str) -> bool:
    """
    Return whether a Wu response contains any structured patch marker.

    Ordinary conversational, advisory, and recommendation responses
    return False and must not be treated as failed patch responses.
    """
    if not isinstance(response_text, str) or not response_text:
        return False

    return bool(
        _PATCH_START_PATTERN.search(response_text)
        or _PATCH_END_PATTERN.search(response_text)
    )


def _extract_single_patch(response_text: str) -> re.Match:
    complete_matches = list(_PATCH_PATTERN.finditer(response_text))
    start_count = len(_PATCH_START_PATTERN.findall(response_text))
    end_count = len(_PATCH_END_PATTERN.findall(response_text))

    if start_count == 0 and end_count == 0:
        raise PatchParseError(
            "The response does not contain a patch block."
        )

    if start_count != end_count:
        raise PatchParseError(
            "The patch response is incomplete or truncated."
        )

    if len(complete_matches) != 1:
        raise PatchParseError(
            "Exactly one complete patch block is required."
        )

    return complete_matches[0]


def parse_patch_response(
    response_text: str,
    expected_file_path: str,
    original_content: str,
) -> ParsedPatch:
    """
    Parse one complete Wu patch block and validate its target path.

    The returned patch contains review data only. This function does not
    create transactions, mutate files, or invoke any provider or UI code.
    """
    if not isinstance(response_text, str) or not response_text.strip():
        raise PatchParseError(
            "The response text is empty."
        )

    expected_path = _normalize_path(expected_file_path)
    patch_match = _extract_single_patch(response_text)
    returned_path = _normalize_path(
        patch_match.group("path")
    )

    if returned_path != expected_path:
        raise PatchParseError(
            "The returned patch path does not match the hydrated source file."
        )

    proposed_content = patch_match.group("content")

    if proposed_content.startswith("\r\n"):
        proposed_content = proposed_content[2:]
    elif proposed_content.startswith("\n"):
        proposed_content = proposed_content[1:]

    if proposed_content.endswith("\r\n"):
        proposed_content = proposed_content[:-2]
    elif proposed_content.endswith("\n"):
        proposed_content = proposed_content[:-1]

    return ParsedPatch(
        file_path=expected_path,
        original_content=original_content,
        proposed_content=proposed_content,
        language=_detect_language(expected_path),
        patch_complete=True,
    )
# ======================================================================
# END: STRUCTURED_WU_PATCH_RESPONSE_PARSER (PATCH 1 OF 1)
# ======================================================================