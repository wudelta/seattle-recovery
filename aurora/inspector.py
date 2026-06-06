# ======================================================================
# FILE: aurora/inspector.py (PATCH 1 OF 2)
# START: STATIC CODE ANALYSIS ENGINE & NATIVE SYNTAX PROCESSING
# ======================================================================
import ast
import subprocess
import json

class ValidationInspector:
    """Automated local code inspector utilizing Ruff to replace Spyder IDE tools."""

    @staticmethod
    def check_syntax_and_imports(code_string: str) -> dict:
        results = {"valid": True, "errors": [], "warnings": []}

        # 1. IMMEDIATE SYNTAX CHECK: Native AST parser
        try:
            ast.parse(code_string)
        except SyntaxError as e:
            results["valid"] = False
            results["errors"].append(f"Syntax Error (Line {e.lineno}): {e.msg}")
            return results  # Halt immediately if code is fundamentally broken
# ======================================================================
# END: STATIC CODE ANALYSIS ENGINE & NATIVE SYNTAX PROCESSING
# ======================================================================

# ======================================================================
# FILE: aurora/inspector.py (PATCH 2 OF 2)
# START: OFFLINE RUFF SUBPROCESS EXECUTION & METRIC PARSING
# ======================================================================
        # 2. ULTRA-FAST RUFF CHECK: Intercept checks via shell stream execution
        try:
            # Command options run completely offline, outputting structured JSON metrics
            cmd = ["ruff", "check", "-", "--output-format=json"]
            process = subprocess.run(
                cmd, input=code_string, capture_output=True, text=True, check=False
            )

            # If ruff successfully returns an analysis array
            if process.stdout.strip():
                violations = json.loads(process.stdout)
                for item in violations:
                    msg = f"[{item.get('code')}] Line {item.get('location', {}).get('row')}: {item.get('message')}"
                    
                    # Distinguish critical errors from linting warnings (like unused imports/variables)
                    # Ruff labels syntax/logic issues as E or F categories
                    if item.get('code', '').startswith(('E', 'F')):
                        results["valid"] = False
                        results["errors"].append(msg)
                    else:
                        results["warnings"].append(msg)
                        
        except FileNotFoundError:
            results["warnings"].append("[System Alert]: 'ruff' binary not found in system path. Run your environment sync.")
        except Exception as e:
            results["errors"].append(f"Ruff Engine Exec Error: {str(e)}")

        return results
# ======================================================================
# END: OFFLINE RUFF SUBPROCESS EXECUTION & METRIC PARSING
# ======================================================================
