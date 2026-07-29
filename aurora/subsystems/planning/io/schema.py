# ======================================================================
# FILE: aurora/subsystems/planning/io/schema.py
# START: PLANNING_DOCUMENT_SCHEMA
# ======================================================================
from collections.abc import Callable, Mapping
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import validate_slug

from aurora.models import EstimateConfidence, ExecutionStatus, RiskLevel
from aurora.subsystems.planning.io.exceptions import PlanningSchemaError


SCHEMA_VERSION = 1

PROJECT_FIELDS = {
    "title",
    "slug",
    "description",
    "status",
    "position",
    "active",
    "initiatives",
}

INITIATIVE_FIELDS = {
    "title",
    "description",
    "status",
    "position",
    "phases",
}

PHASE_FIELDS = {
    "title",
    "description",
    "status",
    "position",
    "steps",
}

STEP_FIELDS = {
    "title",
    "description",
    "status",
    "position",
    "estimated_minutes",
    "estimate_confidence",
    "risk_level",
    "risk_description",
    "validation_description",
}

PLANNING_UPDATE_FIELDS = {
    "schema_version",
    "target",
    "add_initiatives",
    "add_phases",
    "add_steps",
}

UPDATE_TARGET_FIELDS = {
    "project_slug",
}

PHASE_ADDITION_FIELDS = {
    "initiative_title",
    "phases",
}

STEP_ADDITION_FIELDS = {
    "initiative_title",
    "phase_title",
    "steps",
}


def validate_planning_document(document: Any) -> dict[str, Any]:
    """Validate and normalize a version-one planning document."""

    root = _require_mapping(document, "document")
    _reject_unknown_fields(root, {"schema_version", "project"}, "document")

    schema_version = root.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        raise PlanningSchemaError(
            f"document.schema_version must be {SCHEMA_VERSION}."
        )

    project = _validate_project(root.get("project"), "project")

    return {
        "schema_version": SCHEMA_VERSION,
        "project": project,
    }


def validate_planning_update(document: Any) -> dict[str, Any]:
    """Validate and normalize an append-only planning update."""

    root = _require_mapping(document, "document")
    _reject_unknown_fields(root, PLANNING_UPDATE_FIELDS, "document")

    schema_version = root.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        raise PlanningSchemaError(
            f"document.schema_version must be {SCHEMA_VERSION}."
        )

    target = _validate_update_target(root.get("target"), "target")

    add_initiatives = _validate_update_children(
        root.get("add_initiatives", []),
        "add_initiatives",
        _validate_update_initiative,
    )
    add_phases = _validate_update_groups(
        root.get("add_phases", []),
        "add_phases",
        _validate_phase_addition,
    )
    add_steps = _validate_update_groups(
        root.get("add_steps", []),
        "add_steps",
        _validate_step_addition,
    )

    if not add_initiatives and not add_phases and not add_steps:
        raise PlanningSchemaError(
            "document must contain at least one planning addition."
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "target": target,
        "add_initiatives": add_initiatives,
        "add_phases": add_phases,
        "add_steps": add_steps,
    }


def _validate_project(value: Any, path: str) -> dict[str, Any]:
    project = _require_mapping(value, path)
    _reject_unknown_fields(project, PROJECT_FIELDS, path)

    slug = _require_text(project.get("slug"), f"{path}.slug")

    try:
        validate_slug(slug)
    except ValidationError as exc:
        raise PlanningSchemaError(
            f"{path}.slug must be a valid slug."
        ) from exc

    return {
        "title": _require_text(project.get("title"), f"{path}.title"),
        "slug": slug,
        "description": _optional_text(
            project.get("description"),
            f"{path}.description",
        ),
        "status": _validate_choice(
            project.get("status", ExecutionStatus.PLANNED),
            ExecutionStatus.values,
            f"{path}.status",
        ),
        "position": _validate_position(
            project.get("position", 1),
            f"{path}.position",
        ),
        "active": _validate_boolean(
            project.get("active", True),
            f"{path}.active",
        ),
        "initiatives": _validate_children(
            project.get("initiatives", []),
            f"{path}.initiatives",
            _validate_initiative,
        ),
    }


