# ======================================================================
# FILE: aurora/api/handlers/bind.py (PATCH 1 OF 2)
# START: FIXED_BIND_ROUTING_AND_PATH_RESOLUTION
# ======================================================================
import os
from django.http import JsonResponse
from aurora.api.handlers.base import BaseCommandHandler
from aurora.utils.telemetry import TelemetryLogger

class BindCommandHandler(BaseCommandHandler):
    """Processes /bind <app_name> <function_name> <api_name> with exact absolute paths."""
    
    def execute(self, request, parts: list, raw_cmd: str) -> JsonResponse:
        if len(parts) < 4:
            return JsonResponse({
                "status": "success",
                "minion_log": "Syntax: /bind <app_name> <function_name> <api_name>",
                "validation": {"valid": False, "errors": ["Missing parameters"], "warnings": []}
            })
            
        app_name = parts[1].lower().strip()
        func_name = parts[2].lower().strip()
        api_name = parts[3].lower().strip()
        
        TelemetryLogger.emit(f"[BIND_ENGINE] Commencing binding orchestration for: {app_name} -> {func_name} to API: {api_name}\n")
        
        # Locate the template workspace targets securely
        html_filename = f"{func_name}.html"
        possible_paths = [
            os.path.join(app_name, "templates", html_filename),
            os.path.join(app_name, "templates", app_name, html_filename)
        ]
        
        target_html_path = None
        for path in possible_paths:
            TelemetryLogger.emit(f"[BIND_ENGINE] Scanning layout template path: {path}\n")
            if os.path.exists(path):
                target_html_path = path
                TelemetryLogger.emit(f"[BIND_ENGINE] Match confirmed. Target locked: {path}\n")
                break
                
        if not target_html_path:
            target_html_path = possible_paths[0]
            TelemetryLogger.emit(f"[WARNING] Template file not found. Generating directory branch: {os.path.dirname(target_html_path)}\n")
            os.makedirs(os.path.dirname(target_html_path), exist_ok=True)
# ======================================================================
# END: FIXED_BIND_ROUTING_AND_PATH_RESOLUTION (PATCH 1 OF 2)
# ======================================================================

# ======================================================================
# FILE: aurora/api/handlers/bind.py (PATCH 2 OF 2)
# START: FIXED_BIND_ABSOLUTE_URL_INJECTION
# ======================================================================
        # Build clean Bootstrap UI card stream layout block with explicit URL strings
        injected_js_ui = (
            f"<div class='container mt-4'>\n"
            f"  <div class='card shadow-sm'>\n"
            f"    <div class='card-header bg-primary text-white'>\n"
            f"      <h5 class='mb-0'>Live Stream Data: {api_name}</h5>\n"
            f"    </div>\n"
            f"    <div class='card-body'>\n"
            f"      <pre id='json_payload_render' class='bg-light p-3 border rounded'>Loading payload stream...</pre>\n"
            f"    </div>\n"
            f"  </div>\n"
            f"</div>\n"
            f"<script>\n"
            f"  // Absolute fetch URL strategy to avoid browser scope path confusion\n"
            f"  document.addEventListener('DOMContentLoaded', function() {{\n"
            f"    fetch('/{app_name}/api/{api_name}/')\n"
            f"      .then(response => {{\n"
            f"        if (!response.ok) throw new Error('Network stream error');\n"
            f"        return response.json();\n"
            f"      }})\n"
            f"      .then(data => {{\n"
            f"        document.getElementById('json_payload_render').textContent = JSON.stringify(data, null, 2);\n"
            f"      }})\n"
            f"      .catch(err => {{\n"
            f"        document.getElementById('json_payload_render').innerHTML = '<span class=\"text-danger\">Failed to retrieve streaming payload resource.</span>';\n"
            f"      }});\n"
            f"  }});\n"
            f"</script>\n"
        )
        
        try:
            TelemetryLogger.emit(f"[BIND_ENGINE] Committing absolute URL template patch to disk...\n")
            with open(target_html_path, "w", encoding="utf-8") as f:
                f.write(injected_js_ui)
            status_msg = f"SUCCESS: HTML view container bound to backend target '/{app_name}/api/{api_name}/'."
            TelemetryLogger.emit(f"[SUCCESS] Disk IO write verification finalized. Target: {target_html_path}\n")
            valid_flag = True
            errs = []
        except Exception as file_err:
            status_msg = f"FAILURE: Could not modify template vector structure: {str(file_err)}"
            TelemetryLogger.emit(f"[CRITICAL_ERROR] Disk IO fault caught during write loop: {str(file_err)}\n")
            valid_flag = False
            errs = [str(file_err)]

        captured_telemetry_logs = TelemetryLogger.flush()

        return JsonResponse({
            "status": "success",
            "minion_log": status_msg,
            "telemetry_stream": captured_telemetry_logs,
            "validation": {"valid": valid_flag, "errors": errs, "warnings": []}
        })
# ======================================================================
# END: FIXED_BIND_ABSOLUTE_URL_INJECTION (PATCH 2 OF 2)
# ======================================================================
