# ======================================================================
# FILE: aurora/subsystems/planning/services/reconciliation.py
# START: PLANNING_RECONCILIATION_IMPORTS
# ======================================================================

from typing import Any

from aurora.models import Project, UserPosition
from django.core.exceptions import ObjectDoesNotExist

# ======================================================================
# FILE: aurora/subsystems/planning/services/reconciliation.py
# END: PLANNING_RECONCILIATION_IMPORTS
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/planning/services/reconciliation.py
# START: PLANNING_RECONCILIATION_SNAPSHOT_SERVICE
# ======================================================================

def _serialize_user(user) -> dict[str, Any] | None:
    """Return stable user identity for reconciliation evidence."""

    if user is None:
        return None

    return {
        "id": str(user.pk),
        "username": user.username,
    }


def _serialize_time_entries(step) -> list[dict[str, Any]]:
    """Return historical work intervals recorded against one Step."""

    return [
        {
            "id": entry.pk,
            "user": _serialize_user(entry.user),
            "started_at": entry.started_at.isoformat(),
            "ended_at": (
                entry.ended_at.isoformat()
                if entry.ended_at
                else None
            ),
        }
        for entry in step.time_entries.all().order_by(
            "started_at",
            "pk",
        )
    ]


def _serialize_step(step) -> dict[str, Any]:
    """Return reconciliation evidence for one persisted Step."""

    return {
        "id": step.pk,
        "title": step.title,
        "description": step.description,
        "status": step.status,
        "position": step.position,
        "assigned_to": _serialize_user(step.assigned_to),
        "created_by": _serialize_user(step.created_by),
        "estimated_minutes": step.estimated_minutes,
        "estimate_confidence": step.estimate_confidence,
        "risk_level": step.risk_level,
        "risk_description": step.risk_description,
        "validation_description": step.validation_description,
        "validated_by": _serialize_user(step.validated_by),
        "validation_notes": step.validation_notes,
        "created_at": step.created_at.isoformat(),
        "updated_at": step.updated_at.isoformat(),
        "completed_at": (
            step.completed_at.isoformat()
            if step.completed_at
            else None
        ),
        "time_entries": _serialize_time_entries(step),
    }


def _serialize_phase(phase) -> dict[str, Any]:
    """Return reconciliation evidence for one persisted Phase."""

    return {
        "id": phase.pk,
        "title": phase.title,
        "description": phase.description,
        "status": phase.status,
        "position": phase.position,
        "assigned_to": _serialize_user(phase.assigned_to),
        "created_by": _serialize_user(phase.created_by),
        "created_at": phase.created_at.isoformat(),
        "updated_at": phase.updated_at.isoformat(),
        "completed_at": (
            phase.completed_at.isoformat()
            if phase.completed_at
            else None
        ),
        "steps": [
            _serialize_step(step)
            for step in phase.steps.all().order_by(
                "position",
                "pk",
            )
        ],
    }


def _serialize_initiative(initiative) -> dict[str, Any]:
    """Return reconciliation evidence for one persisted Initiative."""

    return {
        "id": initiative.pk,
        "title": initiative.title,
        "description": initiative.description,
        "status": initiative.status,
        "position": initiative.position,
        "assigned_to": _serialize_user(initiative.assigned_to),
        "created_by": _serialize_user(initiative.created_by),
        "created_at": initiative.created_at.isoformat(),
        "updated_at": initiative.updated_at.isoformat(),
        "completed_at": (
            initiative.completed_at.isoformat()
            if initiative.completed_at
            else None
        ),
        "phases": [
            _serialize_phase(phase)
            for phase in initiative.phases.all().order_by(
                "position",
                "pk",
            )
        ],
    }


def _serialize_project(project) -> dict[str, Any]:
    """Return reconciliation evidence for one persisted Project."""

    return {
        "id": project.pk,
        "title": project.title,
        "slug": project.slug,
        "description": project.description,
        "status": project.status,
        "position": project.position,
        "active": project.active,
        "assigned_to": _serialize_user(project.assigned_to),
        "created_by": _serialize_user(project.created_by),
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
        "completed_at": (
            project.completed_at.isoformat()
            if project.completed_at
            else None
        ),
        "initiatives": [
            _serialize_initiative(initiative)
            for initiative in project.initiatives.all().order_by(
                "position",
                "pk",
            )
        ],
    }


