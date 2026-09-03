# Generated for Step 366: optional Planning provenance for Engineering Findings.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("aurora", "0024_engineeringfinding_remedial_phase"),
    ]

    operations = [
        migrations.AlterField(
            model_name="engineeringfinding",
            name="originating_step",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "Lifecycle-authoritative Planning Step active when the finding "
                    "was discovered, when one truthfully existed."
                ),
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="engineering_findings",
                to="aurora.step",
            ),
        ),
    ]
