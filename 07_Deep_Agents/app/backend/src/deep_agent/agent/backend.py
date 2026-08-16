"""Deep Agents filesystem backend factory."""

from deepagents.backends import FilesystemBackend, LocalShellBackend

from deep_agent.config import PROJECTS_DIR, USE_SANDBOX


def build_backend():
    if USE_SANDBOX:
        return LocalShellBackend(root_dir=PROJECTS_DIR)
    return FilesystemBackend(root_dir=PROJECTS_DIR, virtual_mode=True)
