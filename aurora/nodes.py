# ======================================================================
# FILE: aurora/nodes.py (PATCH 1 OF 1)
# START: NEO4J_COMPONENT_GRAPH_STRUCTURE_DEFINITIONS
# ======================================================================
from neomodel import (
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
)


class ComponentNode(StructuredNode):
    """
    Neo4j projection of an authoritative ComponentRegistry record.

    The node stores only metadata needed for graph retrieval and bounded
    dependency traversal. PostgreSQL remains the authoritative data source.
    """

    # PostgreSQL identity and repository location
    postgres_id = StringProperty(unique_index=True, required=True)
    file_path = StringProperty(unique_index=True, required=True)

    # Minimal searchable component metadata
    name = StringProperty()
    persona = StringProperty()
    status = StringProperty()
    description = StringProperty()

    # Directed dependency relationships
    depends_on = RelationshipTo("ComponentNode", "DEPENDS_ON")
    required_by = RelationshipFrom("ComponentNode", "DEPENDS_ON")
# ======================================================================
# END: NEO4J_COMPONENT_GRAPH_STRUCTURE_DEFINITIONS (PATCH 1 OF 1)
# ======================================================================