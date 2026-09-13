# ======================================================================
# FILE: aurora/management/commands/provision_aurora_roles.py
# START: PROVISION_AURORA_ROLES_COMMAND
# ======================================================================

from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from aurora.access.policy import (
    AURORA_DEVELOPER_GROUP,
    AURORA_INITIATIVE_OWNER_GROUP,
    AURORA_PHASE_OWNER_GROUP,
    AURORA_STEP_OWNER_GROUP,
)
from aurora.subsystems.planning.models.hierarchy import (
    Initiative,
    Phase,
    Step,
)


User = get_user_model()


@dataclass(frozen=True)
class RoleDefinition:
    group_name: str
    model: type
    permission_codename: str
    validation_username: str


ROLE_DEFINITIONS = (
    RoleDefinition(
        group_name=AURORA_INITIATIVE_OWNER_GROUP,
        model=Initiative,
        permission_codename="change_initiative",
        validation_username="initiativeowner_test",
    ),
    RoleDefinition(
        group_name=AURORA_PHASE_OWNER_GROUP,
        model=Phase,
        permission_codename="change_phase",
        validation_username="phaseowner_test",
    ),
    RoleDefinition(
        group_name=AURORA_STEP_OWNER_GROUP,
        model=Step,
        permission_codename="change_step",
        validation_username="stepowner_test",
    ),
)


class Command(BaseCommand):
    """Provision Aurora's initial Django role-capability groups."""

    help = (
        "Provision Aurora ownership groups and their exact Django model "
        "permissions. Dry-run is the default; use --apply to mutate the "
        "database."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply the provisioning changes.",
        )
        parser.add_argument(
            "--include-validation-users",
            action="store_true",
            help=(
                "Also provision dedicated validation users for the three "
                "ownership groups."
            ),
        )

    def handle(self, *args, **options) -> None:
        apply_changes = options["apply"]
        include_validation_users = options["include_validation_users"]

        permissions = self._resolve_permissions()

        if not apply_changes:
            self._write_plan(
                permissions=permissions,
                include_validation_users=include_validation_users,
            )
            return

        with transaction.atomic():
            groups = self._provision_groups(
                permissions=permissions,
            )

            if include_validation_users:
                self._provision_validation_users(groups=groups)

        self.stdout.write(
            self.style.SUCCESS(
                "APPLIED: Aurora role capability foundation provisioned."
            )
        )

    def _resolve_permissions(self) -> dict[str, Permission]:
        resolved: dict[str, Permission] = {}

        for definition in ROLE_DEFINITIONS:
            content_type = ContentType.objects.get_for_model(
                definition.model
            )

            try:
                permission = Permission.objects.get(
                    content_type=content_type,
                    codename=definition.permission_codename,
                )
            except Permission.DoesNotExist as exc:
                raise CommandError(
                    "Required Django permission does not exist: "
                    f"{content_type.app_label}."
                    f"{definition.permission_codename}"
                ) from exc

            resolved[definition.group_name] = permission

        return resolved

    def _write_plan(
        self,
        *,
        permissions: dict[str, Permission],
        include_validation_users: bool,
    ) -> None:
        self.stdout.write("DRY RUN: no database changes will be made.")

        for definition in ROLE_DEFINITIONS:
            permission = permissions[definition.group_name]

            self.stdout.write(
                f"GROUP: {definition.group_name}"
            )
            self.stdout.write(
                "  PERMISSION: "
                f"{permission.content_type.app_label}."
                f"{permission.codename}"
            )

            if include_validation_users:
                self.stdout.write(
                    f"  VALIDATION USER: "
                    f"{definition.validation_username}"
                )
                self.stdout.write(
                    "  USER GROUPS: "
                    f"{AURORA_DEVELOPER_GROUP}, "
                    f"{definition.group_name}"
                )

        if not include_validation_users:
            self.stdout.write(
                "VALIDATION USERS: not requested"
            )

        self.stdout.write(
            "Use --apply to provision these records."
        )

    def _provision_groups(
        self,
        *,
        permissions: dict[str, Permission],
    ) -> dict[str, Group]:
        groups: dict[str, Group] = {}

        for definition in ROLE_DEFINITIONS:
            group, _ = Group.objects.get_or_create(
                name=definition.group_name
            )

            group.permissions.set(
                [permissions[definition.group_name]]
            )

            groups[definition.group_name] = group

            permission = permissions[definition.group_name]

            self.stdout.write(
                "GROUP: "
                f"{definition.group_name} -> "
                f"{permission.content_type.app_label}."
                f"{permission.codename}"
            )

        return groups

    def _provision_validation_users(
        self,
        *,
        groups: dict[str, Group],
    ) -> None:
        developers_group, _ = Group.objects.get_or_create(
            name=AURORA_DEVELOPER_GROUP
        )

        for definition in ROLE_DEFINITIONS:
            user, created = User.objects.get_or_create(
                username=definition.validation_username
            )

            user.set_unusable_password()
            user.is_staff = False
            user.is_superuser = False
            user.is_active = True
            user.save(
                update_fields=[
                    "password",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                ]
            )

            user.groups.set(
                [
                    developers_group,
                    groups[definition.group_name],
                ]
            )

            state = "CREATED" if created else "UPDATED"

            self.stdout.write(
                f"{state} VALIDATION USER: "
                f"{definition.validation_username} -> "
                f"{AURORA_DEVELOPER_GROUP}, "
                f"{definition.group_name}"
            )


# ======================================================================
# END: PROVISION_AURORA_ROLES_COMMAND
# ======================================================================