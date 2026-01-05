import os
import pathspec
from typing import List
from pathlib import Path


def load_gitignore_patterns(root_dir: Path) -> pathspec.PathSpec:
    """
    Loads .gitignore patterns from the root directory if it exists.
    Always includes default ignore patterns for .geas, __pycache__, and .git.
    """
    gitignore_path = root_dir / ".gitignore"
    patterns = []

    # Always ignore these
    default_ignores = [".geas/", "__pycache__/", ".git/", "*.pyc"]
    patterns.extend(default_ignores)

    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            patterns.extend(f.readlines())

    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)


def walk_source_files(root_dir: Path, scope_dirs: List[str]) -> List[str]:
    """
    Recursively walks the specified scope directories, filtering files based on .gitignore
    and default ignore patterns.

    Args:
        root_dir: The root directory of the project.
        scope_dirs: List of directory names (relative to root) to include in the walk.

    Returns:
        List of file paths relative to root_dir.
    """
    spec = load_gitignore_patterns(root_dir)
    collected_files = []

    # Ensure scope directories exist
    valid_scope_dirs = []
    for d in scope_dirs:
        p = root_dir / d
        if p.exists() and p.is_dir():
            valid_scope_dirs.append(d)
        # We silently skip missing directories as per previous discussion ("just raise a warning" handled by caller or implied here)
        # Actually, the user said "just raise a warning" for missing scope.
        # I will let the caller handle warnings if needed, here I just walk what exists.

    for scope_dir in valid_scope_dirs:
        # Walk logic
        base_path = root_dir / scope_dir

        # We walk everything under the scope_dir
        for root, dirs, files in os.walk(base_path):
            # Calculate relative path from project root for filtering
            rel_root = Path(root).relative_to(root_dir)

            # Filter directories to prevent traversing into ignored ones
            # pathspec.match_file returns True if it matches an ignore pattern
            # We need to modify 'dirs' in-place to prune the walk

            # Filter dirs
            # We must check each dir against the spec.
            # The spec expects paths relative to the root of the gitignore context (project root)
            dirs[:] = [
                d
                for d in dirs
                if not spec.match_file(str(rel_root / d) + "/")
                # appending "/" helps pathspec identify it as directory if the pattern ends with /
            ]

            for file in files:
                file_rel_path = rel_root / file
                if not spec.match_file(str(file_rel_path)):
                    collected_files.append(str(file_rel_path))

    return sorted(collected_files)
