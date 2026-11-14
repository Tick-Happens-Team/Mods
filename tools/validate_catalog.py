"""Run basic, dependency-free checks on proposed catalog submissions."""

import json
import re
import struct
import sys
import tomllib
from pathlib import Path


LICENSES = {"CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0", "MIT", "MPL-2.0"}
EXTENSIONS = {".toml", ".json", ".png", ".ogg", ".md"}
MOD_ID = re.compile(r"[a-z0-9][a-z0-9_-]*")
SEMVER_CORE = r"(?:0|[1-9][0-9]*)"
SEMVER = re.compile(
    rf"{SEMVER_CORE}\.{SEMVER_CORE}\.{SEMVER_CORE}"
    r"(?:-(?P<prerelease>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)
PNG_HEADER = b"\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR"


def png_size(file: Path) -> tuple[int, int]:
    with file.open("rb") as stream:
        header = stream.read(24)
    if len(header) != 24 or not header.startswith(PNG_HEADER):
        raise ValueError(f"{file}: expected a PNG image")
    return struct.unpack(">II", header[16:24])


def validate_mod(mod: Path) -> None:
    if mod.is_symlink() or not mod.is_dir() or not MOD_ID.fullmatch(mod.name):
        raise ValueError(f"{mod}: expected a directory named with a lowercase mod ID")

    files = []
    for path in mod.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"{path}: symbolic links are prohibited")
        if path.is_file():
            if path.suffix.lower() not in EXTENSIONS:
                raise ValueError(f"{path}: unsupported file type")
            files.append(path)

    try:
        with (mod / "mod.toml").open("rb") as stream:
            manifest = tomllib.load(stream)
    except FileNotFoundError as error:
        raise ValueError(f"{mod}: missing mod.toml") from error

    if type(manifest.get("schema")) is not int or manifest["schema"] != 1:
        raise ValueError(f"{mod}: schema must be 1")
    if manifest.get("id") != mod.name:
        raise ValueError(f"{mod}: manifest ID must match the directory name")
    for field in ("name", "version", "game", "license", "description", "preview"):
        value = manifest.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{mod}: {field} must be a nonempty string")
    version = SEMVER.fullmatch(manifest["version"])
    if not version or any(
        identifier.isdigit() and len(identifier) > 1 and identifier.startswith("0")
        for identifier in (version["prerelease"] or "").split(".")
    ):
        raise ValueError(f"{mod}: version must have SemVer syntax")
    if manifest["license"] not in LICENSES:
        raise ValueError(f"{mod}: unsupported SPDX license {manifest['license']!r}")
    authors = manifest.get("authors")
    if not isinstance(authors, list) or not authors or any(
        not isinstance(author, str) or not author.strip() for author in authors
    ):
        raise ValueError(f"{mod}: authors must contain at least one nonempty name")
    if manifest.get("multiplayer") not in ("required", "client-only"):
        raise ValueError(f"{mod}: multiplayer must be required or client-only")
    provenance = manifest.get("provenance")
    if not isinstance(provenance, dict) or type(provenance.get("ai_generated")) is not bool:
        raise ValueError(f"{mod}: provenance.ai_generated must be true or false")

    preview = manifest["preview"]
    if preview != "preview.png" or mod / preview not in files:
        raise ValueError(f"{mod}: add the preview image as preview.png")
    if png_size(mod / preview) != (256, 144):
        raise ValueError(f"{mod}: preview.png must measure 256 × 144")
    if not any(path.is_relative_to(mod / "content") for path in files):
        raise ValueError(f"{mod}: add data files under content/")

    for path in files:
        if path.suffix.lower() == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (ValueError, UnicodeError) as error:
                raise ValueError(f"{path}: {error}") from error
        if path.suffix.lower() == ".png":
            width, height = png_size(path)
            if not (1 <= width <= 4096 and 1 <= height <= 4096):
                raise ValueError(f"{path}: image sides must be between 1 and 4096 pixels")


def main() -> int:
    catalog = Path(__file__).resolve().parents[1] / "mods"
    if catalog.is_symlink() or (catalog.exists() and not catalog.is_dir()):
        print("mods must be a catalog directory", file=sys.stderr)
        return 1
    mods = sorted(catalog.iterdir()) if catalog.is_dir() else []
    failed = False
    for mod in mods:
        try:
            validate_mod(mod)
        except (OSError, ValueError) as error:
            print(error, file=sys.stderr)
            failed = True
    if failed:
        return 1
    print(f"Validated {len(mods)} mod package(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
