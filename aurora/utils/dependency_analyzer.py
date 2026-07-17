# ======================================================================
# FILE: aurora/utils/dependency_analyzer.py (PATCH 1 OF 1)
# START: DETERMINISTIC_COMPONENT_DEPENDENCY_ANALYSIS
# ======================================================================
"""Read-only AST analysis of repository-local component dependencies."""

import ast
from pathlib import Path, PurePosixPath

from django.conf import settings
from django.db.models import QuerySet

from aurora.models import ComponentRegistry


class DependencyAnalyzer:
    """
    Resolve one registered Python component's repository-local imports.

    This service performs no PostgreSQL mutation, Neo4j mutation,
    repository discovery, or code execution.
    """

    def __init__(self, repository_root: str | Path | None = None):
        configured_root = repository_root or settings.BASE_DIR
        self.repository_root = Path(configured_root).resolve()

    @staticmethod
    def _normalize_path(file_path: str) -> str:
        """Return one normalized repository-relative POSIX path."""
        return file_path.strip().replace("\\", "/").lstrip("/")

    def _absolute_source_path(self, file_path: str) -> Path:
        """Resolve and validate one repository-relative source path."""
        normalized_path = self._normalize_path(file_path)
        source_path = (self.repository_root / normalized_path).resolve()

        try:
            source_path.relative_to(self.repository_root)
        except ValueError as error:
            raise ValueError(
                f"Component path escapes repository root: {file_path}"
            ) from error

        return source_path

    @staticmethod
    def _module_candidates(module_name: str) -> tuple[str, ...]:
        """Return possible repository paths for one Python module name."""
        module_path = module_name.strip(".").replace(".", "/")

        if not module_path:
            return ()

        return (
            f"{module_path}.py",
            f"{module_path}/__init__.py",
        )

    @staticmethod
    def _component_package_parts(file_path: str) -> list[str]:
        """Return the source component's containing Python package parts."""
        path = PurePosixPath(file_path)

        if path.name == "__init__.py":
            return list(path.parent.parts)

        return list(path.parent.parts)

    def _resolve_import_from(
        self,
        *,
        source_path: str,
        node: ast.ImportFrom,
    ) -> set[str]:
        """Return module names represented by one ImportFrom node."""
        resolved_modules: set[str] = set()
        module_parts = node.module.split(".") if node.module else []

        if node.level:
            package_parts = self._component_package_parts(source_path)
            parent_count = node.level - 1

            if parent_count > len(package_parts):
                return resolved_modules

            if parent_count:
                package_parts = package_parts[:-parent_count]

            base_parts = package_parts + module_parts
        else:
            base_parts = module_parts

        if base_parts:
            resolved_modules.add(".".join(base_parts))

        for alias in node.names:
            if alias.name == "*":
                continue

            alias_parts = base_parts + alias.name.split(".")

            if alias_parts:
                resolved_modules.add(".".join(alias_parts))

        return resolved_modules

    def extract_import_modules(
        self,
        component: ComponentRegistry,
    ) -> tuple[str, ...]:
        """Parse and return deterministic imported module names."""
        normalized_path = self._normalize_path(component.file_path)

        if not normalized_path.endswith(".py"):
            return ()

        source_path = self._absolute_source_path(normalized_path)

        if not source_path.is_file():
            raise FileNotFoundError(
                f"Registered component source does not exist: {normalized_path}"
            )

        try:
            source = source_path.read_text(encoding="utf-8")
            syntax_tree = ast.parse(source, filename=normalized_path)
        except UnicodeDecodeError as error:
            raise ValueError(
                f"Component source is not valid UTF-8: {normalized_path}"
            ) from error
        except SyntaxError as error:
            raise ValueError(
                f"Component source contains invalid Python syntax: "
                f"{normalized_path}: {error}"
            ) from error

        imported_modules: set[str] = set()

        for node in ast.walk(syntax_tree):
            if isinstance(node, ast.Import):
                imported_modules.update(
                    alias.name
                    for alias in node.names
                    if alias.name
                )
            elif isinstance(node, ast.ImportFrom):
                imported_modules.update(
                    self._resolve_import_from(
                        source_path=normalized_path,
                        node=node,
                    )
                )

        return tuple(sorted(imported_modules))

    def resolve_dependencies(
        self,
        component: ComponentRegistry,
    ) -> list[ComponentRegistry]:
        """
        Resolve imported modules to active registered repository components.

        External and standard-library imports are ignored because they do not
        resolve to authoritative ComponentRegistry file paths.
        """
        if component.id is None:
            raise ValueError(
                "ComponentRegistry must be persisted before dependency analysis."
            )

        candidate_paths: set[str] = set()

        for module_name in self.extract_import_modules(component):
            candidate_paths.update(self._module_candidates(module_name))

        if not candidate_paths:
            return []

        dependencies: QuerySet[ComponentRegistry] = (
            ComponentRegistry.objects
            .filter(
                status="ACTIVE",
                file_path__in=sorted(candidate_paths),
            )
            .exclude(id=component.id)
            .order_by("file_path")
        )

        return list(dependencies)
# ======================================================================
# END: DETERMINISTIC_COMPONENT_DEPENDENCY_ANALYSIS (PATCH 1 OF 1)
# ======================================================================

