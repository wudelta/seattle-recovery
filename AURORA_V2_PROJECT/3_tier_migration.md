# 3-Tier Enterprise Architecture Migration Guide

### Target Host Environment
* **Platform:** Native Ubuntu Linux Laptop
* **Hardware Profile:** 2-Core CPU / 8GB RAM
* **Execution Layer:** Native Linux Kernel (Processes isolated via cgroups/namespaces)

### Security Target
* **Authentication:** Production-Ready (Authenticated Graph Layer, Isolated Relational Buffers)
* **Resource Profile:** Tight memory ceilings to prevent host-level system lockups

---

## 🗺️ Master Configuration Blueprint (`docker-compose.yml`)

Create this file in your absolute root directory. It applies a **strict 1GB RAM ceiling** to both database services, leaving 6GB free for your Ubuntu desktop host, Django, and Node.js.

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: seattle_postgres
    environment:
      POSTGRES_USER: delta_admin
      POSTGRES_PASSWORD: local_secure_password
      POSTGRES_DB: hopehub_production
      # INTERNAL MEMORY TUNING FOR 1GB CEILING
      POSTGRES_INITDB_ARGS: >-
        --with-segsize=1
        -c shared_buffers=256MB
        -c effective_cache_size=768MB
        -c work_mem=16MB
        -c maintenance_work_mem=64MB
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        reservations:
          memory: 128M
        limits:
          cpus: '0.50'
          memory: 1024M
    networks:
      - recovery_net

  neo4j:
    image: neo4j:5.12-community
    container_name: seattle_neo4j
    ports:
      - "7474:7474"   # HTTP Dashboard Browser Interface
      - "7687:7687"   # Bolt Protocol Connection Port
    environment:
      # FIXED: Production authentication enforced on startup
      - NEO4J_AUTH=neo4j/secure_graph_password_2026
      # FIXED: JVM limits overriding the default 8GB host heuristics
      - NEO4J_server_memory_heap_initial__size=256m
      - NEO4J_server_memory_heap_max__size=512m
      - NEO4J_server_memory_pagecache_size=256m
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    deploy:
      resources:
        reservations:
          memory: 256M
        limits:
          cpus: '0.50'
          memory: 1024M
    networks:
      - recovery_net

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: seattle_api
    command: daphne -b 0.0.0.0 -p 8000 project.asgi:application
    environment:
      - NEO4J_PASSWORD=secure_graph_password_2026
    volumes:
      - ./backend:/app
      - django_media:/app/media
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - neo4j
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 1024M
    networks:
      - recovery_net

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: seattle_frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 1024M
    networks:
      - recovery_net

volumes:
  postgres_data:
  django_media:
  neo4j_data:    # FIXED: Retains your graph network layout
  neo4j_logs:    # FIXED: Captures query error tracking histories

networks:
  recovery_net:
    driver: bridge
```

---

## 📋 Step-by-Step Migration Sequence

### Phase 1: Native Clean & Port Clearing

Run these steps in your native terminal to stop existing native database processes from blocking your Docker container sockets.

1. **Capture Local Dependencies:** Activate your python local virtual environment.
   ```bash
   pip freeze > requirements-dev.txt
   ```
2. **Stop Native PostgreSQL Server:** Free up port `5432`.
   ```bash
   sudo systemctl stop postgresql
   sudo systemctl disable postgresql
   ```
3. **Stop Native Neo4j Instance:** Free up ports `7474` and `7687`.
   ```bash
   sudo systemctl stop neo4j || true
   sudo systemctl disable neo4j || true
   ```

### Phase 2: Secure Neo4j Initialization

This step isolated the graph engine configuration to test your production credentials.

1. **Spin Up Database Engines:** Launch the infrastructure components background layer.
   ```bash
   docker compose up -d postgres neo4j
   ```
2. **Verify Kernel Resource Enforcement:** Monitor the cgroup metrics to verify the 1GB RAM ceilings are locked.
   ```bash
   docker stats seattle_neo4j seattle_postgres
   ```
3. **Verify Auth Over Dashboard:** Open your local browser and navigate to `http://localhost:7474`. Log in with your new production parameters:
   * **Username:** `neo4j`
   * **Password:** `secure_graph_password_2026`
   * *Ensure the dashboard opens cleanly without throwing an unauthenticated error or forcing a password reset prompt.*

### Phase 3: Secure Python Connection Utility Integration

Update your backend graph network client code (e.g., `app/utils/graph_client.py` or your seeding file) to match the explicit authentication requirement:

```python
import os
from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self):
        # Fallback to localhost if running script natively outside container space
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = "neo4j"
        # Extract environment variable securely or use your development fallback
        self.password = os.getenv("NEO4J_PASSWORD", "secure_graph_password_2026")
        self.driver = None
        
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        except Exception as e:
            print(f"CRITICAL: Secure Neo4j initialization failure: {e}")

    def close(self):
        if self.driver:
            self.driver.close()
```

### Phase 4: Data Population & Full-Stack Deployment

1. **Run Population Utility:** Run your existing local data seeding script. Because the configuration passes the authenticated `auth=(user, password)` parameters, transactions will map directly into the secure container.
2. **Build and Boot Rest of Stack:** Bring up Django (Tier 2) and Node.js (Tier 1) together.
   ```bash
   docker compose up -d --build
   ```
3. **Verify Complete Footprint:** Run your final kernel diagnostic tool to ensure all 4 tiers stay balanced.
   ```bash
   docker stats
   ```
