import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# 1. Setup Connection
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "password123" # Use your Docker password

def test_direct_write():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    try:
        with driver.session() as session:
            # 2. Create the "Architect" and the "Mission" nodes manually
            session.run("""
                MERGE (u:User {name: 'Delta'})
                SET u.role = 'Lead Architect'
                CREATE (m:Mission {text: $mission})
                MERGE (u)-[:DEFINED]->(m)
                RETURN u, m
            """, mission="Replace despair with a roadmap for growth.")
        print("--- SUCCESS: Graph nodes created directly! ---")
    except Exception as e:
        print(f"--- FAILED: {e} ---")
    finally:
        driver.close()

if __name__ == "__main__":
    test_direct_write()
