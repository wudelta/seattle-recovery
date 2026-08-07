# ======================================================================
# FILE: aurora/utils/telemetry.py
# START: SYSTEM_TELEMETRY_STREAM_LOGGER
# ======================================================================

import threading


class TelemetryLogger:
    """
    Thread-local telemetry buffer for shared Aurora infrastructure.

    Callers emit tracing events into the active thread's buffer and may
    later flush the accumulated stream as a single string.
    """

    _storage = threading.local()

    @classmethod
    def _get_buffer(cls) -> list[str]:
        if not hasattr(cls._storage, "logs"):
            cls._storage.logs = []

        return cls._storage.logs

    @classmethod
    def emit(cls, message: str) -> None:
        """Append one tracing event to the active thread's telemetry buffer."""
        cls._get_buffer().append(message)

    @classmethod
    def flush(cls) -> str:
        """Return and clear the active thread's accumulated telemetry stream."""
        buffer = cls._get_buffer()
        stream = "".join(buffer)
        buffer.clear()

        return stream

# ======================================================================
# END: SYSTEM_TELEMETRY_STREAM_LOGGER
# ======================================================================