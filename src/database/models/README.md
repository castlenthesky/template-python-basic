# Database Models Organization Guide

Hey there, junior developer! As your principal engineer, I want to help you navigate how we've structured our database models in this project. Think of this README as a friendly guide to understanding where things go and why—it's all about making our codebase scalable, maintainable, and easy for the whole team to work with. We'll focus on the `src/database/models` directory, drawing from established best practices in Python projects using SQLModel (our ORM of choice). I'll explain the "what," "where," and most importantly, the "why" behind it, so you can confidently add new models or refactor existing ones.

### Key Principles for Placing Models
- **Centralize models in one dedicated spot**: All SQLModel classes (which define our database tables) live under `src/database/models`. This keeps database logic isolated from API features or services, reducing clutter and making it obvious where to look for schema definitions.
- **Use subdirectories for organization**: We've grouped models by database schema (e.g., `public/` for the default Postgres schema). Inside, each model gets its own file (e.g., `user.py`, `task.py`), with a `base.py` for shared schema-specific logic like custom metadata.
- **Avoid scattering models across features**: Don't put models in feature folders like `src/api/features/users/models.py` unless a model is truly isolated to that domain—shared entities like users or tasks belong here to prevent duplication and import headaches.
- **Always include `__init__.py` files**: This turns directories into Python packages, enabling clean imports (e.g., `from src.database.models.public.user import User`).

These choices promote modularity while acknowledging that databases are a cross-cutting concern in apps—research suggests this setup works well for FastAPI-like projects, where models double as Pydantic schemas for validation. It might feel opinionated at first, but it's designed to scale as our app grows.

### Why This Structure?
Centralizing models here separates database concerns from business logic (in `services/`) and API endpoints (in `api/features/`), following separation of concerns—a core principle in clean architecture. This makes Alembic migrations easier since all models are imported centrally in `migrations/env.py`, avoiding scattered metadata. Subdirectories by schema (like `public/`) handle Postgres namespaces logically, preventing name conflicts in multi-schema setups. Per-model files keep things readable—imagine debugging a monolithic `models.py` with 20+ classes!

### How to Add a New Model
1. Choose or create a subdirectory (e.g., `stratsim/` for a new schema).
2. Add `__init__.py` if needed, and a `base.py` for schema-specific bases (inherit from SQLModel).
3. Create `my_model.py` with your class (e.g., `class MyModel(StratSimBase, table=True): ...`).
4. Import it in the subdir's `__init__.py` for easy access.
5. Update Alembic if schema changes: `alembic revision --autogenerate`.

This pattern draws from SQLModel's own advice for multi-file setups, ensuring no circular imports via `TYPE_CHECKING` if relationships span files. If you're unsure, ping me—we'll pair on it!

---

As a principal engineer mentoring a junior developer, let's dive deeper into why we've structured `src/database/models` this way. This isn't just arbitrary—it's rooted in best practices from Python communities, SQLModel documentation, and real-world FastAPI projects. I'll frame it as a comprehensive guide, explaining the rationale step-by-step, with examples tailored to our setup. By the end, you'll see how this promotes clean, scalable code while avoiding common pitfalls like circular imports or fragmented database logic.

## Understanding the Role of Models in Our Project
In our app, SQLModel models serve dual purposes: defining database tables (via SQLAlchemy under the hood) and providing Pydantic-based validation for APIs. They're not just data holders—they're the bridge between our Postgres database and the rest of the codebase. Placing them thoughtfully ensures:
- **Consistency**: Everyone knows where to find schema definitions.
- **Scalability**: As we add schemas or models, the structure grows without chaos.
- **Maintainability**: Easier testing, migrations, and refactoring.

Research from SQLAlchemy and FastAPI ecosystems shows that poor organization leads to issues like duplicated code or hard-to-trace dependencies, especially in feature-based apps like ours. Our centralization strikes a balance: modular enough for growth, but not overly distributed.

## The Current Structure Breakdown
Here's a visual of `src/database/models` for reference:

```
src/database/models
├── __init__.py          # Central imports for easy access (e.g., from .public.user import User)
├── base
│   ├── __init__.py
│   └── base.py          # Global base classes (e.g., for common metadata or mixins like timestamps)
└── public               # Subdir for 'public' schema in Postgres
    ├── __init__.py      # Schema-specific imports
    ├── base.py          # Schema base (e.g., MetaData(schema="public"))
    ├── task.py          # Task model class
    └── user.py          # User model class
```

