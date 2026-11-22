"""Aggregate component-owned pages without maintaining a second copy."""

from pathlib import Path

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files


def on_files(files: Files, config: MkDocsConfig) -> Files:
    """Expose application and package documentation inside the project site."""
    root = Path(__file__).resolve().parents[1]
    components = {
        "components/backend": root / "backend" / "docs",
        "components/frontend": root / "frontend" / "docs",
    }
    components.update(
        {f"packages/{directory.parent.name}": directory for directory in sorted((root / "packages").glob("*/docs"))}
    )

    for destination, directory in components.items():
        if not directory.is_dir():
            continue
        for source in sorted(directory.rglob("*.md")):
            relative = source.relative_to(directory).as_posix()
            files.append(
                File.generated(
                    config,
                    f"{destination}/{relative}",
                    content=source.read_text(encoding="utf-8"),
                )
            )
    return files
