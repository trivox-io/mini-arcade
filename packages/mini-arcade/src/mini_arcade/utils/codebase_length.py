"""
Get the length of the whole codebase, in lines of code (LOC) and in bytes,
broken down by language (Python and C/C++).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Canonical package name → relative path from the monorepo root.
# Using explicit source paths avoids counting stale installed artifacts for
# packages that are not installed in editable mode (e.g. mini_arcade_native_backend).
_PACKAGE_SRC_PATHS: dict[str, str] = {
    "mini_arcade": "packages/mini-arcade/src/mini_arcade",
    "mini_arcade_core": "packages/mini-arcade-core/src/mini_arcade_core",
    "mini_arcade_pygame_backend": (
        "packages/mini-arcade-pygame-backend/src/mini_arcade_pygame_backend"
    ),
    "mini_arcade_native_backend": (
        "packages/mini-arcade-native-backend/src/mini_arcade_native_backend"
    ),
}

# C++ source roots relative to the monorepo root (all .cpp / .h / .hpp files
# found recursively under these directories are counted).
_CPP_SRC_PATHS: tuple[str, ...] = (
    "packages/mini-arcade-native-backend/src/native",
    "packages/mini-arcade-native-backend/cpp",
)

_PYTHON_GLOBS: tuple[str, ...] = ("*.py",)
_CPP_GLOBS: tuple[str, ...] = ("*.cpp", "*.cc", "*.cxx", "*.h", "*.hpp")


@dataclass
class CodebaseStats:
    """Aggregated line and byte counts split by language."""

    python_loc: int = 0
    python_bytes: int = 0
    cpp_loc: int = 0
    cpp_bytes: int = 0

    @property
    def total_loc(self) -> int:
        """
        Total lines of code across all languages.

        :return: Total LOC.
        :rtype: int
        """
        return self.python_loc + self.cpp_loc

    @property
    def total_bytes(self) -> int:
        """
        Total bytes of code across all languages.

        :return: Total bytes.
        :rtype: int
        """
        return self.python_bytes + self.cpp_bytes

    def __iadd__(self, other: "CodebaseStats") -> "CodebaseStats":
        self.python_loc += other.python_loc
        self.python_bytes += other.python_bytes
        self.cpp_loc += other.cpp_loc
        self.cpp_bytes += other.cpp_bytes
        return self


def _count_files(root: Path, globs: tuple[str, ...]) -> tuple[int, int]:
    """Return (loc, bytes) for all files matching *globs* under *root*."""
    total_loc = 0
    total_bytes = 0
    for glob in globs:
        for file_path in root.rglob(glob):
            if not file_path.is_file():
                continue
            with file_path.open("r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            lines = content.count("\n")
            if content and not content.endswith("\n"):
                lines += 1
            total_loc += lines
            total_bytes += len(content.encode("utf-8"))
    return total_loc, total_bytes


def _repo_root() -> Path:
    """Return the monorepo root (the directory that contains the 'packages/' folder)."""
    here = Path(__file__).resolve()
    for candidate in here.parents:
        if (candidate / "packages").is_dir():
            return candidate
    raise RuntimeError("Could not locate monorepo root from %s" % here)


def codebase_length(packages: list[str]) -> CodebaseStats:
    """
    Count Python and C++ LOC/bytes for the specified packages.

    Resolves each package to its monorepo source tree so that the count
    always reflects the actual source, regardless of install mode.

    :param packages: A list of package names to analyze.
    :type packages: list[str]
    :return: CodebaseStats with per-language and total counts.
    :rtype: CodebaseStats
    """
    root = _repo_root()
    stats = CodebaseStats()

    for package in packages:
        rel = _PACKAGE_SRC_PATHS.get(package)
        if rel is None:
            raise ValueError(
                f"Unknown package '{package}'. "
                f"Add it to _PACKAGE_SRC_PATHS in {__file__}."
            )
        package_path = root / rel
        if not package_path.is_dir():
            raise FileNotFoundError(
                f"Source directory not found for '{package}': {package_path}"
            )
        loc, bytes_ = _count_files(package_path, _PYTHON_GLOBS)
        stats.python_loc += loc
        stats.python_bytes += bytes_

    for rel in _CPP_SRC_PATHS:
        cpp_path = root / rel
        if not cpp_path.is_dir():
            continue
        loc, bytes_ = _count_files(cpp_path, _CPP_GLOBS)
        stats.cpp_loc += loc
        stats.cpp_bytes += bytes_

    return stats


if __name__ == "__main__":
    packages_codebase = [
        "mini_arcade",
        "mini_arcade_core",
        "mini_arcade_pygame_backend",
        "mini_arcade_native_backend",
    ]
    s = codebase_length(packages_codebase)
    print(f"Python : {s.python_loc:>7,} lines  {s.python_bytes:>10,} bytes")
    print(f"C++    : {s.cpp_loc:>7,} lines  {s.cpp_bytes:>10,} bytes")
    print(f"Total  : {s.total_loc:>7,} lines  {s.total_bytes:>10,} bytes")
