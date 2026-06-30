# ======================================================================
# FILE: users/models.py (PATCH 1 OF 1)
# START: CUSTOM_UUID_USER_MODEL_DECLARATION
# ======================================================================
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Overwrite the standard autoincrement ID with an immutable UUID primary key
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    class Meta:
        db_table = 'auth_user'  # Enforce matching table naming syntax
# ======================================================================
# END: CUSTOM_UUID_USER_MODEL_DECLARATION (PATCH 1 OF 1)
# ======================================================================
