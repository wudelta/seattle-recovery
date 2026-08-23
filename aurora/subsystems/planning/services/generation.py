# ======================================================================
# FILE: aurora/subsystems/planning/services/generation.py
# START: PLANNING_GENERATION_SERVICE
# ======================================================================

from ast import literal_eval
from dataclasses import dataclass
from pathlib import Path
from pprint import pformat
from typing import Any

from aurora.minions.engine import MinionRunner
from aurora.subsystems.planning.io.exceptions import (
    PlanningImportError,
    PlanningSchemaError,
)
from aurora.subsystems.planning.io.updater import (
    PlanningUpdateResult,
    update_planning_document,
)
from aurora.subsystems.planning.services.reconciliation import (
    build_initiative_reconciliation_snapshot,
    build_planning_reconciliation_summary,
)
from aurora.subsystems.planning.services.generation_preflight import (
    PlanningGenerationPreflightError,
    preflight_planning_generation,
)


PLANNING_GENERATOR_DIRECTIVE = "planning_generator"

PLANNING_ROOT = Path(__file__).resolve().parents[1]

PLANNING_TEMPLATE_PATH = (
    PLANNING_ROOT
    / "io"
    / "templates"
    / "planning_update_v1.plan"
)


class PlanningGenerationError(RuntimeError):
    """Raised when AI planning generation cannot produce a valid proposal."""


@dataclass(frozen=True)
class PlanningGenerationResult:
    """One validated, non-applied Planning proposal."""

    document: dict[str, Any]
    validation: PlanningUpdateResult
    raw_response: str


def generate_planning_update(
    *,
    engineering_intent: str,
    project_slug: str,
    user,
) -> PlanningGenerationResult:
    """
    Generate and dry-run one Planning dictionary.

    Persisted Planning evidence is supplied progressively so the worker
    can reconcile intent against exact existing Initiative, Phase, and
    Step titles.

    Current lifecycle state is established deterministically before AI
    generation begins.

    Generated Planning proposals must contain actionable work. A newly
    generated Phase may not be empty.

    This service never applies Planning mutations.
    """

    intent = engineering_intent.strip()
    slug = project_slug.strip()

    if not intent:
        raise PlanningGenerationError(
            "Engineering intent is required."
        )

    if not slug:
        raise PlanningGenerationError(
            "Target Project slug is required."
        )

    if user is None or not user.pk:
        raise PlanningGenerationError(
            "A persisted user is required."
        )

    try:
        preflight = preflight_planning_generation(
            project_slug=slug,
            user=user,
        )
    except PlanningGenerationPreflightError as error:
        raise PlanningGenerationError(
            f"Planning lifecycle preflight failed: {error}"
        ) from error

    planning_evidence = _build_project_planning_evidence(
        project_slug=slug,
    )

    planning_evidence["lifecycle_preflight"] = (
        preflight.as_evidence()
    )

    task_input = _build_generation_task(
        engineering_intent=intent,
        project_slug=slug,
        planning_evidence=planning_evidence,
    )

    runner = MinionRunner()

    raw_response = runner.run_minion_task(
        PLANNING_GENERATOR_DIRECTIVE,
        task_input,
    )

    document = _parse_planning_dictionary(
        raw_response
    )

    _validate_generated_actionability(
        document
    )

    try:
        validation = update_planning_document(
            document,
            user=user,
            apply=False,
        )
    except (
        PlanningSchemaError,
        PlanningImportError,
    ) as error:
        raise PlanningGenerationError(
            "Generated Planning dictionary failed validation: "
            f"{error}"
        ) from error

    return PlanningGenerationResult(
        document=document,
        validation=validation,
        raw_response=raw_response,
    )


def _build_project_planning_evidence(
    *,
    project_slug: str,
) -> dict[str, Any]:
    """
    Return progressively bounded Planning evidence for one Project.

    The compact reconciliation summary identifies candidate Initiatives.
    Each candidate is then expanded only to its bounded Initiative summary
    so exact persisted Phase and Step titles are available for safe targeting.
    """

    summary = build_planning_reconciliation_summary()

    candidates = [
        candidate
        for candidate in summary.get(
            "current_work_candidates",
            [],
        )
        if candidate.get("project") == project_slug
    ]

    initiative_details = []

    for candidate in candidates:
        initiative_id = candidate.get(
            "initiative_id"
        )

        if initiative_id is None:
            continue

        initiative_details.append(
            build_initiative_reconciliation_snapshot(
                initiative_id,
                full=False,
            )
        )

    conflicts = []

    for conflict in summary.get(
        "execution_conflicts",
        [],
    ):
        initiatives = [
            initiative
            for initiative in conflict.get(
                "initiatives",
                [],
            )
            if initiative.get("project") == project_slug
        ]

        if not initiatives:
            continue

        bounded_conflict = dict(conflict)
        bounded_conflict["initiatives"] = initiatives
        conflicts.append(bounded_conflict)

    return {
        "project_slug": project_slug,
        "current_work_candidates": candidates,
        "initiative_details": initiative_details,
        "execution_conflicts": conflicts,
    }


