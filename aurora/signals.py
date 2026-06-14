# ======================================================================
# FILE: aurora/signals.py (PATCH 1 OF 2)
# START: SIGNAL EXPORT & REAL-TIME GRAPH NODE INSERTION SYNCHRONIZER
# ======================================================================
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from aurora.models import ComponentRegistry
from aurora.nodes import ComponentNode
from aurora.utils.page_skeleton import PageSkeletonBuilder  # <-- Injected telemetry broker

@receiver(post_save, sender=ComponentRegistry)
def sync_postgres_to_neo4j(sender, instance, created, **kwargs):
    """Automated Database Signal: Saves or updates graph nodes synchronously with full context and live logging."""
    clean_visibility = (instance.visibility or "PRIVATE").lower()
    
    if created:
        # FIXED: Added live telemetry log emitter for new graph node creation tracking
        PageSkeletonBuilder.emit_log(f"[FORGE_ENGINE] [SIGNAL] Spawning fresh graph bubble in Neo4j for: '{instance.file_path}'\n")
        ComponentNode(
            postgres_id=str(instance.id),
            file_path=instance.file_path,
            name=instance.name or "",
            persona=instance.persona or "COMPILER_MODULE",
            visibility=clean_visibility
        ).save()
    else:
        try:
            node = ComponentNode.nodes.get(postgres_id=str(instance.id))
            # FIXED: Added live telemetry log emitter for updating pre-existing graph nodes
            PageSkeletonBuilder.emit_log(f"[FORGE_ENGINE] [SIGNAL] Synchronizing updated profile data to Neo4j node: '{instance.file_path}'\n")
            node.file_path = instance.file_path
            node.name = instance.name or ""
            node.persona = instance.persona or "COMPILER_MODULE"
            node.visibility = clean_visibility
            node.save()
        except ComponentNode.DoesNotExist:
            PageSkeletonBuilder.emit_log(f"[FORGE_ENGINE] [SIGNAL] Missing node fallback. Provisioning missing graph entry for: '{instance.file_path}'\n")
            ComponentNode(
                postgres_id=str(instance.id),
                file_path=instance.file_path,
                name=instance.name or "",
                persona=instance.persona or "COMPILER_MODULE",
                visibility=clean_visibility
            ).save()
# ======================================================================
# END: SIGNAL EXPORT & REAL-TIME GRAPH NODE INSERTION SYNCHRONIZER (PATCH 1 OF 2)
# ======================================================================

# ======================================================================
# FILE: aurora/signals.py (PATCH 2 OF 2)
# START: SIGNAL EXPORT & REAL-TIME GRAPH NODE PURGE OBLITERATOR
# ======================================================================
@receiver(post_delete, sender=ComponentRegistry)
def purge_from_neo4j_graph(sender, instance, **kwargs):
    """Automated Database Signal: Cleans up graph artifacts on erasure with live logging."""
    try:
        # Locate the exact node via the primary relational key index
        node = ComponentNode.nodes.get(postgres_id=str(instance.id))
        
        # FIXED: Added explicit telemetry tracking message for physical node purges
        PageSkeletonBuilder.emit_log(f"[FORGE_ENGINE] [SIGNAL] Erasing structural graph bubble from Neo4j: '{instance.file_path}'\n")
        
        node.delete()
    except ComponentNode.DoesNotExist:
        pass
# ======================================================================
# END: SIGNAL EXPORT & REAL-TIME GRAPH NODE PURGE OBLITERATOR (PATCH 2 OF 2)
# ======================================================================
