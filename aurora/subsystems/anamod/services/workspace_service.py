# ======================================================================
# FILE: aurora/subsystems/anamod/services/workspace_service.py
# START: ANAMOD_WORKSPACE_SERVICE
# ======================================================================
import os
import shutil
from dataclasses import dataclass
from typing import Any


WORKSPACE_ROOT = "/app"

IGNORED_WORKSPACE_NAMES = {
    ".git",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    "postgres_data",
    "staticfiles",
    ".venv",
    "venv",
    ".idea",
    ".spyproject",
}

BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pyc",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
}


@dataclass
class WorkspaceOperationError(Exception):
    """Represents a workspace failure with its current HTTP status."""

    message: str
    status: int

    def __str__(self) -> str:
        return self.message


def normalize_workspace_path(file_path: str) -> str:
    """
    Convert a repository-relative path into the current /app-based form.

    This preserves existing behavior. It does not yet enforce containment
    inside WORKSPACE_ROOT.
    """
    if file_path.startswith(f"{WORKSPACE_ROOT}/"):
        return file_path

    return os.path.join(
        WORKSPACE_ROOT,
        file_path.lstrip("/"),
    )


def build_file_tree(path: str = WORKSPACE_ROOT) -> dict[str, Any] | None:
    """Build the hierarchical workspace structure consumed by jsTree."""
    name = os.path.basename(path)

    if os.path.isdir(path):
        try:
            items = os.listdir(path)
        except PermissionError:
            return None

        children = []

        for item_name in items:
            if item_name in IGNORED_WORKSPACE_NAMES:
                continue

            child_node = build_file_tree(
                os.path.join(path, item_name)
            )

            if child_node:
                children.append(child_node)

        return {
            "text": name if name else "Workspace Root",
            "type": "folder",
            "children": children,
            "state": {
                "opened": False,
            },
            "data": {
                "path": path,
            },
        }

    extension = (
        name.rsplit(".", 1)[-1].lower()
        if "." in name
        else ""
    )
    file_type = _get_tree_file_type(extension)

    return {
        "text": name,
        "type": file_type,
        "data": {
            "path": path,
        },
    }


def read_workspace_file(file_path: str) -> str:
    """Read one text file or return the existing binary placeholder."""
    normalized_path = normalize_workspace_path(file_path)

    if not os.path.exists(normalized_path):
        raise WorkspaceOperationError(
            f"File not found: {normalized_path}",
            404,
        )

    if any(
        normalized_path.lower().endswith(extension)
        for extension in BINARY_EXTENSIONS
    ):
        return (
            "# Binary Asset detected. "
            "Contents hidden inside text viewport."
        )

    try:
        with open(
            normalized_path,
            "r",
            encoding="utf-8",
        ) as source_file:
            return source_file.read()
    except Exception as exc:
        raise WorkspaceOperationError(
            f"Could not decode file: {exc}",
            500,
        ) from exc


def create_workspace_node(
    *,
    file_path: str,
    node_type: str = "file",
    content: str = "",
) -> dict[str, str]:
    """Create one workspace file or directory."""
    if node_type not in {"file", "directory"}:
        raise WorkspaceOperationError(
            "Unsupported workspace node type",
            400,
        )

    normalized_path = normalize_workspace_path(file_path)

    if os.path.exists(normalized_path):
        raise WorkspaceOperationError(
            "Workspace node already exists",
            409,
        )

    try:
        if node_type == "directory":
            os.makedirs(normalized_path)

            return {
                "status": "success",
                "type": "directory",
                "path": normalized_path,
            }

        parent_directory = os.path.dirname(normalized_path)

        if (
            parent_directory
            and not os.path.exists(parent_directory)
        ):
            os.makedirs(
                parent_directory,
                exist_ok=True,
            )

        with open(
            normalized_path,
            "w",
            encoding="utf-8",
        ) as destination_file:
            destination_file.write(content)

        return {
            "status": "success",
            "type": "file",
            "path": normalized_path,
        }
    except Exception as exc:
        raise WorkspaceOperationError(
            f"Failed to create workspace node: {exc}",
            500,
        ) from exc


def update_workspace_file(
    *,
    file_path: str,
    content: str,
) -> dict[str, str]:
    """Replace the contents of an existing workspace file."""
    normalized_path = normalize_workspace_path(file_path)

    if not os.path.exists(normalized_path):
        raise WorkspaceOperationError(
            "Target file does not exist",
            404,
        )

    if not os.path.isfile(normalized_path):
        raise WorkspaceOperationError(
            "Target path is not a file",
            400,
        )

    try:
        with open(
            normalized_path,
            "w",
            encoding="utf-8",
        ) as destination_file:
            destination_file.write(content)

        return {
            "status": "success",
            "type": "file",
            "path": normalized_path,
        }
    except Exception as exc:
        raise WorkspaceOperationError(
            f"Failed to update workspace file: {exc}",
            500,
        ) from exc


def rename_workspace_node(
    *,
    file_path: str,
    new_name: str,
) -> dict[str, str]:
    """Rename one existing workspace node within its parent directory."""
    normalized_path = normalize_workspace_path(file_path)

    if not os.path.exists(normalized_path):
        raise WorkspaceOperationError(
            "Target file to rename does not exist",
            404,
        )

    try:
        parent_directory = os.path.dirname(normalized_path)
        new_file_path = os.path.join(
            parent_directory,
            new_name,
        )

        os.rename(
            normalized_path,
            new_file_path,
        )

        return {
            "status": "success",
        }
    except Exception as exc:
        raise WorkspaceOperationError(
            f"Rename tracking failure: {exc}",
            500,
        ) from exc


def delete_workspace_node(file_path: str) -> dict[str, str]:
    """Delete one existing workspace file or directory."""
    normalized_path = normalize_workspace_path(file_path)

    if not os.path.exists(normalized_path):
        raise WorkspaceOperationError(
            "File already absent from disk hierarchy",
            404,
        )

    try:
        if os.path.isdir(normalized_path):
            shutil.rmtree(normalized_path)
        else:
            os.remove(normalized_path)

        return {
            "status": "success",
        }
    except Exception as exc:
        raise WorkspaceOperationError(
            f"Purge validation routine failure: {exc}",
            500,
        ) from exc


def _get_tree_file_type(extension: str) -> str:
    """Return the existing jsTree presentation type for an extension."""
    if extension == "py":
        return "python"

    if extension in {"html", "htm"}:
        return "html"

    if extension == "css":
        return "css"

    if extension in {"js", "ts"}:
        return "js"

    if extension in {
        "json",
        "yaml",
        "yml",
        "ini",
        "cfg",
    }:
        return "config"

    return "file"
# ======================================================================
# FILE: aurora/subsystems/anamod/services/workspace_service.py
# END: ANAMOD_WORKSPACE_SERVICE
# ======================================================================