# aurora/minion_array/generate_python.py
import sys
import traceback

def run(clean_task_details, fallback_context=""):
    """
    Validates incoming Python code snippets by passing them through the 
    built-in compile() framework before writing them to the host drive.
    Includes traceback error capture parameters.
    """
    try:
        # Compile text snippet to verify syntax without executing the code strings
        compile(clean_task_details, "<string>", "exec")
        # CRUCIAL: Return the actual clean code string, NOT an evaluation return
        return clean_task_details
    except SyntaxError as syntax_err:
        error_log = (
            f"<!-- Python Minion Compilation Exception Block -->\n"
            f"<!-- Line: {syntax_err.lineno} | Offset: {syntax_err.offset} -->\n"
            f"<!-- Error Details: {str(syntax_err)} -->\n"
            f"<!-- Full Context Trace:\n{traceback.format_exc()}\n-->"
        )
        return error_log
