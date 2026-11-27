"""Check built wheel contents and public typing in a clean external environment."""

import shutil
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZipFile


def find_wheel(dist: Path, name: str) -> Path:
    """Return the single built wheel for a package and reject missing or stale builds."""
    matches = sorted(dist.rglob(f"elims_{name}-*.whl"))
    if len(matches) != 1:
        found = ", ".join(str(match.relative_to(dist)) for match in matches) or "none"
        raise RuntimeError(f"Expected exactly one elims_{name} wheel under {dist}, found: {found}")
    return matches[0]


def main() -> None:
    """Install only built wheels and verify their contents and public imports with Mypy."""
    root = Path(__file__).resolve().parents[1]
    packages = ("cli", "com", "database", "instruments", "utils")
    wheels = [find_wheel(root / "dist", name) for name in packages]
    for name, wheel in zip(packages, wheels, strict=True):
        with ZipFile(wheel) as archive:
            entries = archive.namelist()
        if f"elims_{name}/py.typed" not in entries:
            raise RuntimeError(f"Missing py.typed in {wheel.name}")
        if not any(entry.endswith(".dist-info/licenses/LICENSE") for entry in entries):
            raise RuntimeError(f"Missing LICENSE in {wheel.name}")
    with tempfile.TemporaryDirectory(prefix="elims-wheel-check-") as directory:
        environment = Path(directory) / "venv"
        python = environment / ("Scripts/python.exe" if __import__("os").name == "nt" else "bin/python")
        uv = shutil.which("uv")
        if uv is None:
            raise RuntimeError("uv is required to validate built wheels")
        subprocess.run([uv, "venv", str(environment), "--python", "3.13"], check=True)  # noqa: S603
        subprocess.run(  # noqa: S603
            [uv, "pip", "install", "--python", str(python), "mypy", *map(str, wheels)], check=True
        )
        subprocess.run(  # noqa: S603
            [
                str(python),
                "-m",
                "mypy",
                "--strict",
                "-c",
                "from elims_database import Database; from elims_com import Message; "
                "from elims_utils import utc_now; from elims_instruments import Instrument; "
                "from elims_cli.app import app; message: Message = Message(subject='check'); utc_now()",
            ],
            cwd=directory,
            check=True,
        )


if __name__ == "__main__":
    main()
