from __future__ import annotations

from pathlib import Path


TEXT_EXTENSIONS = {
    ".md",
    ".markdown",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
}


def find_repo_root(start: Path | None = None) -> Path | None:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".ai" / "rules" / "rules.md").is_file():
            return candidate
        if (candidate / ".ai").is_dir() and (candidate / "AGENTS.md").exists():
            return candidate
    return None


def rel_path(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def list_files(root: Path, exclude_dirs: set[str] | None = None) -> list[Path]:
    excluded = exclude_dirs or {".git", "node_modules", "dist", "build", "__pycache__"}
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in excluded for part in path.parts):
            continue
        if path.is_file():
            files.append(path)
    return files


def list_skill_files(root: Path) -> list[Path]:
    skills_root = root / ".ai" / "skills"
    if not skills_root.exists():
        return []
    return sorted(skills_root.rglob("*.skill.md"))


def list_workflow_files(root: Path) -> list[Path]:
    workflow_root = root / ".ai" / "workflows"
    if not workflow_root.exists():
        return []
    return sorted(path for path in workflow_root.iterdir() if path.is_file())


def find_symlinks(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for base in paths:
        if not base.exists():
            continue
        for path in [base, *base.rglob("*")]:
            if path.is_symlink():
                found.append(path)
    return sorted(found)


def find_utf8_bom_files(root: Path) -> list[Path]:
    bom_files: list[Path] = []
    for path in list_files(root):
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            with path.open("rb") as handle:
                if handle.read(3) == b"\xef\xbb\xbf":
                    bom_files.append(path)
        except OSError:
            continue
    return sorted(bom_files)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

