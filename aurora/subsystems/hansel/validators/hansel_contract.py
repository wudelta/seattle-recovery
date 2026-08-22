# ======================================================================
# FILE: aurora/subsystems/hansel/validators/hansel_contract.py
# START: HANSEL_CONTRACT_VALIDATOR
# ======================================================================

from dataclasses import dataclass
from pathlib import Path
import re


VALID_KNOWLEDGE_STATES = frozenset(
    {
        "VERIFIED",
        "PLANNED",
        "UNKNOWN",
        "DEFERRED",
        "DEPRECATED",
    }
)

PATH_PATTERN = re.compile(
    r"(?:aurora|docs)/[A-Za-z0-9_./-]+"
)

KNOWLEDGE_STATE_PATTERN = re.compile(
    r"Knowledge State:\s*([A-Z_]+)",
    re.IGNORECASE,
)

SUBSYSTEM_PATTERN = re.compile(
    r"\*\*Subsystem:\*\*\s*`?([A-Za-z0-9_-]+)`?",
    re.IGNORECASE,
)

FILE_ANCHOR_PATTERN = re.compile(
    r"^# FILE:\s*(.+?)\s*$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class HanselContractIssue:
    """One deterministic Hansel contract integrity issue."""

    code: str
    message: str
    path: str


@dataclass(frozen=True)
class HanselContractValidation:
    """Deterministic validation result for one subsystem Hansel contract."""

    contract_path: str
    issues: tuple[HanselContractIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.issues


def validate_hansel_contract(
    subsystem_path: Path | str,
    *,
    repository_root: Path | str = ".",
) -> HanselContractValidation:
    """
    Validate one subsystem's canonical contracts/HANSEL.md.

    This validator checks only deterministic contract integrity.

    It does not infer semantic ownership, architecture, dependency correctness,
    or documentation completeness from prose structure.
    """

    root = Path(repository_root).resolve()

    subsystem = _resolve_subsystem_path(
        subsystem_path,
        root,
    )

    contract = (
        subsystem
        / "contracts"
        / "HANSEL.md"
    )

    issues: list[HanselContractIssue] = []

    if not contract.is_file():
        issues.append(
            HanselContractIssue(
                code="MISSING_CONTRACT",
                message=(
                    "Subsystem does not contain the canonical "
                    "contracts/HANSEL.md."
                ),
                path=_display_path(
                    contract,
                    root,
                ),
            )
        )

        return HanselContractValidation(
            contract_path=_display_path(
                contract,
                root,
            ),
            issues=tuple(issues),
        )

    text = contract.read_text(
        encoding="utf-8"
    )

    if not text.strip():
        issues.append(
            HanselContractIssue(
                code="BLANK_CONTRACT",
                message=(
                    "Canonical contracts/HANSEL.md must not be blank."
                ),
                path=_display_path(
                    contract,
                    root,
                ),
            )
        )

        return HanselContractValidation(
            contract_path=_display_path(
                contract,
                root,
            ),
            issues=tuple(issues),
        )

    _validate_contract_identity(
        text=text,
        subsystem=subsystem,
        contract=contract,
        root=root,
        issues=issues,
    )

    _validate_knowledge_states(
        text=text,
        contract=contract,
        root=root,
        issues=issues,
    )

    _validate_unknown_breadcrumbs(
        text=text,
        contract=contract,
        root=root,
        issues=issues,
    )

    _validate_repository_paths(
        text=text,
        contract=contract,
        root=root,
        issues=issues,
    )

    return HanselContractValidation(
        contract_path=_display_path(
            contract,
            root,
        ),
        issues=tuple(issues),
    )


def _validate_contract_identity(
    *,
    text: str,
    subsystem: Path,
    contract: Path,
    root: Path,
    issues: list[HanselContractIssue],
) -> None:
    """
    Verify explicit contract identity agrees with repository location.

    Identity metadata is optional, but when present it must be truthful.
    """

    expected_subsystem = subsystem.name

    subsystem_match = SUBSYSTEM_PATTERN.search(
        text
    )

    if (
        subsystem_match
        and subsystem_match.group(1).casefold()
        != expected_subsystem.casefold()
    ):
        issues.append(
            HanselContractIssue(
                code="SUBSYSTEM_IDENTITY_MISMATCH",
                message=(
                    "Contract declares subsystem "
                    f"'{subsystem_match.group(1)}' "
                    "but resides under "
                    f"'{expected_subsystem}'."
                ),
                path=_display_path(
                    contract,
                    root,
                ),
            )
        )

    file_match = FILE_ANCHOR_PATTERN.search(
        text
    )

    if not file_match:
        return

    declared_path = file_match.group(1).strip()

    expected_path = _display_path(
        contract,
        root,
    )

    if declared_path == expected_path:
        return

    issues.append(
        HanselContractIssue(
            code="FILE_ANCHOR_MISMATCH",
            message=(
                "Contract FILE anchor declares "
                f"'{declared_path}' "
                "but canonical path is "
                f"'{expected_path}'."
            ),
            path=expected_path,
        )
    )


def _validate_knowledge_states(
    *,
    text: str,
    contract: Path,
    root: Path,
    issues: list[HanselContractIssue],
) -> None:
    """Reject explicitly declared knowledge states outside the standard."""

    for match in KNOWLEDGE_STATE_PATTERN.finditer(
        text
    ):
        state = match.group(1).upper()

        if state in VALID_KNOWLEDGE_STATES:
            continue

        issues.append(
            HanselContractIssue(
                code="INVALID_KNOWLEDGE_STATE",
                message=(
                    "Unknown Hansel knowledge state: "
                    f"{state}."
                ),
                path=_display_path(
                    contract,
                    root,
                ),
            )
        )


def _validate_unknown_breadcrumbs(
    *,
    text: str,
    contract: Path,
    root: Path,
    issues: list[HanselContractIssue],
) -> None:
    """
    Require explicitly UNKNOWN sections to identify a next breadcrumb.

    Semantic correctness of the breadcrumb remains outside deterministic
    validation.
    """

    sections = re.split(
        r"(?=^#{2,6}\s+)",
        text,
        flags=re.MULTILINE,
    )

    for section in sections:
        if not re.search(
            r"Knowledge State:\s*UNKNOWN\b",
            section,
            flags=re.IGNORECASE,
        ):
            continue

        has_route_marker = re.search(
            r"(?:Next (?:Hansel )?Breadcrumb|Go to:)",
            section,
            flags=re.IGNORECASE,
        )

        has_repository_path = PATH_PATTERN.search(
            section
        )

        if (
            has_route_marker
            and has_repository_path
        ):
            continue

        issues.append(
            HanselContractIssue(
                code="UNKNOWN_WITHOUT_BREADCRUMB",
                message=(
                    "UNKNOWN knowledge must identify an actionable "
                    "repository breadcrumb."
                ),
                path=_display_path(
                    contract,
                    root,
                ),
            )
        )


def _validate_repository_paths(
    *,
    text: str,
    contract: Path,
    root: Path,
    issues: list[HanselContractIssue],
) -> None:
    """Verify deterministic repository paths referenced by the contract."""

    checked: set[str] = set()

    for match in PATH_PATTERN.finditer(
        text
    ):
        relative_path = _normalize_repository_path(
            match.group(0)
        )

        if relative_path in checked:
            continue

        checked.add(
            relative_path
        )

        destination = (
            root
            / relative_path
        )

        if destination.exists():
            continue

        issues.append(
            HanselContractIssue(
                code="BROKEN_BREADCRUMB",
                message=(
                    "Referenced repository authority "
                    "does not exist: "
                    f"{relative_path}"
                ),
                path=_display_path(
                    contract,
                    root,
                ),
            )
        )


def _normalize_repository_path(
    value: str,
) -> str:
    """Normalize one repository path extracted from contract text."""

    return value.rstrip(
        ".,:;`)"
    )


def _resolve_subsystem_path(
    subsystem_path: Path | str,
    root: Path,
) -> Path:
    """Resolve an absolute or repository-relative subsystem path."""

    path = Path(
        subsystem_path
    )

    if path.is_absolute():
        return path.resolve()

    return (
        root
        / path
    ).resolve()


def _display_path(
    path: Path,
    root: Path,
) -> str:
    """Return a stable repository-relative path when possible."""

    resolved = path.resolve()

    try:
        return str(
            resolved.relative_to(
                root
            )
        )
    except ValueError:
        return str(
            resolved
        )


# ======================================================================
# END: HANSEL_CONTRACT_VALIDATOR
# ======================================================================