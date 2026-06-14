# ======================================================================
# FILE: aurora/signals.py (PATCH 1 OF 3)
# START: RUNTIME_IMPORTS_AND_DELETION_SIGNAL_MATRIX
# ======================================================================
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from aurora.models import ComponentRegistry
from aurora.nodes import ComponentNode
from neomodel import db
import os

@receiver(post_delete, sender=ComponentRegistry)
def clean_graph_on_component_deletion(sender, instance, **kwargs):
    """
    Cleans up corresponding Neo4j graph artifacts completely when a 
    ComponentRegistry relational record is removed.
    """
    try:
        # Clear nodes linked via database ID tracking mapping
        cypher_purge = """
        MATCH (n {postgres_id: $pg_id})
        DETACH DELETE n
        """
        db.cypher_query(cypher_purge, {"pg_id": str(instance.id)})
        
        # Fallback path clearance for completely unindexed components
        if instance.file_path:
            db.cypher_query("MATCH (n {file_path: $fp}) DETACH DELETE n", {"fp": instance.file_path})
    except Exception as purge_err:
        print(f"[SIGNAL EXCEPTION] Clean graph sync failed: {str(purge_err)}")
# ======================================================================
# END: RUNTIME_IMPORTS_AND_DELETION_SIGNAL_MATRIX (PATCH 1 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/signals.py (PATCH 2 OF 3)
# START: POST_SAVE_NODE_SYNCHRONIZATION_BLOCK
# ======================================================================
@receiver(post_save, sender=ComponentRegistry)
def sync_component_to_neo4j(sender, instance, created, **kwargs):
    """
    Centralized Signal engine running the exact defensive lookup logic 
    ported directly from the successful page skeleton builder sequence.
    """
    visibility_clean = instance.visibility.lower() if instance.visibility else "private"
    current_path = instance.file_path

    # 1. DEFENSIVE LOOKUP PASS: Fallback lookup matching both postgres_id and file_path
    node = None
    try:
        if instance.id:
            node = ComponentNode.nodes.get(postgres_id=str(instance.id))
    except ComponentNode.DoesNotExist:
        pass

    if not node and current_path:
        try:
            node = ComponentNode.nodes.get(file_path=current_path)
        except ComponentNode.DoesNotExist:
            pass

    if not node:
        try:
            # Supply postgres_id immediately to satisfy neomodel required validation constraints
            node = ComponentNode(file_path=current_path, postgres_id=str(instance.id))
            node.save()
        except Exception as create_err:
            print(f"[SIGNAL EXCEPTION] Failed to initialize node shell: {str(create_err)}")
            return

    # Sync relational parameters safely onto the fetched/created graph record node
    node.postgres_id = str(instance.id)
    node.file_path = current_path  # FIX: Ensure updated file paths are explicitly synced to Neo4j
    node.name = instance.name
    node.persona = instance.persona
    node.visibility = visibility_clean
    node.save()
# ======================================================================
# END: POST_SAVE_NODE_SYNCHRONIZATION_BLOCK (PATCH 2 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/signals.py (PATCH 3 OF 3)
# START: TOPO_LINKING_PORTED_MATCH_ENGINE
# ======================================================================
    # 2. TOPO-LINKING PORTED MATCH ENGINE
    # When the signal catches a CONTROLLER_MODULE file entry, reconstruct the HTML link string
    if instance.persona == "CONTROLLER_MODULE" and current_path and "_view.py" in current_path:
        try:
            # Reconstruct string targets exactly like page_skeleton.py did
            path_parts = current_path.replace("\\", "/").split("/")
            if len(path_parts) >= 3:
                app_name = path_parts[0]
                filename = path_parts[-1] 
                page_base = filename.replace("_view.py", "") 
                
                # Reconstruct the precise relative target paths that successfully paired in the query
                rel_html_path = f"templates/{app_name}/{page_base}.html"
                rel_view_path = current_path 

                # Run the exact MERGE query configuration that established the visual arrows
                cypher_link_query = """
                MERGE (h:ComponentNode {file_path: $html_path})
                ON CREATE SET h.name = $html_name, h.persona = 'CANVAS_LAYOUT', h.visibility = $vis
                MERGE (v:ComponentNode {file_path: $view_path})
                ON CREATE SET v.name = $view_name, v.persona = 'CONTROLLER_MODULE', v.visibility = $vis
                MERGE (h)-[r:DEPENDS_ON]->(v)
                RETURN count(r) as link_count
                """
                params = {
                    "html_path": rel_html_path,
                    "html_name": f"{page_base}_layout",
                    "view_path": rel_view_path,
                    "view_name": f"{page_base}_view",
                    "vis": visibility_clean
                }
                result, meta = db.cypher_query(cypher_link_query, params)
                print(f"[SIGNAL DIAGNOSTIC] Ported Cypher relationship merge output counter: {result}")
        except Exception as sync_err:
            print(f"[SIGNAL WARNING] Ported lineage line pairing deferred: {str(sync_err)}")
            
    # 3. CONSTRAINED DEFENSIVE SWEEP
    # Safeguard: Prevent triggering the recursive scanner inside transactional automated mock test environments
    if not os.environ.get('PYTEST_CURRENT_TEST'):
        try:
            from aurora.utils.ast_scanner import OGMTopographyScanner
            scanner = OGMTopographyScanner(os.getcwd())
            scanner.map_workspace_topography()
        except Exception as scan_err:
            print(f"[SIGNAL WARNING] Background topography update deferred: {str(scan_err)}")
# ======================================================================
# END: TOPO_LINKING_PORTED_MATCH_ENGINE (PATCH 3 OF 3)
# ======================================================================
