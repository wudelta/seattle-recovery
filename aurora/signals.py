# aurora/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from aurora.models import ComponentRegistry
from aurora.nodes import ComponentNode

@receiver(post_save, sender=ComponentRegistry)
def sync_postgres_to_neo4j(sender, instance, created, **kwargs):
    """Automated Database Signal: Saves or updates graph nodes synchronously."""
    if created:
        # Generate the graph bubble directly in your auth-free container
        ComponentNode(
            postgres_id=str(instance.id),
            file_path=instance.file_path
        ).save()
    else:
        try:
            node = ComponentNode.nodes.get(postgres_id=str(instance.id))
            node.file_path = instance.file_path
            node.save()
        except ComponentNode.DoesNotExist:
            ComponentNode(
                postgres_id=str(instance.id),
                file_path=instance.file_path
            ).save()

@receiver(post_delete, sender=ComponentRegistry)
def purge_from_neo4j_graph(sender, instance, **kwargs):
    """Automated Database Signal: Cleans up graph artifacts on erasure."""
    try:
        node = ComponentNode.nodes.get(postgres_id=str(instance.id))
        node.delete()
    except ComponentNode.DoesNotExist:
        pass
