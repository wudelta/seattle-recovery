# ======================================================================
# FILE: aurora/management/commands/run_daphne.py (PATCH 1 OF 1)
# START: CUSTOM DAPHNE ASYNC DEV SERVER ROUTINE
# ======================================================================
import subprocess
import sys
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Launches the Daphne ASGI development server with development static asset styling support."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Initializing Daphne ASGI Engine Layer..."))
        self.stdout.write("Target Matrix: core_logic.asgi:application @ 127.0.0.1:8000\n")
        
        # Cleaned command array containing strictly valid Daphne runtime arguments
        cmd = [
            sys.executable, "-m", "daphne",
            "-b", "127.0.0.1",
            "-p", "8000",
            "core_logic.asgi:application"
        ]
        
        try:
            # Pass execution directly over to the sub-process container
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n🛑 Daphne ASGI server halted via keyboard interrupt."))
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f"❌ Daphne exited with a critical error: {e}"))
# ======================================================================
# END: CUSTOM DAPHNE ASYNC DEV SERVER ROUTINE
# ======================================================================
