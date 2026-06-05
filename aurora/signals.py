# aurora/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from aurora.models import ComponentRegistry
from aurora.nodes import ComponentNode

@receiver(post_save, sender=ComponentRegistry)
def sync_postgres_to_neo4j(sender, instance, created, **kwargs):
    """
    Automated Sync Signal.
    Creating or updating a file log entry in PostgreSQL automatically
    drops, registers, or synchronizes its twin Node in the Neo4j graph network.
    """
    if created:
        # Instantly spawn the node inside the graph network topology
        ComponentNode(
            postgres_id=str(instance.id),
            file_path=instance.file_path
        ).save()
    else:
        # Handle path alterations safely if an active file moves
        try:
            node = ComponentNode.nodes.get(postgres_id=str(instance.id))
            node.file_path = instance.file_path
            node.save()
        except ComponentNode.DoesNotExist:
            # Fallback failsafe if graph database was cleared out-of-band
            ComponentNode(
                postgres_id=str(instance.id),
                file_path=instance.file_path
            ).save()

@receiver(post_delete, sender=ComponentRegistry)
def purge_from_neo4j_graph(sender, instance, **kwargs):
    """
    Cleans up graph artifacts when a components entry is legally purged from SQL.
    """
    try:
        node = ComponentNode.nodes.get(postgres_id=str(instance.id))
        node.delete()
    except ComponentNode.DoesNotExist:
        pass
