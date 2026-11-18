"""Git directory lookups that read ``.git`` markers instead of running git."""

from pathlib import Path
from typing import Optional


def repo_common_dir(project_path: Path) -> Optional[Path]:
    """Resolve the Git directory a checkout shares with its linked worktrees."""
    git_dir = project_path / ".git"
    if git_dir.is_file():
        marker = git_dir.read_text(encoding="utf-8", errors="surrogateescape").strip()
        if not marker.startswith("gitdir:") or not marker[7:].strip():
            return None
        git_dir = project_path / marker[7:].strip()
    elif not git_dir.is_dir():
        return None
    try:
        common = (
            (git_dir / "commondir").read_text(encoding="utf-8", errors="surrogateescape").strip()
        )
    except FileNotFoundError:
        return git_dir
    return git_dir / common if common else None
