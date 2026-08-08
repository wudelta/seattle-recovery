# ======================================================================
# FILE: aurora/subsystems/component_registry/services/registry.py
# START: REGISTRY_CORE_IMPORTS_AND_SYSTEM_CONSTRAINTS
# ======================================================================
from django.contrib.auth import get_user_model

from aurora.models import ComponentRegistry


UserModel = get_user_model()

BANNED_DIRECTORIES = ["venv", ".venv", "site-packages", ".git"]
# ======================================================================
# END: REGISTRY_CORE_IMPORTS_AND_SYSTEM_CONSTRAINTS
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/component_registry/services/registry.py
# START: SANDBOX_GUARDRAILS_AND_EXPLICIT_POSTGRES_PROVISIONING
# ======================================================================
def register_new_component(
    file_path: str,
    name: str,
    visibility: str,
    user_instance: UserModel,
    persona: str = "COMPILER_MODULE",
    description: str = "",
):
    """
    Register a new ComponentRegistry entry.

    This function is intentionally limited to PostgreSQL registration.
    Graph synchronization is an explicit responsibility of the caller.
    """
    path_parts = file_path.replace("\\", "/").split("/")

    if any(banned in path_parts for banned in BANNED_DIRECTORIES):
        raise PermissionError(
            "FORGE GUARDRAIL VIOLATION: "
            f"Execution blocked for environment path: {file_path}"
        )

    clean_visibility = visibility.strip().upper()

    if clean_visibility not in ["PUBLIC", "PRIVATE"]:
        clean_visibility = "PRIVATE"

    return ComponentRegistry.objects.create(
        file_path=file_path,
        name=name,
        persona=persona,
        status="ACTIVE",
        visibility=clean_visibility,
        locked=False,
        created_by=user_instance,
        description=description,
        description_audiences=["developers"],
    )
# ======================================================================
# END: SANDBOX_GUARDRAILS_AND_EXPLICIT_POSTGRES_PROVISIONING
# ======================================================================