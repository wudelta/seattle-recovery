# ======================================================================
# FILE: aurora/subsystems/delta_directives/services/deployment.py
# START: DIRECTIVE_DEPLOYMENT_SERVICE
# ======================================================================
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.db import transaction

from aurora.subsystems.delta_directives.models import DeltaDirectives


_DIRECTIVE_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

_HTML_TAG_PATTERN = re.compile(
    r"</?(?:"
    r"html|body|div|span|p|br|strong|em|ul|ol|li|"
    r"h[1-6]|table|thead|tbody|tr|th|td|pre|code"
    r")\b[^>]*>",
    re.IGNORECASE,
)


class DirectiveDeploymentError(Exception):
    """Raised when a worker directive cannot be safely deployed."""


@dataclass(frozen=True)
class DirectiveDeploymentResult:
    """Deterministic result of one directive deployment operation."""

    directive_name: str
    source_path: Path
    action: str
    applied: bool
    character_count: int


def get_directive_artifact_directory() -> Path:
    """Return the repository-owned directive deployment-artifact directory."""

    return (
        Path(settings.BASE_DIR)
        / "aurora"
        / "subsystems"
        / "delta_directives"
        / "directives"
    ).resolve()


def get_directive_artifact_path(directive_name: str) -> Path:
    """Resolve the one conventional deployment artifact for a directive."""

    _validate_directive_name(directive_name)

    return (
        get_directive_artifact_directory()
        / f"{directive_name}.md"
    ).resolve()


def deploy_directive(
    *,
    directive_name: str,
    user,
    apply: bool,
) -> DirectiveDeploymentResult:
    """
    Validate and optionally deploy one complete worker directive.

    Repository Markdown files are deployment artifacts only.
    DeltaDirectives.instructions remains the canonical persistent authority.
    """

    if not getattr(user, "is_authenticated", False):
        raise DirectiveDeploymentError(
            "Directive deployment requires an authenticated user."
        )

    source_path = get_directive_artifact_path(directive_name)
    source_text = _load_and_validate_source(
        directive_name=directive_name,
        source_path=source_path,
    )

    existing = DeltaDirectives.objects.filter(
        directive_name=directive_name
    ).first()

    action = "REPLACE" if existing is not None else "CREATE"

    if not apply:
        return DirectiveDeploymentResult(
            directive_name=directive_name,
            source_path=source_path,
            action=action,
            applied=False,
            character_count=len(source_text),
        )

    with transaction.atomic():
        directive = (
            DeltaDirectives.objects.select_for_update()
            .filter(directive_name=directive_name)
            .first()
        )

        if directive is None:
            directive = DeltaDirectives(
                directive_name=directive_name,
                instructions=source_text,
                created_by=user,
            )
        else:
            directive.instructions = source_text

        directive.save()

        persisted_text = DeltaDirectives.objects.values_list(
            "instructions",
            flat=True,
        ).get(pk=directive.pk)

        if persisted_text != source_text:
            raise DirectiveDeploymentError(
                "Post-apply equivalence validation failed for "
                f'"{directive_name}".'
            )

    return DirectiveDeploymentResult(
        directive_name=directive_name,
        source_path=source_path,
        action=action,
        applied=True,
        character_count=len(source_text),
    )


def _validate_directive_name(directive_name: str) -> None:
    if not directive_name:
        raise DirectiveDeploymentError(
            "Directive name is required."
        )

    if not _DIRECTIVE_NAME_PATTERN.fullmatch(directive_name):
        raise DirectiveDeploymentError(
            "Directive name must begin with a letter and contain only "
            "letters, numbers, and underscores."
        )


def _load_and_validate_source(
    *,
    directive_name: str,
    source_path: Path,
) -> str:
    canonical_directory = get_directive_artifact_directory()

    try:
        source_path.relative_to(canonical_directory)
    except ValueError as exc:
        raise DirectiveDeploymentError(
            "Directive artifact resolved outside the canonical "
            "deployment directory."
        ) from exc

    if source_path.name != f"{directive_name}.md":
        raise DirectiveDeploymentError(
            "Directive artifact filename does not match directive identity."
        )

    try:
        source_text = source_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise DirectiveDeploymentError(
            f'Directive artifact does not exist: "{source_path}".'
        ) from exc
    except (OSError, UnicodeError) as exc:
        raise DirectiveDeploymentError(
            f'Unable to read directive artifact "{source_path}": {exc}'
        ) from exc

    if not source_text.strip():
        raise DirectiveDeploymentError(
            f'Directive artifact "{source_path}" is empty.'
        )

    if "\x00" in source_text:
        raise DirectiveDeploymentError(
            f'Directive artifact "{source_path}" contains a null byte.'
        )

    if _HTML_TAG_PATTERN.search(source_text):
        raise DirectiveDeploymentError(
            f'Directive artifact "{source_path}" contains HTML markup. '
            "Canonical worker instructions must use Markdown text."
        )

    return source_text
# ======================================================================
# FILE: aurora/subsystems/delta_directives/services/deployment.py
# END: DIRECTIVE_DEPLOYMENT_SERVICE
# ======================================================================