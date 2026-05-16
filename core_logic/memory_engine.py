# core_logic/memory_engine.py
import os
from mem0 import Memory

class IsolatedMemoryEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IsolatedMemoryEngine, cls).__new__(cls)
            cls._instance._initialize_engine()
        return cls._instance

    def _initialize_engine(self):
        """Initializes Mem0 utilizing Gemini Cloud Embeddings + Local Neo4j."""
        api_key = os.getenv("GEMINI_API_KEY")
        neo4j_uri = os.getenv("DB_NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("DB_NEO4J_USER", "neo4j")
        neo4j_pass = os.getenv("DB_NEO4J_PASSWORD")

        if not api_key:
            raise ValueError("[FATAL] GEMINI_API_KEY is missing from your .env configurations.")

        # Re-map the configurations to feed 768-dimensional float maps to Neo4j
        config = {
            "vector_store": {
                "provider": "neo4j",
                "config": {
                    "url": neo4j_uri,
                    "username": neo4j_user,
                    "password": neo4j_pass,
                    "embedding_model_dims": 768  # Matches Gemini text-embedding-004 dimensions
                }
            },
            "embedder": {
                "provider": "gemini",
                "config": {
                    "model": "text-embedding-004",
                    "api_key": api_key
                }
            },
            "llm": {
                "provider": "groq",
                "config": {
                    "model": "llama-3.1-8b-instant",
                    "api_key": os.getenv("GROQ_API_KEY")
                }
            }
        }

        self.memory = Memory.from_config(config)
        print("[SUCCESS] Mem0 Cloud-Embedding / Local Neo4j Gemini Engine Active.")

    def store_development_fact(self, user_id, text, project_scope="aurora"):
        metadata = {"project": project_scope.lower()}
        return self.memory.add(text, user_id=user_id, metadata=metadata)

    def search_relevant_context(self, user_id, query, project_scope="aurora"):
        return self.memory.search(query, user_id=user_id, limit=5)
