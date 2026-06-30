# Migration Guide: Database Segregation, Application Splitting, and UUID Overhaul

## Phase 1: Architectural Blueprint & Code Restructuring

Before touching the database, you must separate your Django application code into two distinct directory trees to prepare for individual Docker tracking.

### 1.1 Directory Tree Realignment
Duplicate your current repository into two completely independent folders on your system.

```text
/home/user/projects/
├── aurora-builder/           # Git Repo 1: Kept strictly local
│   ├── aurora/               # The Builder app folder
│   └── core_logic/           # Isolated project configuration
│
└── hopehub-app/              # Git Repo 2: Pushed to Cloud production
    ├── hopehub/              # The Application app folder
    └── core_logic/           # Isolated project configuration
```

### 1.2 Configuration Isolation
Inside both directories, completely decouple the `settings.py` and master `urls.py` files.

#### In `aurora-builder/core_logic/settings.py`:
* Remove `'hopehub'` from your `INSTALLED_APPS`.
* Keep a configuration variable pointing to your local sibling directory so macros can resolve paths:
  ```python
  HOPEHUB_PROJECT_DIR = "/home/user/projects/hopehub-app/"
  ```

#### In `hopehub-app/core_logic/settings.py`:
* Remove `'aurora'` from your `INSTALLED_APPS`.

#### In both master `urls.py` files:
* Strip out any cross-app routing `path()` inclusions. Each application must only include its own respective app paths.

***

## Phase 2: Implementing the Custom UUID User Model

To securely eliminate sequential primary keys (`id = 1`), you must swap out Django's native authentication backend for a Custom User model across **both** applications.

### 2.1 Code Implementation
In both codebases, create or modify a `models.py` file within a user-management application context (e.g., `users/models.py`):

```python
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
```

### 2.2 Wire Up Settings
Update `core_logic/settings.py` in **both** repositories to register your custom model:

```python
AUTH_USER_MODEL = 'users.CustomUser'
```

### 2.3 Refactor Related Models
Search your codebases for any reference to the User model. Ensure that any models pointing to it explicitly use `settings.AUTH_USER_MODEL` instead of direct imports:

```python
from django.conf import settings
from django.db import models

class HopeHubFeature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
```

***

## Phase 3: Domain Data Extraction

Since the applications are still combined in your live database, extract your business domain schemas using explicit table-prefix filters to prevent user-table collisions.

### 3.1 Back up Independent Domain Tables
Run these explicit backup commands from your Ubuntu terminal to isolate raw data:

```bash
# Export strictly Aurora domain tables
pg_dump -U postgres -d your_current_db -t "aurora_*" -F c -f /tmp/aurora_domain.dump

# Export strictly Hopehub domain tables
pg_dump -U postgres -d your_current_db -t "hope_hub_*" -F c -f /tmp/hopehub_domain.dump
```

***

## Phase 4: Database Provisioning and Re-linking

Now we initialize the isolated logical databases on your single PostgreSQL instance, allow Django to build modern UUID core schemas, and snap your legacy data back in.

### 4.1 Provision the New Logical Databases
Log into your local `psql` instance and create two empty targets:

```sql
CREATE DATABASE aurora_db;
CREATE DATABASE hopehub_db;
```

### 4.2 Generate and Apply Pristine Base Schemas
Point your local environment configuration to your new databases temporarily. Since the databases are blank, Django's native migration engine will construct your `auth_user` and system architecture with clean, **UUID-native** definitions.

```bash
# In /aurora-builder/
python manage.py makemigrations
python manage.py migrate --database=aurora_db

# In /hopehub-app/
python manage.py makemigrations
python manage.py migrate --database=hopehub_db
```

### 4.3 Inject Core Domain Data
Restore the business logic data you exported in Phase 3. Use the `--data-only` flag to preserve the new structural integrity of the base schemas.

```bash
pg_restore -U postgres -d aurora_db --data-only /tmp/aurora_domain.dump
pg_restore -U postgres -d hopehub_db --data-only /tmp/hopehub_domain.dump
```

### 4.4 Bootstrap Identity & Resolve Foreign Keys
Generate a static UUID string using python to use as your unified developer security identity:

```bash
python3 -c "import uuid; print(uuid.uuid4())"
# Copy output string example: f81d4fae-7dec-11d0-a765-00a0c91e6bf6
```

Create your administrative superuser entries via Django management utilities inside both folders:

```bash
python manage.py createsuperuser
```

Connect directly to your local Postgres server (`psql`) to perform data manipulation. This remaps the internal legacy integer relationship (`owner_id = 1`) seamlessly to your fresh UUID:

```sql
-- Connect to Aurora
\c aurora_db
UPDATE auth_user SET id = 'YOUR_STATIC_UUID_STRING' WHERE username = 'your_username';
UPDATE aurora_project SET owner_id = 'YOUR_STATIC_UUID_STRING' WHERE owner_id = '1';

-- Connect to Hopehub
\c hopehub_db
UPDATE auth_user SET id = 'YOUR_STATIC_UUID_STRING' WHERE username = 'your_username';
UPDATE hope_hub_table SET owner_id = 'YOUR_STATIC_UUID_STRING' WHERE owner_id = '1';
```
*(Repeat the data row updates for any other tables containing the legacy `owner_id` column).*

***

## Phase 5: Containerized Dev Architecture Setup

Bring everything back together by writing an enterprise-style multi-service `docker-compose.yml` file at the root of your workspace (`/home/user/projects/`).

```yaml
version: '3.8'

services:
  # Aurora Development Service
  aurora:
    build: ./aurora-builder
    command: daphne -b 0.0.0.0 -p 8000 core_logic.asgi:application
    ports:
      - "8000:8000"
    volumes:
      - ./aurora-builder:/app
      # Grants local macro file-system write access into Hopehub workspace
      - ./hopehub-app:/home/user/projects/hopehub-app
    environment:
      - DATABASE_URL=postgres://postgres:pass@host.docker.internal:5432/aurora_db
      - DEBUG=True

  # Hopehub Staging Service (Simulating Cloud production locally)
  hopehub:
    build: ./hopehub-app
    command: daphne -b 0.0.0.0 -p 8000 core_logic.asgi:application
    ports:
      - "8001:8000" # Mapped to 8001 to resolve host conflicts
    volumes:
      - ./hopehub-app:/app
    environment:
      - DATABASE_URL=postgres://postgres:pass@host.docker.internal:5432/hopehub_db
      - DEBUG=True
```
