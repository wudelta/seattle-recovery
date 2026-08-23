# ======================================================================
# FILE: aurora/subsystems/hansel/services/generator.py
# START: HANSEL_SUBSYSTEM_GENERATOR
# ======================================================================

from dataclasses import dataclass
from pathlib import Path
import re
import shutil

from aurora.subsystems.hansel.validators.hansel_contract import (
    validate_hansel_contract,
)


SUBSYSTEM_PATTERN = re.compile(
    r"^[a-z][a-z0-9_]*$"
)

TEMPLATE_PATH = Path(
    "aurora/subsystems/hansel/templates/"
    "subsystem_contracts/HANSEL.md"
)

SUBSYSTEMS_PATH = Path(
    "aurora/subsystems"
)

REQUIRED_PLACEHOLDERS = (
    "<subsystem>",
    "<Subsystem>",
    "<SUBSYSTEM>",
)


class SubsystemGenerationError(RuntimeError):
    """Raised when deterministic subsystem generation cannot proceed."""


@dataclass(frozen=True)
class SubsystemGenerationResult:
    """Result of one deterministic subsystem generation request."""

    subsystem: str
    destination: str
    directories: tuple[str, ...]
    files: tuple[str, ...]
    applied: bool


def generate_subsystem(
    subsystem: str,
    *,
    repository_root: Path | str = ".",
    apply: bool = False,
) -> SubsystemGenerationResult:
    """
    Preflight, render, and optionally create one minimal Aurora subsystem.

    Dry-run behavior is represented by apply=False.
    """

    root = Path(
        repository_root
    ).resolve()

    identifier = _validate_identifier(
        subsystem
    )

    subsystems_root = (
        root
        / SUBSYSTEMS_PATH
    ).resolve()

    template_path = (
        root
        / TEMPLATE_PATH
    ).resolve()

    destination = (
        subsystems_root
        / identifier
    ).resolve()

    _validate_destination(
        destination=destination,
        subsystems_root=subsystems_root,
    )

    template = _load_template(
        template_path
    )

    rendered = _render_template(
        template,
        identifier,
    )

    directories = (
        destination,
        destination / "contracts",
    )

    files = (
        destination / "__init__.py",
        destination / "contracts" / "__init__.py",
        destination / "contracts" / "HANSEL.md",
    )

    result = SubsystemGenerationResult(
        subsystem=identifier,
        destination=_display_path(
            destination,
            root,
        ),
        directories=tuple(
            _display_path(
                path,
                root,
            )
            for path in directories
        ),
        files=tuple(
            _display_path(
                path,
                root,
            )
            for path in files
        ),
        applied=apply,
    )

    if not apply:
        return result

    _apply_generation(
        root=root,
        destination=destination,
        rendered_contract=rendered,
    )

    return result


def _validate_identifier(
    subsystem: str,
) -> str:
    """Return a validated canonical subsystem identifier."""

    identifier = str(
        subsystem
    ).strip()

    if not identifier:
        raise SubsystemGenerationError(
            "Subsystem identifier is required."
        )

    if not SUBSYSTEM_PATTERN.fullmatch(
        identifier
    ):
        raise SubsystemGenerationError(
            "Subsystem identifier must use lowercase snake_case, "
            "begin with a lowercase ASCII letter, and contain only "
            "lowercase ASCII letters, digits, and underscores."
        )

    return identifier


def _validate_destination(
    *,
    destination: Path,
    subsystems_root: Path,
) -> None:
    """Verify repository destination safety and collision absence."""

    if not subsystems_root.is_dir():
        raise SubsystemGenerationError(
            "Canonical subsystem root does not exist: "
            f"{subsystems_root}"
        )

    try:
        destination.relative_to(
            subsystems_root
        )
    except ValueError as exc:
        raise SubsystemGenerationError(
            "Generated subsystem destination escapes "
            "aurora/subsystems/."
        ) from exc

    if destination.parent != subsystems_root:
        raise SubsystemGenerationError(
            "Generated subsystem must be a direct child "
            "of aurora/subsystems/."
        )

    if destination.exists():
        raise SubsystemGenerationError(
            "Subsystem destination already exists: "
            f"{destination}"
        )


def _load_template(
    template_path: Path,
) -> str:
    """Load and preflight the canonical repository-owned template."""

    if not template_path.is_file():
        raise SubsystemGenerationError(
            "Canonical Hansel subsystem template does not exist: "
            f"{template_path}"
        )

    try:
        template = template_path.read_text(
            encoding="utf-8"
        )
    except (OSError, UnicodeError) as exc:
        raise SubsystemGenerationError(
            "Unable to read canonical Hansel subsystem template: "
            f"{template_path}"
        ) from exc

    missing = [
        placeholder
        for placeholder in REQUIRED_PLACEHOLDERS
        if placeholder not in template
    ]

    if missing:
        raise SubsystemGenerationError(
            "Canonical Hansel subsystem template is missing "
            "required placeholders: "
            + ", ".join(
                missing
            )
        )

    return template


def _render_template(
    template: str,
    subsystem: str,
) -> str:
    """Perform deterministic template placeholder substitution."""

    title = " ".join(
        part.capitalize()
        for part in subsystem.split("_")
    )

    rendered = template.replace(
        "<subsystem>",
        subsystem,
    )

    rendered = rendered.replace(
        "<Subsystem>",
        title,
    )

    rendered = rendered.replace(
        "<SUBSYSTEM>",
        subsystem.upper(),
    )

    return rendered


def _apply_generation(
    *,
    root: Path,
    destination: Path,
    rendered_contract: str,
) -> None:
    """Create, validate, and atomically retain one subsystem scaffold."""

    created_destination = False

    try:
        destination.mkdir()
        created_destination = True

        contracts = (
            destination
            / "contracts"
        )

        contracts.mkdir()

        (
            destination
            / "__init__.py"
        ).write_text(
            "",
            encoding="utf-8",
        )

        (
            contracts
            / "__init__.py"
        ).write_text(
            "",
            encoding="utf-8",
        )

        (
            contracts
            / "HANSEL.md"
        ).write_text(
            rendered_contract,
            encoding="utf-8",
        )

        validation = validate_hansel_contract(
            destination,
            repository_root=root,
        )

        if not validation.is_valid:
            details = "; ".join(
                f"{issue.code}: {issue.message}"
                for issue in validation.issues
            )

            raise SubsystemGenerationError(
                "Generated Hansel contract failed deterministic "
                f"validation: {details}"
            )

    except Exception as exc:
        if created_destination:
            try:
                shutil.rmtree(
                    destination
                )
            except OSError as cleanup_exc:
                raise SubsystemGenerationError(
                    "Subsystem generation failed and atomic cleanup "
                    f"also failed for {destination}: {cleanup_exc}"
                ) from exc

        if isinstance(
            exc,
            SubsystemGenerationError,
        ):
            raise

        raise SubsystemGenerationError(
            f"Unable to generate subsystem at {destination}: {exc}"
        ) from exc


def _display_path(
    path: Path,
    root: Path,
) -> str:
    """Return a stable repository-relative path when possible."""

    try:
        return str(
            path.relative_to(
                root
            )
        )
    except ValueError:
        return str(
            path
        )


# ======================================================================
# END: HANSEL_SUBSYSTEM_GENERATOR
# ======================================================================