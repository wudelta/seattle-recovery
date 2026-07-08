# ======================================================================
# FILE: aurora/agents.py (PATCH 1 OF 2)
# START: PROVIDER_INITIALIZATION_&_DIRECTIVE_LOOKUP
# ======================================================================

from django.core.exceptions import ObjectDoesNotExist

from core_logic.ai.registry import registry
from .models import DeltaDirectives

# ======================================================================
# END: PROVIDER_INITIALIZATION_&_DIRECTIVE_LOOKUP (PATCH 1 OF 2)
# ======================================================================

# ======================================================================
# FILE: aurora/agents.py (PATCH 2 OF 2)
# START: DATABASE-DRIVEN_AI_REQUEST_DISPATCH
# ======================================================================

provider = registry.get(provider_name)

# ======================================================================
# END: DATABASE-DRIVEN_AI_REQUEST_DISPATCH (PATCH 2 OF 2)
# ======================================================================