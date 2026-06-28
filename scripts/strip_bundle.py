#!/usr/bin/env python3
"""
strip_bundle.py — Walk a skill folder and remove files that should not ship.

Removes:
  - Version control metadata: .git/, .gitignore (kept if explicitly required), .gitattributes
  - OS metadata: .DS_Store, Thumbs.db, .Spotlight-V100/, .Trashes/
  - Editor metadata: .vscode/, .idea/, .swp, .swo, *~
  - Build artifacts: node_modules/, __pycache__/, .pytest_cache/, dist/, build/, target/
  - Cache dirs: .cache/, .mypy_cache/, .ruff_cache/, .tox/
  - Logs and temp files: *.log, *.tmp, *.bak, *.swp
  - Credentials and secrets: .env, .env.*, *.key, *.pem, *.p12, *.pfx,
                              credentials.*, secrets.*, *.keystore

Keeps:
  - SKILL.md, skill-card.md, README.md, README.zh-cn.md, RELEASE_NOTES.md
  - Anything under references/, scripts/, assets/, templates/, config/
  - LICENSE, LICENSE.md, NOTICE
  - .gitignore and .clawhubignore (used for explicit exclusions)

Logs every removal. Exits non-zero if it had to remove any file whose name
matches a credential pattern, so the user can review before publishing.

Usage:
  python3 strip_bundle.py <skill-dir> [--dry-run] [--no-fail-on-credentials]

Exit codes:
  0  Bundle clean (or dry-run only)
  1  Removed at least one credential-looking file; review before publishing
  2  Invalid arguments or skill-dir does not exist
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import shutil
import sys
from pathlib import Path
from typing import Iterable

# Always-remove directory names.
REMOVE_DIRS = {
    ".git",
    ".vscode",
    ".idea",
    ".playwright-mcp",
    ".DS_Store",  # technically a file, but listed here for clarity
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".cache",
    "dist",
    "build",
    "target",
    ".Spotlight-V100",
    ".Trashes",
    ".fseventsd",
    ".claude",  # session caches; keep .claude/settings.json if needed via explicit allowlist
    "output",  # generated files (e.g. PDF/HTML output from a rendering skill)
}

# Always-remove file name patterns (case-insensitive substring / glob).
REMOVE_FILE_PATTERNS = [
    ".DS_Store",
    "Thumbs.db",
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".env.test",
]

# Glob-style patterns for files we never want to ship.
REMOVE_GLOBS = [
    "*.log",
    "*.tmp",
    "*.bak",
    "*.swp",
    "*.swo",
    "*~",
    "*.key",
    "*.pem",
    "*.p12",
    "*.pfx",
    "*.keystore",
    "*.jks",
    "credentials.*",
    "secrets.*",
    "secret.*",
    ".envrc",
]

# Always-keep file names at the root.
KEEP_ROOT_FILES = {
    "SKILL.md",
    "skill.md",  # legacy alias
    "skills.md",  # legacy alias
    "skill-card.md",
    "README.md",
    "README.zh-cn.md",
    "RELEASE_NOTES.md",
    "LICENSE",
    "LICENSE.md",
    "NOTICE",
    ".gitignore",
    ".clawhubignore",
    ".gitattributes",
    "package.json",  # only if it exists for runtime, will warn if found
    "pyproject.toml",  # same
}

# Always-keep subdirectories (relative to skill root).
KEEP_DIRS = {
    "references",
    "scripts",
    "assets",
    "templates",
    "config",
    "examples",
    "tests",
}

# Patterns that, if removed, escalate the exit code (so the user must review).
CREDENTIAL_GLOBS = {
    ".env",
    ".env.*",
    "*.key",
    "*.pem",
    "*.p12",
    "*.pfx",
    "*.keystore",
    "*.jks",
    "credentials.*",
    "secrets.*",
    "secret.*",
}


def is_credential(path: Path) -> bool:
    """Return True if path matches any credential pattern."""
    name = path.name
    for pattern in CREDENTIAL_GLOBS:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def should_remove(path: Path, root: Path) -> str | None:
    """Return a reason string if path should be removed, else None."""
    # Don't touch the root itself.
    if path == root:
        return None

    rel = path.relative_to(root)

    parts = rel.parts

    # If any parent directory is in REMOVE_DIRS, remove.
    for part in parts[:-1]:
        if part in REMOVE_DIRS:
            return f"parent directory '{part}/' is excluded"

    name = path.name

    # Directory matches.
    if path.is_dir():
        if name in REMOVE_DIRS:
            return f"directory '{name}/' is excluded"

        # Allow explicitly-kept directories at any depth.
        # (We already checked parents; if the dir itself is kept, allow it.)
        if name in KEEP_DIRS and len(parts) > 1 and parts[0] == name:
            return None
        return None

    # File at root: check keep list first.
    if len(parts) == 1:
        if name in KEEP_ROOT_FILES:
            return None

    # Subdirectory files: keep if under a KEEP_DIRS.
    if len(parts) > 1 and parts[0] in KEEP_DIRS:
        return None

    # File name patterns.
    if name in REMOVE_FILE_PATTERNS:
        return f"file name '{name}' is in the exclusion list"

    # Glob patterns.
    for pattern in REMOVE_GLOBS:
        if fnmatch.fnmatch(name, pattern):
            return f"matches pattern '{pattern}'"

    return None


def walk_and_strip(root: Path, dry_run: bool) -> tuple[list[tuple[Path, str]], bool]:
    """Walk root, collect (path, reason) for removals. Return removals + credential flag."""
    removals: list[tuple[Path, str]] = []
    had_credential = False

    # Walk top-down so we can prune REMOVE_DIRS without descending into them.
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        current = Path(dirpath)
        rel_parts = current.relative_to(root).parts

        # Prune: remove directories in-place so os.walk doesn't descend.
        pruned: list[str] = []
        for d in list(dirnames):
            full = current / d
            reason = should_remove(full, root)
            if reason is not None:
                removals.append((full, reason))
                if any(p in str(full).lower() for p in [".env", ".key", ".pem", "secret", "credential"]):
                    had_credential = True
                dirnames.remove(d)
            else:
                pruned.append(d)
        dirnames[:] = pruned

        # Files in this directory.
        for f in filenames:
            full = current / f
            reason = should_remove(full, root)
            if reason is not None:
                removals.append((full, reason))
                if is_credential(full):
                    had_credential = True

    return removals, had_credential


def perform_removals(removals: Iterable[tuple[Path, str]], dry_run: bool) -> None:
    for path, reason in removals:
        if dry_run:
            print(f"[DRY-RUN] would remove: {path}  ({reason})")
            continue
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"removed: {path}  ({reason})")
        except OSError as e:
            print(f"FAILED to remove {path}: {e}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Strip non-bundle files from a skill folder before publishing."
    )
    parser.add_argument("skill_dir", type=Path, help="Path to the skill folder.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be removed without removing anything.",
    )
    parser.add_argument(
        "--no-fail-on-credentials",
        action="store_true",
        help="Exit 0 even if credential-looking files were removed (use only if you have reviewed them).",
    )
    args = parser.parse_args()

    root = args.skill_dir.resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    if not (root / "SKILL.md").exists() and not (root / "skill.md").exists():
        print(f"warning: no SKILL.md found at {root}", file=sys.stderr)

    removals, had_credential = walk_and_strip(root, args.dry_run)

    if not removals:
        print(f"clean: nothing to remove in {root}")
        return 0

    perform_removals(removals, args.dry_run)

    print(f"\nsummary: {len(removals)} item(s) {'would be' if args.dry_run else ''} removed")

    if had_credential and not args.no_fail_on_credentials and not args.dry_run:
        print(
            "\nWARNING: credential-looking files were removed. "
            "Review the list above before publishing.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())