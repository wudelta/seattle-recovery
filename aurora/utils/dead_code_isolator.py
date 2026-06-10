# ======================================================================
# FILE: aurora/utils/dead_code_isolator.py (COMPLETE COMPONENT)
# START: FULL_DEAD_CODE_ISOLATOR_ENGINE
# ======================================================================
import os
from aurora.nodes import ComponentNode
from aurora.models import ComponentRegistry
from aurora.utils.ast_scanner import OGMTopographyScanner

class DeadCodeIsolator:
    """Analyzes Neo4j relationship maps to identify and quarantine orphaned assets."""

    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.abspath(workspace_root)

    def execute_complete_audit(self) -> dict:
        """Refreshes topography maps, finds dead leaves, and isolates records."""
        # Step 1: Run fresh AST mapping pass to guarantee graph accuracy
        scanner = OGMTopographyScanner(self.workspace_root)
        scanner.map_workspace_topography()

        report = {"quarantined_files": [], "skipped_locked_files": []}

        # Step 2: Fetch all tracking records from the relational DB layer
        all_tracked_components = ComponentRegistry.objects.filter(status="ACTIVE")

        for component in all_tracked_components:
            # System entry points are entry vectors and must never be pruned
            if component.persona == "ENTRY_POINT":
                continue

            try:
                # Pull the live graph topography representation
                graph_node = ComponentNode.nodes.get(postgres_id=str(component.id))
                
                # Check for inbound parent connections (files relying on this asset)
                incoming_dependencies = graph_node.required_by.all()

                # If no other system assets point to this file, it is an orphan
                if not incoming_dependencies:
                    # Defense layer: Respect manual safety flags applied by Delta
                    if component.locked:
                        report["skipped_locked_files"].append(component.file_path)
                        continue
                    
                    # Apply quarantine state directly to the transactional layer
                    component.status = "STAGED_FOR_DELETION"
                    component.description = (
                        f"[QUARANTINE ALERT] Isolated automatically via system scan. "
                        f"Zero inbound dependencies resolved in topological graph map.\n"
                        f"{component.description}"
                    )
                    component.save()
                    report["quarantined_files"].append(component.file_path)

            except ComponentNode.DoesNotExist:
                # Fallback safety handler if a database entry misses its graph bubble
                continue

        return report
# ======================================================================
# END: FULL_DEAD_CODE_ISOLATOR_ENGINE
# ======================================================================