def _serialize_user_positions() -> list[dict[str, Any]]:
    """Return Planning UI navigation state as diagnostic evidence."""

    positions = (
        UserPosition.objects
        .select_related(
            "user",
            "project",
            "initiative",
            "phase",
            "step",
        )
        .order_by("user__username")
    )

    return [
        {
            "user": _serialize_user(position.user),
            "project_id": position.project_id,
            "initiative_id": position.initiative_id,
            "phase_id": position.phase_id,
            "step_id": position.step_id,
            "updated_at": position.updated_at.isoformat(),
        }
        for position in positions
    ]


def build_planning_reconciliation_snapshot() -> dict[str, Any]:
    """Return the complete forensic Planning reconciliation snapshot."""

    projects = (
        Project.objects
        .select_related(
            "assigned_to",
            "created_by",
        )
        .prefetch_related(
            "initiatives__assigned_to",
            "initiatives__created_by",
            "initiatives__phases__assigned_to",
            "initiatives__phases__created_by",
            "initiatives__phases__steps__assigned_to",
            "initiatives__phases__steps__created_by",
            "initiatives__phases__steps__validated_by",
            "initiatives__phases__steps__time_entries__user",
        )
        .order_by(
            "position",
            "pk",
        )
    )

    return {
        "snapshot_type": "planning_reconciliation",
        "projects": [
            _serialize_project(project)
            for project in projects
        ],
        "user_positions": _serialize_user_positions(),
    }

# ======================================================================
# FILE: aurora/subsystems/planning/services/reconciliation.py
# END: PLANNING_RECONCILIATION_SNAPSHOT_SERVICE
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/planning/services/reconciliation.py
# START: PLANNING_RECONCILIATION_SUMMARY_SERVICE
# ======================================================================

def _collect_status_counts(projects) -> dict[str, dict[str, int]]:
    """Return lifecycle counts for each Planning hierarchy level."""

    counts = {
        "projects": {},
        "initiatives": {},
        "phases": {},
        "steps": {},
    }

    def increment(level: str, status: str) -> None:
        counts[level][status] = (
            counts[level].get(status, 0) + 1
        )

    for project in projects:
        increment("projects", project.status)

        for initiative in project.initiatives.all():
            increment("initiatives", initiative.status)

            for phase in initiative.phases.all():
                increment("phases", phase.status)

                for step in phase.steps.all():
                    increment("steps", step.status)

    return counts


def _collect_legacy_completion_counts(
    projects,
) -> dict[str, int]:
    """
    Count legacy completed records that lack historical timestamps.

    These records are retained as historical evidence rather than emitted
    individually as reconciliation anomalies.
    """

    counts = {
        "initiatives_completed_without_timestamp": 0,
        "phases_completed_without_timestamp": 0,
        "steps_completed_without_timestamp": 0,
    }

    for project in projects:
        for initiative in project.initiatives.all():
            if (
                initiative.status == "COMPLETED"
                and initiative.completed_at is None
            ):
                counts[
                    "initiatives_completed_without_timestamp"
                ] += 1

            for phase in initiative.phases.all():
                if (
                    phase.status == "COMPLETED"
                    and phase.completed_at is None
                ):
                    counts[
                        "phases_completed_without_timestamp"
                    ] += 1

                for step in phase.steps.all():
                    if (
                        step.status == "COMPLETED"
                        and step.completed_at is None
                    ):
                        counts[
                            "steps_completed_without_timestamp"
                        ] += 1

    return counts


def _collect_execution_conflicts(
    projects,
) -> list[dict[str, Any]]:
    """Return execution-state conflicts requiring Planning reconciliation."""

    conflicts = []

    initiatives_by_user = {}

    for project in projects:
        for initiative in project.initiatives.all():
            if initiative.status != "ACTIVE":
                continue

            user = initiative.assigned_to

            if user is None:
                conflicts.append(
                    {
                        "type": "ACTIVE_INITIATIVE_WITHOUT_ASSIGNEE",
                        "project": project.slug,
                        "initiative_id": initiative.pk,
                        "initiative": initiative.title,
                    }
                )
                continue

            initiatives_by_user.setdefault(
                user.pk,
                {
                    "user": _serialize_user(user),
                    "initiatives": [],
                },
            )

            initiatives_by_user[user.pk][
                "initiatives"
            ].append(
                {
                    "project": project.slug,
                    "id": initiative.pk,
                    "title": initiative.title,
                }
            )

    for record in initiatives_by_user.values():
        if len(record["initiatives"]) <= 1:
            continue

        conflicts.append(
            {
                "type": "MULTIPLE_ACTIVE_INITIATIVES",
                "user": record["user"],
                "initiatives": record["initiatives"],
            }
        )

    return conflicts