def _build_generation_task(
    *,
    engineering_intent: str,
    project_slug: str,
    planning_evidence: dict[str, Any],
) -> str:
    """Build the bounded task given to the Planning Generator."""

    template = _load_canonical_template()

    evidence_text = pformat(
        planning_evidence,
        sort_dicts=False,
        width=100,
    )

    grouped_addition_guidance = (
        "When extending EXISTING Planning work, use these exact group "
        "shapes.\n\n"
        "ADD PHASES TO AN EXISTING INITIATIVE:\n"
        "{\n"
        '    "initiative_title": "Existing Initiative title",\n'
        '    "phases": [\n'
        "        {\n"
        '            "title": "New Phase title",\n'
        '            "description": "New Phase description",\n'
        '            "status": "PLANNED",\n'
        '            "steps": [\n'
        "                {\n"
        '                    "title": "Actionable Step title",\n'
        '                    "description": '
        '"Describe one bounded implementation or discovery task.",\n'
        '                    "status": "PLANNED",\n'
        '                    "estimated_minutes": 60,\n'
        '                    "estimate_confidence": "MEDIUM",\n'
        '                    "risk_level": "LOW",\n'
        '                    "risk_description": "",\n'
        '                    "validation_description": '
        '"Describe deterministic completion evidence.",\n'
        '                    "document": {\n'
        '                        "technical_design": "",\n'
        '                        "dependencies": "",\n'
        '                        "assumptions": "",\n'
        '                        "implementation_notes": "",\n'
        '                        "discussion": "",\n'
        "                    },\n"
        '                    "validation": {\n'
        '                        "description": '
        '"Describe deterministic completion evidence.",\n'
        '                        "notes": "",\n'
        "                    },\n"
        '                    "planned_files": [],\n'
        '                    "actual_files": [],\n'
        "                },\n"
        "            ],\n"
        "        },\n"
        "    ],\n"
        "}\n\n"
        "ADD STEPS TO AN EXISTING PHASE:\n"
        "{\n"
        '    "initiative_title": "Existing Initiative title",\n'
        '    "phase_title": "Existing Phase title",\n'
        '    "steps": [\n'
        "        {\n"
        '            "title": "New Step title",\n'
        '            "description": "New Step description",\n'
        '            "status": "PLANNED",\n'
        '            "estimated_minutes": 60,\n'
        '            "estimate_confidence": "MEDIUM",\n'
        '            "risk_level": "LOW",\n'
        '            "risk_description": "",\n'
        '            "validation_description": '
        '"Describe deterministic completion evidence.",\n'
        '            "document": {\n'
        '                "technical_design": "",\n'
        '                "dependencies": "",\n'
        '                "assumptions": "",\n'
        '                "implementation_notes": "",\n'
        '                "discussion": "",\n'
        "            },\n"
        '            "validation": {\n'
        '                "description": '
        '"Describe deterministic completion evidence.",\n'
        '                "notes": "",\n'
        "            },\n"
        '            "planned_files": [],\n'
        '            "actual_files": [],\n'
        "        },\n"
        "    ],\n"
        "}\n\n"
        "Every newly generated Phase MUST contain at least one actionable "
        "Step.\n"
        "Never generate a new Phase with steps: [].\n"
        "If an appropriate existing Phase already owns the engineering "
        "intent, prefer add_steps instead of creating another Phase.\n"
        "Use add_phases only when a genuinely new architectural milestone "
        "is required inside the existing Initiative.\n"
        "When targeting an existing Initiative or Phase, copy its title "
        "EXACTLY from the persisted Planning evidence. "
        "Do not paraphrase, normalize, expand, abbreviate, or improve an "
        "existing title.\n"
        "Do not place Phase fields directly inside an add_phases group.\n"
        "Do not place Step fields directly inside an add_steps group.\n"
        "Do not use initiative_id, phase_id, or any database ID in a "
        "planning dictionary.\n"
        "Existing Initiative and Phase targets are identified only by their "
        "exact persisted titles.\n"
    )

    return (
        "Generate one Decision Engine planning dictionary.\n\n"
        f"Target Project slug: {project_slug}\n\n"
        "Engineering intent:\n"
        f"{engineering_intent}\n\n"
        "Persisted Planning reconciliation evidence for the target Project "
        "follows.\n\n"
        "PLANNING EVIDENCE START\n"
        f"{evidence_text}\n"
        "PLANNING EVIDENCE END\n\n"
        "Reconcile the engineering intent against this existing Planning "
        "evidence before choosing what to add. "
        "The Initiative detail evidence contains exact persisted Phase and "
        "Step titles. "
        "When targeting existing work, copy those titles exactly. "
        "Do not create a new Initiative merely because the intent is new to "
        "this conversation. "
        "If the work belongs to an existing Initiative, first determine "
        "whether an existing Phase already owns the work. "
        "If so, prefer add_steps. "
        "If a genuinely new architectural milestone is required, use "
        "add_phases. "
        "Create a new Initiative only when the intent represents a distinct "
        "durable engineering outcome not already owned by existing Planning "
        "work.\n\n"
        f"{grouped_addition_guidance}\n"
        "The repository-owned canonical output template follows.\n"
        "Your response MUST use this exact top-level schema and only fields "
        "represented by this template or the grouped-addition shapes above."
        "\n\n"
        "CANONICAL TEMPLATE START\n"
        f"{template}\n"
        "CANONICAL TEMPLATE END\n\n"
        "Adapt the template to the engineering intent and persisted Planning "
        "evidence. "
        "For an existing Project, use add_projects: []. "
        "Every newly generated Phase must contain at least one bounded Step. "
        "Return exactly one Python-literal dictionary. "
        "Do not include Markdown fences, assignments, imports, headings, "
        "explanations, or commentary."
    )


