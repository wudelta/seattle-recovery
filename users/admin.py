# ======================================================================
# FILE: users/admin.py (PATCH 1 OF 1)
# START: CUSTOM_UUID_USER_ADMIN
# ======================================================================
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Provides complete administrative CRUD for UUID-backed users."""

    model = CustomUser

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "id",
    )

    ordering = ("username",)
    filter_horizontal = ("groups", "user_permissions")

    readonly_fields = (
        "id",
        "last_login",
        "date_joined",
    )

    fieldsets = (
        (
            "User Identity",
            {
                "fields": (
                    "id",
                    "username",
                    "password",
                ),
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                ),
            },
        ),
        (
            "Authorization",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Account History",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            "Create User",
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )
# ======================================================================
# END: CUSTOM_UUID_USER_ADMIN (PATCH 1 OF 1)
# ======================================================================