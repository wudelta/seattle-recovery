# ======================================================================
# FILE: aurora/migrations/0014_migrate_step_validation_data.py
# START: MIGRATE_STEP_VALIDATION_DATA
# ======================================================================
from django.db import migrations


def migrate_step_validation_forward(
    apps,
    schema_editor,
):
    Step = apps.get_model(
        "aurora",
        "Step",
    )

    StepValidation = apps.get_model(
        "aurora",
        "StepValidation",
    )

    steps = Step.objects.exclude(
        validation_description="",
        validation_notes="",
        validated_by__isnull=True,
    )

    for step in steps.iterator():
        StepValidation.objects.update_or_create(
            step_id=step.id,
            defaults={
                "description": (
                    step.validation_description
                    or ""
                ),
                "notes": (
                    step.validation_notes
                    or ""
                ),
                "validated_by_id": (
                    step.validated_by_id
                ),
            },
        )


def migrate_step_validation_reverse(
    apps,
    schema_editor,
):
    Step = apps.get_model(
        "aurora",
        "Step",
    )

    StepValidation = apps.get_model(
        "aurora",
        "StepValidation",
    )

    for validation in (
        StepValidation.objects.all().iterator()
    ):
        Step.objects.filter(
            id=validation.step_id
        ).update(
            validation_description=(
                validation.description
                or ""
            ),
            validation_notes=(
                validation.notes
                or ""
            ),
            validated_by_id=(
                validation.validated_by_id
            ),
        )

    StepValidation.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        (
            "aurora",
            "0013_stepdocument_stepvalidation_stepfile",
        ),
    ]

    operations = [
        migrations.RunPython(
            migrate_step_validation_forward,
            migrate_step_validation_reverse,
        ),
    ]
# ======================================================================
# END: MIGRATE_STEP_VALIDATION_DATA
# ======================================================================