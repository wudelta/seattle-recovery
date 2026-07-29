# ======================================================================
# FILE: aurora/subsystems/planning/io/markdown_exporter.py
# START: PLANNING_MARKDOWN_EXPORTER
# ======================================================================
from aurora.models import Project
from aurora.subsystems.planning.io.exceptions import PlanningExportError


def export_planning_markdown(project: Project) -> str:
    """Render one persisted Project hierarchy as readable Markdown."""

    if project is None or not project.pk:
        raise PlanningExportError(
            "A persisted Project is required for Markdown export."
        )

    lines = [
        f"# {project.title}",
        "",
        project.description.strip(),
        "",
        "## Project Status",
        "",
        f"- **Slug:** `{project.slug}`",
        f"- **Status:** {project.get_status_display()}",
        f"- **Position:** {project.position}",
        f"- **Active:** {'Yes' if project.active else 'No'}",
        "",
    ]

    initiatives = project.initiatives.order_by("position", "pk")

    for initiative in initiatives:
        lines.extend(
            [
                f"## Initiative {initiative.position}: {initiative.title}",
                "",
                initiative.description.strip(),
                "",
                f"**Status:** {initiative.get_status_display()}",
                "",
            ]
        )

        phases = initiative.phases.order_by("position", "pk")

        for phase in phases:
            lines.extend(
                [
                    f"### Phase {phase.position}: {phase.title}",
                    "",
                    phase.description.strip(),
                    "",
                    f"**Status:** {phase.get_status_display()}",
                    "",
                ]
            )

            steps = phase.steps.order_by("position", "pk")

            for step in steps:
                lines.extend(_render_step(step))

    return "\n".join(lines).rstrip() + "\n"


def _render_step(step) -> list[str]:
    lines = [
        f"#### Step {step.position}: {step.title}",
        "",
        step.description.strip(),
        "",
        f"- **Status:** {step.get_status_display()}",
        f"- **Risk:** {step.get_risk_level_display()}",
    ]

    if step.estimated_minutes is not None:
        lines.append(
            f"- **Estimated effort:** {step.estimated_minutes} minutes"
        )

    if step.estimate_confidence:
        lines.append(
            f"- **Estimate confidence:** "
            f"{step.get_estimate_confidence_display()}"
        )

    if step.risk_description.strip():
        lines.extend(
            [
                "",
                "**Risk details**",
                "",
                step.risk_description.strip(),
            ]
        )

    if step.validation_description.strip():
        lines.extend(
            [
                "",
                "**Validation**",
                "",
                step.validation_description.strip(),
            ]
        )

    if step.validation_notes.strip():
        lines.extend(
            [
                "",
                "**Validation notes**",
                "",
                step.validation_notes.strip(),
            ]
        )

    lines.append("")

    return lines
# ======================================================================
# END: PLANNING_MARKDOWN_EXPORTER
# ======================================================================