def _load_canonical_template() -> str:
    """Load the repository-owned Planning dictionary template."""

    try:
        return PLANNING_TEMPLATE_PATH.read_text(
            encoding="utf-8"
        )
    except OSError as error:
        raise PlanningGenerationError(
            "Unable to load the canonical Planning dictionary template: "
            f"{PLANNING_TEMPLATE_PATH}"
        ) from error


def _parse_planning_dictionary(
    raw_response: str,
) -> dict[str, Any]:
    """Parse one AI response as a Python-literal Planning dictionary."""

    if not isinstance(raw_response, str):
        raise PlanningGenerationError(
            "Planning Generator returned a non-text response."
        )

    source = raw_response.strip()

    if not source:
        raise PlanningGenerationError(
            "Planning Generator returned an empty response."
        )

    try:
        document = literal_eval(source)
    except (
        SyntaxError,
        ValueError,
    ) as error:
        raise PlanningGenerationError(
            "Planning Generator did not return one valid "
            "Python-literal dictionary."
        ) from error

    if not isinstance(document, dict):
        raise PlanningGenerationError(
            "Planning Generator response must evaluate to a dictionary."
        )

    return document


def _validate_generated_actionability(
    document: dict[str, Any],
) -> None:
    """
    Require actionable Steps in every newly generated Phase.

    This rule applies to AI-generated Planning proposals only. It does not
    change the general Planning dictionary schema.
    """

    for initiative in document.get(
        "add_initiatives",
        [],
    ):
        initiative_title = initiative.get(
            "title",
            "<untitled Initiative>",
        )

        for phase in initiative.get(
            "phases",
            [],
        ):
            _require_generated_phase_steps(
                phase=phase,
                context=(
                    f'Initiative "{initiative_title}"'
                ),
            )

    for addition in document.get(
        "add_phases",
        [],
    ):
        initiative_title = addition.get(
            "initiative_title",
            "<unknown Initiative>",
        )

        for phase in addition.get(
            "phases",
            [],
        ):
            _require_generated_phase_steps(
                phase=phase,
                context=(
                    f'Initiative "{initiative_title}"'
                ),
            )


def _require_generated_phase_steps(
    *,
    phase: dict[str, Any],
    context: str,
) -> None:
    """Reject one generated Phase when it contains no Steps."""

    steps = phase.get(
        "steps",
        [],
    )

    if steps:
        return

    phase_title = phase.get(
        "title",
        "<untitled Phase>",
    )

    raise PlanningGenerationError(
        "Generated Planning proposal contains an empty Phase: "
        f'"{phase_title}" in {context}. '
        "Every generated Phase must contain at least one Step."
    )


# ======================================================================
# END: PLANNING_GENERATION_SERVICE
# ======================================================================