def _collect_current_work_candidates(
    projects,
) -> list[dict[str, Any]]:
    """
    Return non-completed Initiatives requiring bootstrap reconciliation.

    These are candidates for current or future canonical Planning state.
    """

    candidates = []

    for project in projects:
        for initiative in project.initiatives.all():
            if initiative.status == "COMPLETED":
                continue

            phase_counts = {}
            step_counts = {}

            for phase in initiative.phases.all():
                phase_counts[phase.status] = (
                    phase_counts.get(phase.status, 0) + 1
                )

                for step in phase.steps.all():
                    step_counts[step.status] = (
                        step_counts.get(step.status, 0) + 1
                    )

            candidates.append(
                {
                    "project": project.slug,
                    "initiative_id": initiative.pk,
                    "title": initiative.title,
                    "status": initiative.status,
                    "assigned_to": _serialize_user(
                        initiative.assigned_to
                    ),
                    "phase_counts": phase_counts,
                    "step_counts": step_counts,
                }
            )

    return candidates


def _collect_navigation_state() -> list[dict[str, Any]]:
    """
    Return current Planning navigation separately from execution state.

    UserPosition is intentionally treated as UI navigation evidence only.
    """

    positions = (
        UserPosition.objects
        .select_related(
            "user",
            "project",
            "initiative",
            "phase",
            "step",
        )
        .order_by("user__username")
    )

    return [
        {
            "user": _serialize_user(position.user),
            "project": (
                {
                    "id": position.project.pk,
                    "slug": position.project.slug,
                    "title": position.project.title,
                    "status": position.project.status,
                }
                if position.project
                else None
            ),
            "initiative": (
                {
                    "id": position.initiative.pk,
                    "title": position.initiative.title,
                    "status": position.initiative.status,
                }
                if position.initiative
                else None
            ),
            "phase": (
                {
                    "id": position.phase.pk,
                    "title": position.phase.title,
                    "status": position.phase.status,
                }
                if position.phase
                else None
            ),
            "step": (
                {
                    "id": position.step.pk,
                    "title": position.step.title,
                    "status": position.step.status,
                }
                if position.step
                else None
            ),
            "updated_at": position.updated_at.isoformat(),
        }
        for position in positions
    ]


def build_planning_reconciliation_summary() -> dict[str, Any]:
    """
    Return compact evidence for Planning bootstrap reconciliation.

    The report distinguishes:

    - historical lifecycle evidence;
    - current execution conflicts;
    - non-completed Initiative candidates;
    - UI navigation state.

    The full forensic snapshot remains available through
    build_planning_reconciliation_snapshot().
    """

    projects = (
        Project.objects
        .select_related(
            "assigned_to",
            "created_by",
        )
        .prefetch_related(
            "initiatives__assigned_to",
            "initiatives__phases__assigned_to",
            "initiatives__phases__steps__assigned_to",
            "initiatives__phases__steps__time_entries",
        )
        .order_by(
            "position",
            "pk",
        )
    )

    project_list = list(projects)

    return {
        "snapshot_type": "planning_reconciliation_summary",
        "project_count": len(project_list),
        "status_counts": _collect_status_counts(
            project_list
        ),
        "legacy_completion_evidence": (
            _collect_legacy_completion_counts(
                project_list
            )
        ),
        "execution_conflicts": (
            _collect_execution_conflicts(
                project_list
            )
        ),
        "current_work_candidates": (
            _collect_current_work_candidates(
                project_list
            )
        ),
        "navigation_state": (
            _collect_navigation_state()
        ),
    }

# ======================================================================
# FILE: aurora/subsystems/planning/services/reconciliation.py
# END: PLANNING_RECONCILIATION_SUMMARY_SERVICE
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/planning/services/reconciliation.py
# START: PLANNING_INITIATIVE_RECONCILIATION_INSPECTION
# ======================================================================

