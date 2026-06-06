# ======================================================================
# FILE: aurora/nodes.py (PATCH 1 OF 1)
# START: NEO4J TOPOLOGY GRAPH STRUCTURE DEFINITIONS
# ======================================================================
from neomodel import StructuredNode, StringProperty, RelationshipTo, RelationshipFrom

class ComponentNode(StructuredNode):
    """
    Graph representation tracking codebase filesystem topology.
    Maps directly to PostgreSQL ComponentRegistry record entries via 'postgres_id'.
    """
    # Unique system identity parity anchors
    postgres_id = StringProperty(unique_index=True, required=True)
    file_path = StringProperty(unique_index=True, required=True)
    
    # Directed dependency network graph links
    # Outbound path defines assets required to function (Child Dependencies)
    depends_on = RelationshipTo('ComponentNode', 'DEPENDS_ON')
    
    # Inbound path defines external items relying on this file (Parent Dependencies)
    required_by = RelationshipFrom('ComponentNode', 'DEPENDS_ON')
# ======================================================================
# END: NEO4J TOPOLOGY GRAPH STRUCTURE DEFINITIONS
# ======================================================================