def _validate_initiative(value: Any, path: str) -> dict[str, Any]:
    initiative = _require_mapping(value, path)
    _reject_unknown_fields(initiative, INITIATIVE_FIELDS, path)

    return {
        "title": _require_text(
            initiative.get("title"),
            f"{path}.title",
        ),
        "description": _optional_text(
            initiative.get("description"),
            f"{path}.description",
        ),
        "status": _validate_choice(
            initiative.get("status", ExecutionStatus.PLANNED),
            ExecutionStatus.values,
            f"{path}.status",
        ),
        "position": _validate_position(
            initiative.get("position", 1),
            f"{path}.position",
        ),
        "phases": _validate_children(
            initiative.get("phases", []),
            f"{path}.phases",
            _validate_phase,
        ),
    }


def _validate_phase(value: Any, path: str) -> dict[str, Any]:
    phase = _require_mapping(value, path)
    _reject_unknown_fields(phase, PHASE_FIELDS, path)

    return {
        "title": _require_text(
            phase.get("title"),
            f"{path}.title",
        ),
        "description": _optional_text(
            phase.get("description"),
            f"{path}.description",
        ),
        "status": _validate_choice(
            phase.get("status", ExecutionStatus.PLANNED),
            ExecutionStatus.values,
            f"{path}.status",
        ),
        "position": _validate_position(
            phase.get("position", 1),
            f"{path}.position",
        ),
        "steps": _validate_children(
            phase.get("steps", []),
            f"{path}.steps",
            _validate_step,
        ),
    }


def _validate_step(value: Any, path: str) -> dict[str, Any]:
    step = _require_mapping(value, path)
    _reject_unknown_fields(step, STEP_FIELDS, path)

    estimated_minutes = step.get("estimated_minutes")
    if estimated_minutes is not None:
        estimated_minutes = _validate_positive_integer(
            estimated_minutes,
            f"{path}.estimated_minutes",
        )

    estimate_confidence = step.get("estimate_confidence")
    if estimate_confidence is not None:
        estimate_confidence = _validate_choice(
            estimate_confidence,
            EstimateConfidence.values,
            f"{path}.estimate_confidence",
        )

    return {
        "title": _require_text(
            step.get("title"),
            f"{path}.title",
        ),
        "description": _optional_text(
            step.get("description"),
            f"{path}.description",
        ),
        "status": _validate_choice(
            step.get("status", ExecutionStatus.PLANNED),
            ExecutionStatus.values,
            f"{path}.status",
        ),
        "position": _validate_position(
            step.get("position", 1),
            f"{path}.position",
        ),
        "estimated_minutes": estimated_minutes,
        "estimate_confidence": estimate_confidence,
        "risk_level": _validate_choice(
            step.get("risk_level", RiskLevel.LOW),
            RiskLevel.values,
            f"{path}.risk_level",
        ),
        "risk_description": _optional_text(
            step.get("risk_description"),
            f"{path}.risk_description",
        ),
        "validation_description": _optional_text(
            step.get("validation_description"),
            f"{path}.validation_description",
        ),
    }


def _validate_update_target(value: Any, path: str) -> dict[str, Any]:
    target = _require_mapping(value, path)
    _reject_unknown_fields(target, UPDATE_TARGET_FIELDS, path)

    project_slug = _require_text(
        target.get("project_slug"),
        f"{path}.project_slug",
    )

    try:
        validate_slug(project_slug)
    except ValidationError as exc:
        raise PlanningSchemaError(
            f"{path}.project_slug must be a valid slug."
        ) from exc

    return {
        "project_slug": project_slug,
    }


def _validate_update_initiative(
    value: Any,
    path: str,
) -> dict[str, Any]:
    initiative = _require_mapping(value, path)
    _reject_unknown_fields(
        initiative,
        INITIATIVE_FIELDS - {"position"},
        path,
    )

    return {
        "title": _require_text(
            initiative.get("title"),
            f"{path}.title",
        ),
        "description": _optional_text(
            initiative.get("description"),
            f"{path}.description",
        ),
        "status": _validate_choice(
            initiative.get("status", ExecutionStatus.PLANNED),
            ExecutionStatus.values,
            f"{path}.status",
        ),
        "phases": _validate_update_children(
            initiative.get("phases", []),
            f"{path}.phases",
            _validate_update_phase,
        ),
    }


def _validate_update_phase(
    value: Any,
    path: str,
) -> dict[str, Any]:
    phase = _require_mapping(value, path)
    _reject_unknown_fields(
        phase,
        PHASE_FIELDS - {"position"},
        path,
    )

    return {
        "title": _require_text(
            phase.get("title"),
            f"{path}.title",
        ),
        "description": _optional_text(
            phase.get("description"),
            f"{path}.description",
        ),
        "status": _validate_choice(
            phase.get("status", ExecutionStatus.PLANNED),
            ExecutionStatus.values,
            f"{path}.status",
        ),
        "steps": _validate_update_children(
            phase.get("steps", []),
            f"{path}.steps",
            _validate_update_step,
        ),
    }


