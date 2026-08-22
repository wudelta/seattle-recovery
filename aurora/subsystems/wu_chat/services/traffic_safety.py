# ======================================================================
# FILE: aurora/subsystems/wu_chat/services/traffic_safety.py
# START: WU_TRAFFIC_SAFETY_SERVICE
# ======================================================================

import sys
from collections import deque
from threading import Lock


# Thread safety locks and allocation deques tracking network transaction states
OUTBOUND_TRAFFIC_LOG = deque()
TRAFFIC_LOCK = Lock()
# ======================================================================
# END: PRE_SEND_TRAFFIC_SAFETY_MONITORING_METRICS
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/wu_chat/api/endpoint.py
# START: UTILITY_CONTEXT_TOKEN_BUDGETER
# ======================================================================
def enforce_context_token_budget(raw_text_payload, max_tokens=150000):
    """
    Traps and analyzes outbound payloads before any API call is made.
    Logs absolute metrics and strips out massive text blocks dynamically.
    """
    if not raw_text_payload:
        sys.stderr.write(
            "📊 [TRAFFIC ANALYZER]: Received empty or null payload text.\n"
        )
        sys.stderr.flush()
        return ""

    # Measure exact inbound metrics before modification
    raw_char_count = len(raw_text_payload)
    estimated_raw_tokens = raw_char_count // 4

    sys.stderr.write(
        f"\n📊 [TRAFFIC ANALYZER PRE-SEND AUDIT]:\n"
        f"  -> Total Character Volume: {raw_char_count}\n"
        f"  -> Estimated Inbound Tokens: {estimated_raw_tokens}\n"
        f"  -> Safety Budget Target Limit: {max_tokens} tokens "
        f"(~{max_tokens * 4} chars)\n"
    )
    sys.stderr.flush()

    # If the payload fits comfortably within our budget boundaries, pass it intact
    max_chars = max_tokens * 4
    if raw_char_count <= max_chars:
        sys.stderr.write(
            "📊 [TRAFFIC ANALYZER]: "
            "Payload is clean. Forwarding completely intact.\n"
        )
        sys.stderr.flush()
        return raw_text_payload

    sys.stderr.write(
        "⚠️ [TRAFFIC ANALYZER]: Payload size boundary crossed! "
        "Executing surgical line-trimming...\n"
    )
    sys.stderr.flush()

    # Split the payload into lines to find what is inflating the string footprint
    lines = raw_text_payload.split("\n")
    sanitized_lines = []
    accumulated_chars = 0
    stripped_lines_count = 0

    for line in lines:
        line_len = len(line)

        # Guard 1: Drop individual giant string lines
        if line_len > 2000:
            stripped_lines_count += 1
            continue

        # Guard 2: Halt collection near the hard character ceiling
        if accumulated_chars + line_len + 1 > max_chars:
            stripped_lines_count += (
                len(lines)
                - len(sanitized_lines)
                - stripped_lines_count
            )
            break

        sanitized_lines.append(line)
        accumulated_chars += line_len + 1

    sanitized_text = "\n".join(sanitized_lines)

    # Append a clear system marker when truncation occurred
    if stripped_lines_count > 0:
        sanitized_text += (
            "\n\n... [🛡️ SECURITY INTERCEPT: "
            f"{stripped_lines_count} OVERSIZED/SURPLUS LINES STRIPPED "
            "TO PREVENT 429 LOCKOUT] ..."
        )

    sys.stderr.write(
        f"📊 [TRAFFIC ANALYZER POST-SANITIZATION SUMMARY]:\n"
        f"  -> Cleaned Character Footprint: {len(sanitized_text)}\n"
        f"  -> Cleaned Token Appx: {len(sanitized_text) // 4}\n"
        f"  -> Total Structural Lines Evicted: "
        f"{stripped_lines_count}\n\n"
    )
    sys.stderr.flush()

    return sanitized_text
# ======================================================================
# END: UTILITY_CONTEXT_TOKEN_BUDGETER

# ======================================================================
# END: WU_TRAFFIC_SAFETY_SERVICE
# ======================================================================
