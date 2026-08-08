# ======================================================================
# FILE: aurora/subsystems/delta_directives/models.py
# START: DIRECTIVES_SCHEMA
# ======================================================================

import uuid

from django.conf import settings
from django.db import models


class DeltaDirectives(models.Model):
    """
    Standalone configuration engine storing system instructions, prompts, and
    model processing boundaries for your AI minion fleet.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    directive_name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
    )
    instructions = models.TextField()
    constraints = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Delta Directive Profile"
        verbose_name_plural = "Delta Directive Profiles"

    def __str__(self):
        return f"{self.directive_name} [Active: {self.is_active}]"


# ======================================================================
# END: DIRECTIVES_SCHEMA
# ======================================================================