def _serialize_step_closeout_evidence(step) -> dict[str, Any]:
    """
    Return bounded closeout evidence for one Step.

    Narrative Planning fields are surfaced for review rather than
    semantically classified by deterministic code.
    """

    try:
        document = step.document
    except ObjectDoesNotExist:
        document = None

    try:
        validation = step.validation
    except ObjectDoesNotExist:
        validation = None

    planned_files = []
    actual_files = []

    for step_file in step.files.all().order_by(
        "role",
        "file_path",
        "pk",
    ):
        record = {
            "path": step_file.file_path,
            "reason": step_file.reason,
            "recorded_by": _serialize_user(
                step_file.recorded_by
            ),
        }

        if step_file.role == "PLANNED":
            planned_files.append(record)
        elif step_file.role == "ACTUAL":
            actual_files.append(record)

    return {
        "id": step.pk,
        "title": step.title,
        "status": step.status,
        "description": step.description,
        "document": (
            {
                "technical_design": document.technical_design,
                "dependencies": document.dependencies,
                "assumptions": document.assumptions,
                "implementation_notes": document.implementation_notes,
                "discussion": document.discussion,
            }
            if document is not None
            else None
        ),
        "validation": (
            {
                "description": validation.description,
                "notes": validation.notes,
                "validated_by": _serialize_user(
                    validation.validated_by
                ),
                "validated_at": (
                    validation.validated_at.isoformat()
                    if validation.validated_at
                    else None
                ),
            }
            if validation is not None
            else None
        ),
        "planned_files": planned_files,
        "actual_files": actual_files,
    }


def _collect_step_closeout_findings(
    step,
) -> list[dict[str, Any]]:
    """
    Return only deterministic closeout findings for one Step.

    These findings identify evidence requiring review. They do not infer
    whether narrative Planning assumptions are semantically stale.
    """

    findings = []

    if step.status != "COMPLETED":
        return findings

    try:
        validation = step.validation
    except ObjectDoesNotExist:
        validation = None

    if validation is None:
        findings.append(
            {
                "type": "COMPLETED_STEP_WITHOUT_VALIDATION",
                "step_id": step.pk,
                "step": step.title,
            }
        )
    else:
        if not validation.description.strip():
            findings.append(
                {
                    "type": "COMPLETED_STEP_WITHOUT_VALIDATION_REQUIREMENT",
                    "step_id": step.pk,
                    "step": step.title,
                }
            )

        if not validation.notes.strip():
            findings.append(
                {
                    "type": "COMPLETED_STEP_WITHOUT_VALIDATION_EVIDENCE",
                    "step_id": step.pk,
                    "step": step.title,
                }
            )

        if (
            validation.validated_by_id is None
            or validation.validated_at is None
        ):
            findings.append(
                {
                    "type": "COMPLETED_STEP_WITHOUT_VALIDATION_ATTRIBUTION",
                    "step_id": step.pk,
                    "step": step.title,
                }
            )

    planned_paths = set(
        step.files.filter(
            role="PLANNED"
        ).values_list(
            "file_path",
            flat=True,
        )
    )

    actual_paths = set(
        step.files.filter(
            role="ACTUAL"
        ).values_list(
            "file_path",
            flat=True,
        )
    )

    for path in sorted(
        planned_paths - actual_paths
    ):
        findings.append(
            {
                "type": "PLANNED_FILE_NOT_OBSERVED_AS_ACTUAL",
                "step_id": step.pk,
                "step": step.title,
                "file_path": path,
            }
        )

    return findings


