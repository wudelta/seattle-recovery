# seed_existing_docs.py
import os
import sys
import django

sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_logic.settings')
django.setup()

from aurora.models import Document, Content, Metadata

def seed_system_spec_to_existing_schema():
    print("💾 Seeding SAS-001 directly into Wu's Relational Architecture Schema...")
    
    # 1. Establish the base parent Document token
    doc_title = "SAS-001: Immutable System Prompter"
    document, created = Document.objects.get_or_create(title=doc_title)
    
    # 2. Insert or update the raw text payload block in the Content table
    technical_payload = (
        "## 1. Core Purpose\n"
        "Acts as the project's immutable memory anchor. It isolates and preserves "
        "global system prompts, hardware limits, and operational laws within the local "
        "graph database. This prevents total context loss when cleaning session chatter.\n\n"
        "## 2. Technical Blueprint\n"
        "The 8B Janitor sweep query explicitly excludes this node label using a "
        "`WHERE NOT s:SystemState` filter directive.\n\n"
        "## 3. Hardware Impact Profile\n"
        "- RAM Footprint: 0MB idle. Consumes transient network sockets only during execution.\n"
        "- Storage Footprint: Optimized for resource-constrained 8GB RAM host environments."
    )
    
    content_node, content_created = Content.objects.get_or_create(
        document=document,
        defaults={'content': technical_payload}
    )
    if not content_created:
        content_node.content = technical_payload
        content_node.save()

    # 3. Insert specific metadata control tags for fast relational scoping
    # Ensure every single dictionary item contains the "type" key
    metadata_tags = [
        {
            "key": "associated_module", 
            "value": "core_logic/memory.py", 
            "type": "source_dependency",
            "criticality": "HIGH", 
            "status": "IMPLEMENTED"
        },
        {
            "key": "component_scope", 
            "value": "Core Logic Layer / Neo4j Graph Integrity", 
            "type": "architectural_boundary",
            "criticality": "HIGH", 
            "status": "IMPLEMENTED"
        },
        {
            "key": "project_scope", 
            "value": "aurora", 
            "type": "ecosystem_partition", # <-- Added this missing element
            "criticality": "MEDIUM", 
            "status": "ACTIVE"
        }
    ]

    for tag in metadata_tags:
        meta_node, meta_created = Metadata.objects.get_or_create(
            document=document,
            key=tag["key"],
            defaults={
                "value": tag["value"],
                "criticality": tag["criticality"],
                "status": tag["status"],
                "type": tag["type"]
            }
        )
        if not meta_created:
            meta_node.value = tag["value"]
            meta_node.criticality = tag["criticality"]
            meta_node.status = tag["status"]
            meta_node.save()

    print(f"✔ SUCCESS: Linked fields populated across Document, Content, and Metadata tables.")

if __name__ == "__main__":
    seed_system_spec_to_existing_schema()
