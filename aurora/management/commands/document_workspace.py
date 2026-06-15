# ======================================================================
# FILE: aurora/management/commands/document_workspace.py (PATCH 1 OF 1)
# START: DJANGO_MANAGEMENT_COMMAND_DOCUMENTER_BRIDGE
# ======================================================================
from django.core.management.base import BaseCommand
from aurora.utils.documenter import WorkspaceDocumenter

class Command(BaseCommand):
    """
    Custom Django management command to execute the automated 
    WorkspaceCrawler documentation sweep via the Groq Minion fleet.
    """
    help = "Crawls registered active system components and generates documentation using Groq AI minions."

    def handle(self, *args, **options):
        # 1. Notify the operator of system initialization
        self.stdout.write(self.style.MIGRATE_HEADING("🚀 Initializing Native Management Command Documentation Stream..."))
        
        # 2. Instantiate the crawler utility
        documenter = WorkspaceDocumenter()
        
        # 3. Intercept the utility log stream and redirect outputs to the native self.stdout console writer
        def native_management_logger(text: str):
            self.stdout.write(text, ending="")
            
        documenter.emit_log = native_management_logger

        # 4. Trigger the active file system loop sweep
        report = documenter.execute_documentation_sweep()
        
        # 5. Output localized final completion summaries using Django style tags
        success_msg = f"📊 [SWEEP COMPLETE] Processed: {len(report['processed_files'])} | Skipped: {len(report['skipped_files'])} | Faults: {len(report['failures'])}"
        self.stdout.write(self.style.SUCCESS(f"\n{success_msg}"))
# ======================================================================
# END: DJANGO_MANAGEMENT_COMMAND_DOCUMENTER_BRIDGE (PATCH 1 OF 1)
# ======================================================================
