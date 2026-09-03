# One-time Step 366 reconciliation of the temporary Engineering Discovery ledger.

from django.conf import settings
from django.db import migrations


def reconcile_pending_findings(apps, schema_editor):
    EngineeringFinding = apps.get_model("aurora", "EngineeringFinding")
    Step = apps.get_model("aurora", "Step")
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))

    origin_step = Step.objects.select_related("completed_by").get(pk=328)
    discovered_by = origin_step.completed_by
    if discovered_by is None:
        discovered_by = User.objects.filter(is_superuser=True).order_by("pk").first()
    if discovered_by is None:
        raise RuntimeError(
            "Step 366 reconciliation could not determine the historical discoverer."
        )

    resolved_step_361 = Step.objects.get(pk=361)
    resolved_step_363 = Step.objects.get(pk=363)

    findings = [
        {
            "originating_step": origin_step,
            "category": "BOUNDARY_VIOLATION",
            "blocking_classification": "NON_BLOCKING",
            "resolution_state": "RESOLVED",
            "observed_condition": (
                "Wu Chat independently queried Planning Initiative, Phase, and "
                "Step models to reconstruct lifecycle-authoritative execution state."
            ),
            "evidence": (
                "ExecutionContextResolver.build() reconstructed ACTIVE Planning "
                "state instead of consuming a Planning-owned execution boundary."
            ),
            "resolution_evidence": (
                "Step 361 routed Wu Chat through Planning-owned execution state and "
                "validated the same Initiative/Phase/Step without direct Planning ORM "
                "reconstruction."
            ),
            "resolved_at": resolved_step_361.completed_at,
        },
        {
            "originating_step": origin_step,
            "category": "NEEDED_SOLUTION",
            "blocking_classification": "NON_BLOCKING",
            "resolution_state": "RESOLVED",
            "observed_condition": (
                "Structured Step actual-file evidence was not maintained "
                "deterministically during engineering work."
            ),
            "evidence": (
                "Repository files were created or modified while actual-file paths "
                "were reconstructed manually in free-form Step validation notes."
            ),
            "resolution_evidence": (
                "Step 363 integrated Component Registry reconciliation with Planning "
                "StepFile ACTUAL evidence and registry refresh during Step completion."
            ),
            "resolved_at": resolved_step_363.completed_at,
        },
        {
            "originating_step": None,
            "category": "NEEDED_SOLUTION",
            "blocking_classification": "NON_BLOCKING",
            "resolution_state": "UNRESOLVED",
            "observed_condition": (
                "The Between-Initiative Gap did not define the repository mutation "
                "boundary between Planning-state reconciliation and permanent "
                "repository implementation work."
            ),
            "evidence": (
                "Reconciliation required allowing persisted Planning-state maintenance "
                "and temporary non-authoritative artifacts while prohibiting permanent "
                "repository mutation without an authoritative Initiative, Phase, and Step."
            ),
            "resolution_evidence": "",
            "resolved_at": None,
        },
        {
            "originating_step": None,
            "category": "BROKEN_HANSEL_TRAIL",
            "blocking_classification": "NON_BLOCKING",
            "resolution_state": "UNRESOLVED",
            "observed_condition": (
                "The Delta Notes Hansel catalogue did not route workers to the existing "
                "cross-subsystem Planning workflow for processing Delta Notes."
            ),
            "evidence": (
                "The supported coordination path had to be found by targeted repository "
                "search instead of through the owning Delta Notes Hansel catalogue."
            ),
            "resolution_evidence": "",
            "resolved_at": None,
        },
        {
            "originating_step": None,
            "category": "NEEDED_SOLUTION",
            "blocking_classification": "NON_BLOCKING",
            "resolution_state": "UNRESOLVED",
            "observed_condition": (
                "The backend supported atomic grouped Delta Notes to Planning application, "
                "but the normal Wu workflow exposed only the older single-note path."
            ),
            "evidence": (
                "apply_delta_notes_to_new_initiative() supported grouped provenance and "
                "atomic resolution while the Wu workflow proposed and applied one active "
                "note at a time."
            ),
            "resolution_evidence": "",
            "resolved_at": None,
        },
        {
            "originating_step": None,
            "category": "VALIDATION_GAP",
            "blocking_classification": "BLOCKING",
            "resolution_state": "UNRESOLVED",
            "observed_condition": (
                "Resolve / No Action could remove an unresolved Delta Note from actionable "
                "work without durable disposition evidence or another established outcome."
            ),
            "evidence": (
                "The exercised resolution path marked a note processed without requiring a "
                "reason, Planning handoff, resolution evidence, or reversible disposition; "
                "manual verification required recreating the note."
            ),
            "resolution_evidence": "",
            "resolved_at": None,
        },
    ]

    for item in findings:
        defaults = {
            "originating_step": item["originating_step"],
            "discovered_by": discovered_by,
            "blocking_classification": item["blocking_classification"],
            "resolution_state": item["resolution_state"],
            "evidence": item["evidence"],
            "steps_to_reproduce": "",
            "resolution_evidence": item["resolution_evidence"],
            "resolved_at": item["resolved_at"],
        }
        EngineeringFinding.objects.get_or_create(
            category=item["category"],
            observed_condition=item["observed_condition"],
            defaults=defaults,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("aurora", "0025_alter_engineeringfinding_originating_step"),
    ]

    operations = [
        migrations.RunPython(
            reconcile_pending_findings,
            migrations.RunPython.noop,
        ),
    ]
