"""Project tools — write code/files into a Unity Catalog Volume."""

import io
import os
import re

from deep_agent.clients import get_workspace_client
from deep_agent.config import PROJECTS_DIR, VOLUME_BASE


def _slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    return slug.strip("-")


def name_project(project_name: str) -> str:
    """Create a project folder with the given name.

    Call this FIRST before writing any files. The name should be a short,
    descriptive, lowercase slug using hyphens (e.g., 'email-validator',
    'todo-api', 'csv-parser').

    Args:
        project_name: A short, lowercase, hyphenated name for the project.
    """
    slug = _slugify(project_name)
    if not slug:
        return "Error: Could not create a valid project name."

    os.makedirs(os.path.join(PROJECTS_DIR, slug), exist_ok=True)

    try:
        volume_path = f"{VOLUME_BASE}/{slug}/.project"
        get_workspace_client().files.upload(
            volume_path,
            io.BytesIO(f"project: {slug}\n".encode()),
            overwrite=True,
        )
    except Exception as e:
        return f"Project '{slug}' created locally but Volume write failed: {e}"

    return (
        f"Project folder created: {slug}/\n"
        f"Volume path: {VOLUME_BASE}/{slug}/\n"
        f"Use write_project_file('{slug}', 'main.py', '...code...') to write files."
    )


def write_project_file(project_name: str, file_name: str, content: str) -> str:
    """Write a file to a project folder in the Databricks Volume.

    This persists the file in Unity Catalog Volume storage so it survives
    app redeployments. Always call name_project() first to create the project.

    Args:
        project_name: The project slug (e.g., 'csv-parser-cli').
        file_name: The file name including extension (e.g., 'main.py', 'README.md').
        content: The full file content to write.
    """
    slug = _slugify(project_name)
    volume_path = f"{VOLUME_BASE}/{slug}/{file_name}"
    try:
        get_workspace_client().files.upload(
            volume_path,
            io.BytesIO(content.encode("utf-8")),
            overwrite=True,
        )
        return f"Written: {volume_path} ({len(content)} bytes)"
    except Exception as e:
        return f"Failed to write {volume_path}: {e}"


def list_project_files(project_name: str) -> str:
    """List all files in a project folder in the Databricks Volume.

    Args:
        project_name: The project slug (e.g., 'csv-parser-cli').
    """
    slug = _slugify(project_name)
    volume_dir = f"{VOLUME_BASE}/{slug}/"
    try:
        files = list(get_workspace_client().files.list_directory_contents(volume_dir))
        if not files:
            return f"No files in {volume_dir}"
        lines = [f"- {f.name} ({f.file_size} bytes)" for f in files if f.name != ".project"]
        return f"Files in {volume_dir}:\n" + "\n".join(lines)
    except Exception as e:
        return f"Failed to list {volume_dir}: {e}"