def build_initiative_closeout_inspection(
    initiative_id: int,
) -> dict[str, Any]:
    """
    Return bounded deterministic evidence for Initiative closeout.

    Narrative assumptions and implementation decisions are exposed for
    review. This service reports provable Planning discrepancies only and
    does not automatically classify semantic architectural staleness.
    """

    project = (
        Project.objects
        .filter(
            initiatives__pk=initiative_id,
        )
        .select_related(
            "assigned_to",
            "created_by",
        )
        .prefetch_related(
            "initiatives__assigned_to",
            "initiatives__created_by",
            "initiatives__phases__assigned_to",
            "initiatives__phases__created_by",
            "initiatives__phases__steps__assigned_to",
            "initiatives__phases__steps__created_by",
            "initiatives__phases__steps__validated_by",
            "initiatives__phases__steps__document",
            "initiatives__phases__steps__validation__validated_by",
            "initiatives__phases__steps__files__recorded_by",
        )
        .first()
    )

    if project is None:
        raise ValueError(
            f"Initiative {initiative_id} does not exist."
        )

    initiative = (
        project.initiatives
        .filter(pk=initiative_id)
        .first()
    )

    if initiative is None:
        raise ValueError(
            f"Initiative {initiative_id} does not exist."
        )

    findings = []
    phases = []

    for phase in initiative.phases.all().order_by(
        "position",
        "pk",
    ):
        steps = []

        if (
            phase.status not in {
                "COMPLETED",
                "CANCELLED",
            }
        ):
            findings.append(
                {
                    "type": "UNFINISHED_NON_CANCELLED_PHASE",
                    "phase_id": phase.pk,
                    "phase": phase.title,
                    "status": phase.status,
                }
            )

        for step in phase.steps.all().order_by(
            "position",
            "pk",
        ):
            findings.extend(
                _collect_step_closeout_findings(
                    step
                )
            )

            steps.append(
                _serialize_step_closeout_evidence(
                    step
                )
            )

        phases.append(
            {
                "id": phase.pk,
                "title": phase.title,
                "status": phase.status,
                "steps": steps,
            }
        )

    return {
        "snapshot_type": (
            "planning_initiative_closeout_inspection"
        ),
        "project": {
            "id": project.pk,
            "slug": project.slug,
            "title": project.title,
        },
        "initiative": {
            "id": initiative.pk,
            "title": initiative.title,
            "status": initiative.status,
            "phases": phases,
        },
        "findings": findings,
        "semantic_review_required": any(
            (
                step["document"] is not None
                and any(
                    (
                        step["document"]["technical_design"],
                        step["document"]["dependencies"],
                        step["document"]["assumptions"],
                        step["document"]["implementation_notes"],
                        step["document"]["discussion"],
                    )
                )
            )
            for phase in phases
            for step in phase["steps"]
        ),
    }


def build_initiative_reconciliation_snapshot(
    initiative_id: int,
    *,
    full: bool = False,
) -> dict[str, Any]:
    """Return bounded reconciliation evidence for one Initiative."""

    project = (
        Project.objects
        .filter(
            initiatives__pk=initiative_id,
        )
        .select_related(
            "assigned_to",
            "created_by",
        )
        .prefetch_related(
            "initiatives__assigned_to",
            "initiatives__created_by",
            "initiatives__phases__assigned_to",
            "initiatives__phases__created_by",
            "initiatives__phases__steps__assigned_to",
            "initiatives__phases__steps__created_by",
            "initiatives__phases__steps__validated_by",
            "initiatives__phases__steps__time_entries__user",
        )
        .first()
    )

    if project is None:
        raise ValueError(
            f"Initiative {initiative_id} does not exist."
        )

    initiative = (
        project.initiatives
        .filter(pk=initiative_id)
        .first()
    )

    if initiative is None:
        raise ValueError(
            f"Initiative {initiative_id} does not exist."
        )

    if full:
        return {
            "snapshot_type": (
                "planning_initiative_reconciliation_full"
            ),
            "project": {
                "id": project.pk,
                "slug": project.slug,
                "title": project.title,
                "status": project.status,
            },
            "initiative": _serialize_initiative(
                initiative
            ),
        }

    return {
        "snapshot_type": (
            "planning_initiative_reconciliation_summary"
        ),
        "project": {
            "id": project.pk,
            "slug": project.slug,
            "title": project.title,
        },
        "initiative": {
            "id": initiative.pk,
            "title": initiative.title,
            "status": initiative.status,
            "assigned_to": _serialize_user(
                initiative.assigned_to
            ),
            "phases": [
                {
                    "id": phase.pk,
                    "title": phase.title,
                    "status": phase.status,
                    "assigned_to": _serialize_user(
                        phase.assigned_to
                    ),
                    "steps": [
                        {
                            "id": step.pk,
                            "title": step.title,
                            "status": step.status,
                        }
                        for step in phase.steps.all().order_by(
                            "position",
                            "pk",
                        )
                    ],
                }
                for phase in initiative.phases.all().order_by(
                    "position",
                    "pk",
                )
            ],
        },
    }


# ======================================================================
# FILE: aurora/subsystems/planning/services/reconciliation.py
# END: PLANNING_INITIATIVE_RECONCILIATION_INSPECTION
# ======================================================================