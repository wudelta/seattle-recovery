# ======================================================================
# FILE: aurora/api/handlers/base.py (PATCH 1 OF 1)
# START: ABSTRACT_COMMAND_BASE_INTERFACE
# ======================================================================
from abc import ABC, abstractmethod
from django.http import JsonResponse

class BaseCommandHandler(ABC):
    """
    Abstract interface layer enforcing unified command parsing and execution structures 
    across all blueprint automation sub-modules.
    """

    @abstractmethod
    def execute(self, request, parts: list, raw_cmd: str) -> JsonResponse:
        """
        Executes the business logic of a sub-command.
        
        Args:
            request: The active HttpRequest instance.
            parts: Tokenized list of strings representing the parsed space-separated arguments.
            raw_cmd: The full pristine string layout captured by the entry router.
            
        Returns:
            JsonResponse payload package mapping back to the interface terminal hook.
        """
        pass
# ======================================================================
# END: ABSTRACT_COMMAND_BASE_INTERFACE (PATCH 1 OF 1)
# ======================================================================