def _validate_update_step(
    value: Any,
    path: str,
) -> dict[str, Any]:
    step = _require_mapping(value, path)
    _reject_unknown_fields(
        step,
        STEP_FIELDS - {"position"},
        path,
    )

    normalized = _validate_step(
        {
            **step,
            "position": 1,
        },
        path,
    )
    normalized.pop("position")

    return normalized


def _validate_phase_addition(
    value: Any,
    path: str,
) -> dict[str, Any]:
    addition = _require_mapping(value, path)
    _reject_unknown_fields(addition, PHASE_ADDITION_FIELDS, path)

    phases = _validate_update_children(
        addition.get("phases"),
        f"{path}.phases",
        _validate_update_phase,
    )
    if not phases:
        raise PlanningSchemaError(
            f"{path}.phases must contain at least one item."
        )

    return {
        "initiative_title": _require_text(
            addition.get("initiative_title"),
            f"{path}.initiative_title",
        ),
        "phases": phases,
    }


def _validate_step_addition(
    value: Any,
    path: str,
) -> dict[str, Any]:
    addition = _require_mapping(value, path)
    _reject_unknown_fields(addition, STEP_ADDITION_FIELDS, path)

    steps = _validate_update_children(
        addition.get("steps"),
        f"{path}.steps",
        _validate_update_step,
    )
    if not steps:
        raise PlanningSchemaError(
            f"{path}.steps must contain at least one item."
        )

    return {
        "initiative_title": _require_text(
            addition.get("initiative_title"),
            f"{path}.initiative_title",
        ),
        "phase_title": _require_text(
            addition.get("phase_title"),
            f"{path}.phase_title",
        ),
        "steps": steps,
    }


def _validate_children(
    value: Any,
    path: str,
    validator: Callable[[Any, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise PlanningSchemaError(f"{path} must be a list.")

    children = []

    for index, child in enumerate(value):
        child_path = f"{path}[{index}]"
        child_mapping = _require_mapping(child, child_path)
        validated_child = validator(child_mapping, child_path)

        if "position" not in child_mapping:
            validated_child["position"] = index + 1

        children.append(validated_child)

    positions = [child["position"] for child in children]
    if len(positions) != len(set(positions)):
        raise PlanningSchemaError(
            f"{path} contains duplicate positions."
        )

    return children


def _validate_update_children(
    value: Any,
    path: str,
    validator: Callable[[Any, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise PlanningSchemaError(f"{path} must be a list.")

    children = [
        validator(child, f"{path}[{index}]")
        for index, child in enumerate(value)
    ]

    titles = [child["title"] for child in children]
    if len(titles) != len(set(titles)):
        raise PlanningSchemaError(
            f"{path} contains duplicate titles."
        )

    return children


def _validate_update_groups(
    value: Any,
    path: str,
    validator: Callable[[Any, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise PlanningSchemaError(f"{path} must be a list.")

    return [
        validator(group, f"{path}[{index}]")
        for index, group in enumerate(value)
    ]


def _require_mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise PlanningSchemaError(f"{path} must be a mapping.")

    return value


def _reject_unknown_fields(
    value: Mapping[str, Any],
    allowed_fields: set[str],
    path: str,
) -> None:
    unknown_fields = sorted(set(value) - allowed_fields)

    if unknown_fields:
        raise PlanningSchemaError(
            f"{path} contains unknown fields: "
            f"{', '.join(unknown_fields)}."
        )


def _require_text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PlanningSchemaError(
            f"{path} must be non-empty text."
        )

    return value.strip()


def _optional_text(value: Any, path: str) -> str:
    if value is None:
        return ""

    if not isinstance(value, str):
        raise PlanningSchemaError(f"{path} must be text.")

    return value.strip()


def _validate_choice(
    value: Any,
    choices: list[str],
    path: str,
) -> str:
    if value not in choices:
        raise PlanningSchemaError(
            f"{path} must be one of: {', '.join(choices)}."
        )

    return value


def _validate_position(value: Any, path: str) -> int:
    return _validate_positive_integer(value, path)


def _validate_positive_integer(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise PlanningSchemaError(
            f"{path} must be a positive integer."
        )

    return value


def _validate_boolean(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise PlanningSchemaError(
            f"{path} must be true or false."
        )

    return value
# ======================================================================
# END: PLANNING_DOCUMENT_SCHEMA
# ======================================================================