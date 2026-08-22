# ======================================================================
# FILE: aurora/subsystems/engineering_session/api/serializers.py
# START: ENGINEERING_SESSION_API_SERIALIZERS
# ======================================================================

from dataclasses import asdict


def serialize_session(session):
    """Return stable API data for one EngineeringSession."""

    if session is None:
        return None

    return {
        "id": session.id,
        "started_at": session.started_at.isoformat(),
        "ended_at": (
            session.ended_at.isoformat()
            if session.ended_at
            else None
        ),
    }


def serialize_time_entry(time_entry):
    """Return stable API data for one Planning TimeEntry."""

    if time_entry is None:
        return None

    return {
        "id": time_entry.id,
        "step_id": time_entry.step_id,
        "step": time_entry.step.title,
        "started_at": time_entry.started_at.isoformat(),
        "ended_at": (
            time_entry.ended_at.isoformat()
            if time_entry.ended_at
            else None
        ),
    }


def serialize_delta_note(note):
    """Return stable API data for one Delta Note."""

    if note is None:
        return None

    return {
        "id": note.pk,
        "text": note.text,
        "created_at": note.created_at.isoformat(),
        "updated_at": note.updated_at.isoformat(),
    }


def serialize_planning_proposal(proposal):
    """Return stable API data for one validated Planning proposal."""

    return {
        "note_id": proposal.note_id,
        "note_text": proposal.note_text,
        "project_slug": proposal.project_slug,
        "document": proposal.document,
        "validation": asdict(
            proposal.validation
        ),
    }


def serialize_planning_application(application):
    """Return stable API data for an applied Delta Note Planning proposal."""

    return {
        "note_id": application.note_id,
        "project_slug": application.project_slug,
        "validation": asdict(
            application.validation
        ),
        "application": asdict(
            application.application
        ),
        "note_resolved": application.note_resolved,
    }


def serialize_grouped_planning_application(application):
    """Return stable API data for one grouped Delta Note handoff."""

    return {
        "note_ids": list(
            application.note_ids
        ),
        "project_slug": application.project_slug,
        "initiative_id": application.initiative_id,
        "initiative_title": application.initiative_title,
        "validation": asdict(
            application.validation
        ),
        "application": asdict(
            application.application
        ),
        "provenance_links_created": (
            application.provenance_links_created
        ),
        "notes_resolved": application.notes_resolved,
    }


def serialize_registry_maintenance(report):
    """Return stable deterministic maintenance results for the browser."""

    return {
        "counts": report.counts,
        "review": list(report.review),
        "failures": list(report.failures),
    }


def serialize_registry_enrichment(report):
    """Return stable Component Registry enrichment results for the browser."""

    return {
        "candidates": len(report.get("candidates", [])),
        "completed": len(report.get("completed", [])),
        "skipped": len(report.get("skipped", [])),
        "failures": len(report.get("failures", [])),
        "stopped": bool(report.get("stopped", False)),
        "last_completed": report.get("last_completed"),
        "failure_point": report.get("failure_point"),
        "restart_from": report.get("restart_from"),
        "remaining": report.get("remaining", 0),
    }


# ======================================================================
# END: ENGINEERING_SESSION_API_SERIALIZERS
# ======================================================================
