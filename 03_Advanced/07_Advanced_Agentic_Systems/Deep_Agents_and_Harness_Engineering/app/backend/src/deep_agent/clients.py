"""Shared Databricks client singletons."""

from databricks.sdk import WorkspaceClient


_workspace_client: WorkspaceClient | None = None


def get_workspace_client() -> WorkspaceClient:
    """Return the process-wide Databricks WorkspaceClient."""
    global _workspace_client
    if _workspace_client is None:
        _workspace_client = WorkspaceClient()
    return _workspace_client
