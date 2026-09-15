# Generated for Decision Engine intake disposition authority.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("aurora", "0028_decisionenginework"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DecisionEngineIntakeDisposition",
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
                (
                    "source_type",
                    models.CharField(
                        choices=[
                            ("DELTA_NOTE", "Delta Note"),
                            ("ENGINEERING_FINDING", "Engineering Finding"),
                        ],
                        db_index=True,
                        max_length=32,
                    ),
                ),
                ("source_id", models.PositiveBigIntegerField()),
                (
                    "disposition",
                    models.CharField(
                        choices=[
                            ("OPEN", "Open"),
                            ("DEFERRED", "Deferred"),
                            ("NEEDS_MITIGATION", "Needs Mitigation"),
                            ("WORK_COMMITTED", "Work Committed"),
                            ("REJECTED", "Rejected"),
                            ("WITHDRAWN", "Withdrawn"),
                        ],
                        db_index=True,
                        max_length=32,
                    ),
                ),
                ("authorized_at", models.DateTimeField(auto_now_add=True)),
                ("reason", models.TextField()),
                (
                    "authorized_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="decision_engine_dispositions_authorized",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "delta_note",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="decision_engine_dispositions",
                        to="aurora.deltanotesentry",
                    ),
                ),
                (
                    "engineering_finding",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="decision_engine_dispositions",
                        to="aurora.engineeringfinding",
                    ),
                ),
                (
                    "resolving_work",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="intake_dispositions",
                        to="aurora.decisionenginework",
                    ),
                ),
            ],
            options={"ordering": ["authorized_at", "pk"]},
        ),
        migrations.AddConstraint(
            model_name="decisionengineintakedisposition",
            constraint=models.UniqueConstraint(
                fields=("source_type", "source_id"),
                name="uniq_decision_engine_source_disposition",
            ),
        ),
        migrations.AddConstraint(
            model_name="decisionengineintakedisposition",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(
                        disposition="WORK_COMMITTED",
                        resolving_work__isnull=False,
                    )
                    | (
                        ~models.Q(disposition="WORK_COMMITTED")
                        & models.Q(resolving_work__isnull=True)
                    )
                ),
                name="decision_engine_resolving_work_matches_disposition",
            ),
        ),
    ]
