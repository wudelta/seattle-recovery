# ======================================================================
# FILE: aurora/migrations/0009_project_step_risk_and_initiative_project.py (PATCH 1 OF 1)
# START: PROJECT_AND_PLANNING_RISK_SCHEMA
# ======================================================================
from django.db import migrations, models
import django.db.models.deletion


def reset_planning_data_and_create_projects(apps, schema_editor):
    """Discards development planning data and establishes initial projects."""
    Step = apps.get_model("aurora", "Step")
    Phase = apps.get_model("aurora", "Phase")
    Initiative = apps.get_model("aurora", "Initiative")
    Project = apps.get_model("aurora", "Project")

    Step.objects.all().delete()
    Phase.objects.all().delete()
    Initiative.objects.all().delete()

    Project.objects.get_or_create(
        slug="aurora",
        defaults={
            "title": "Aurora",
            "description": "Aurora engineering and platform development.",
            "position": 0,
            "active": True,
        },
    )

    Project.objects.get_or_create(
        slug="hopehub",
        defaults={
            "title": "HopeHub",
            "description": "HopeHub application planning and development.",
            "position": 1,
            "active": True,
        },
    )


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ("aurora", "0008_remove_step_completed_step_estimate_confidence_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                (
                    "slug",
                    models.SlugField(
                        max_length=255,
                        unique=True,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                (
                    "color",
                    models.CharField(
                        blank=True,
                        help_text=(
                            "Optional presentation color for planning interfaces."
                        ),
                        max_length=32,
                    ),
                ),
                (
                    "icon",
                    models.CharField(
                        blank=True,
                        help_text=(
                            "Optional icon identifier for planning interfaces."
                        ),
                        max_length=64,
                    ),
                ),
                ("position", models.PositiveIntegerField(default=0)),
                (
                    "active",
                    models.BooleanField(
                        db_index=True,
                        default=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["position", "title"],
            },
        ),
        migrations.AddField(
            model_name="initiative",
            name="project",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="initiatives",
                to="aurora.project",
            ),
        ),
        migrations.AddField(
            model_name="step",
            name="risk_description",
            field=models.TextField(
                blank=True,
                help_text=(
                    "Reason this step carries implementation or operational risk."
                ),
            ),
        ),
        migrations.AddField(
            model_name="step",
            name="risk_level",
            field=models.CharField(
                choices=[
                    ("LOW", "Low"),
                    ("MEDIUM", "Medium"),
                    ("HIGH", "High"),
                    ("CRITICAL", "Critical"),
                ],
                db_index=True,
                default="LOW",
                help_text="Potential impact if this implementation step fails.",
                max_length=10,
            ),
        ),
        migrations.RunPython(
            reset_planning_data_and_create_projects,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="initiative",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="initiatives",
                to="aurora.project",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="initiative",
            unique_together={
                ("project", "position"),
            },
        ),
    ]
# ======================================================================
# END: PROJECT_AND_PLANNING_RISK_SCHEMA (PATCH 1 OF 1)
# ======================================================================