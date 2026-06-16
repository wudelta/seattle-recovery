# ======================================================================
# FILE: aurora/utils/telemetry.py (PATCH 1 OF 1)
# START: SYSTEM_TELEMETRY_STREAM_LOGGER
# ======================================================================
import threading

class TelemetryLogger:
    """
    Stateless Thread-safe Console Logging Utility.
    Isolates log capture streams from individual builders to prevent cross-app contamination.
    """
    _storage = threading.local()

    @classmethod
    def _get_buffer(cls) -> list:
        if not hasattr(cls._storage, "logs"):
            cls._storage.logs = []
        return cls._storage.logs

    @classmethod
    def emit(cls, message: str) -> None:
        """Appends a localized tracing event to the active thread's stream buffer."""
        cls._get_buffer().append(message)

    @classmethod
    def flush(cls) -> str:
        """Extracts, builds, and wipes the active log stack returning a unified stream string."""
        buffer = cls._get_buffer()
        stream = "".join(buffer)
        buffer.clear()
        return stream
# ======================================================================
# END: SYSTEM_TELEMETRY_STREAM_LOGGER (PATCH 1 OF 1)
# ======================================================================
