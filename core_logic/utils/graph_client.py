# ======================================================================
# FILE: core_logic/utils/graph_client.py (PATCH 1 OF 1)
# START: SECURE_NEO4J_CLIENT_INITIALIZATION
# ======================================================================
import os
from neo4j import GraphDatabase

class Neo4jConnection:
    """
    Shared enterprise network connection utility for Neo4j.
    Accessible by both Aurora and HopeHub apps to prevent circular imports.
    """
    def __init__(self):
        # Resolve target network routing for native host or container space
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "secure_graph_password_2026")
        self.driver = None
        
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password),
                max_connection_lifetime=300,
                keep_alive=True
            )
        except Exception as e:
            raise ConnectionError(f"CRITICAL: Secure Neo4j initialization failure: {e}")

    def close(self):
        if self.driver:
            self.driver.close()

    def get_session(self):
        if not self.driver:
            raise ValueError("Driver is not initialized.")
        return self.driver.session()
# ======================================================================
# END: SECURE_NEO4J_CLIENT_INITIALIZATION (PATCH 1 OF 1)
# ======================================================================