- **Why a dedicated `models/` dir under `database/`?** This isolates all ORM-related code from features (`api/features/`) and services (`services/`), aligning with layered architectures where data access is a separate concern. In FastAPI projects, this setup complements dependency injection (e.g., sessions from `database/connection.py`), keeping models pure for schema definition.
- **Why subdirectories like `public/`?** For multi-schema Postgres apps, grouping by schema prevents conflicts (e.g., same table name in different schemas). It simulates "directory-level" config via a `base.py` with schema-specific `MetaData`, reducing repetition in model definitions.
- **Why one file per model (e.g., `user.py`)?** SQLModel recommends splitting for complex projects to avoid monolithic files, using `TYPE_CHECKING` for relationships across files. This improves readability—each file focuses on one entity, making it easier to onboard juniors like you.
- **Why base classes?** Global `base/base.py` for shared logic (e.g., ID fields), schema-specific `public/base.py` for things like `metadata = MetaData(schema="public")`. This DRY principle scales better than per-model `__table_args__`.

## Why Not Distribute Models to Features?
In feature-based structures (like our `api/features/`), it might tempt you to put models in `users/models.py`. But avoid this for shared entities— it risks duplication if `User` is used across tasks and health features. Centralization ensures one truth for the schema, simplifying Alembic (which needs all models imported). If a model is truly feature-isolated, we could discuss moving it, but start centralized.

## Handling Common Challenges
- **Circular Imports**: Use string annotations (e.g., `team: Optional["Team"]`) and `from typing import TYPE_CHECKING` for editor support without runtime issues.
- **Migrations**: Import all models in `database/models/__init__.py` and reference in `migrations/env.py` for autogeneration.
- **Testing**: Models here are easy to mock or test independently, without feature coupling.

## Comparison of Organization Approaches
To help you see alternatives, here's a table of common strategies, with why we chose ours:

| Approach | Description | Pros | Cons | Why Not for Us? |
|----------|-------------|------|------|-----------------|
| **Single File (e.g., models.py)** | All models in one file under database/. | Simple for small apps; no import issues. | Becomes unreadable as models grow. | Our multi-schema setup needs better grouping. |
| **Per-Model Files, No Subdirs** | Flat files like user.py, task.py in models/. | Easy navigation; one file per entity. | Clutters dir with many models; no schema grouping. | We use subdirs for logical schema separation. |
| **Feature-Distributed** | Models in api/features/users/models.py. | Aligns with DDD; feature isolation. | Duplication for shared models; complicates migrations. | Our entities cross features—centralization avoids redundancy. |
| **Our Hybrid (Schema-Subdivided)** | Subdirs by schema, files per model, with bases. | Modular, schema-aware; scalable for Postgres. | Slight import complexity (e.g., deeper paths). | Chosen for balance: centralized yet organized. |

## Best Practices Backed by Sources
This structure draws from SQLModel's multi-file guidance, FastAPI tutorials, and Python layout refs. For instance, tutorials centralize models in `app/models.py` but suggest splitting for complexity. In larger apps, subdirs mimic Django's app-based models.py per feature, but we adapt for schemas. Always profile if mapper overhead (from imports) becomes an issue—it's rarely a bottleneck.

If adding models, remember: start simple, refactor as needed. Questions? Let's chat—this is how we build great software together!

## Key Citations
- [Code Structure and Multiple Files - SQLModel](https://sqlmodel.tiangolo.com/tutorial/code-structure/)
- [Best practices for FastAPI projects with SQLModel ORM and PostgreSQL database](https://github.com/fastapi/fastapi/discussions/9936)
- [Best way to organize the folders containing the SQLAlchemy models](https://stackoverflow.com/questions/362998/best-way-to-organize-the-folders-containing-the-sqlalchemy-models)
- [FastAPI with Async SQLAlchemy, SQLModel, and Alembic](https://testdriven.io/blog/fastapi-sqlmodel/)
- [What is the best project structure for a Python application?](https://stackoverflow.com/questions/193161/what-is-the-best-project-structure-for-a-python-application)
- [Python Application Layouts: A Reference](https://realpython.com/python-application-layouts/)