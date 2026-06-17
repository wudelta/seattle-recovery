# ======================================================================
# AURORA FORGE ENGINE: AI SLASH COMMAND IMPLEMENTATION ARCHITECTURE
# ======================================================================

To implement a new slash command (e.g., `/bind`, `/page`, `/api`) in the Seattle Recovery ecosystem without causing architectural regressions, the AI must strictly execute the following decoupled 5-step workflow.

## STEP 1: Implement the Standalone Handler Class
Create a dedicated file inside `aurora/api/handlers/[command_name].py`. 
* Must inherit from `BaseCommandHandler` found in `aurora/api/handlers/base.py`.
* Must implement the concrete `execute(self, request, parts: list, raw_cmd: str) -> JsonResponse` method.
* Must isolate log capture streams via the thread-safe `TelemetryLogger` utility.

```python
# FILE: aurora/api/handlers/example.py
from django.http import JsonResponse
from aurora.api.handlers.base import BaseCommandHandler
from aurora.utils.telemetry import TelemetryLogger

class ExampleCommandHandler(BaseCommandHandler):
    def execute(self, request, parts: list, raw_cmd: str) -> JsonResponse:
        if len(parts) < 2:
            return JsonResponse({"status": "success", "minion_log": "Syntax error"})
            
        TelemetryLogger.emit("[EXAMPLE] Initiating task loop...\n")
        # Functional business logic goes here
        logs = TelemetryLogger.flush()
        return JsonResponse({"status": "success", "telemetry_stream": logs})
```

## STEP 2: Register the Handler with the Central Command Matrix Map
Open `aurora/api/blueprint.py` and mount the new command trigger token to the structural command map.

```python
# FILE: aurora/api/blueprint.py
from aurora.api.handlers.example import ExampleCommandHandler

COMMAND_MAP = {
    "/page": PageCommandHandler(),
    "/api": ApiCommandHandler(),
    "/destroy": DestroyCommandHandler(),
    "/bind": BindCommandHandler(),
    "/example": ExampleCommandHandler(), # Add trigger token pointer hook here
}
```

## STEP 3: Route Content Signals via Console Views
Open `aurora/api/endpoints.py` and append the matching console gateway view function to funnel commands typed from the console.

```python
# FILE: aurora/api/endpoints.py
@csrf_exempt
@login_required
def example_command_endpoint(request):
    raw_cmd = request.POST.get("blueprint", "").strip()
    parts = [p.strip() for p in raw_cmd.split(" ") if p.strip()]
    from aurora.api.handlers.example import ExampleCommandHandler
    return ExampleCommandHandler().execute(request, parts, raw_cmd)
```

## STEP 4: Expose Gateway View Vectors to URL Routing Layers
Update `aurora/api/api_commands.py` to add your view to the module export list configuration matrix `__all__`.

```python
# FILE: aurora/api/api_commands.py
from aurora.api.endpoints import example_command_endpoint
__all__ = [..., 'example_command_endpoint']
```

## STEP 5: Twin-Track Testing Mandate (TDD)
Write standalone, under-100-line test suites in `aurora/tests/test_[command_name]_command.py`.
* Ensure graph sandbox isolation by flushing the active Neo4j port mapping inside `setUp()` and `tearDown()` using:
  `neomodel_db.cypher_query("MATCH (n) DETACH DELETE n")`
* Assert the HTTP return status code, the validation data dictionary arrays, and confirm that file system modifications don't leak outside the sandboxed `hopehub_sandbox` tree.
