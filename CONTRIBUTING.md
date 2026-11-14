# Contributing mods

When submissions open, place each mod under `mods/<id>/` and submit a pull request. Include `mod.toml`, a 256 × 144 preview, content, usage notes, the SPDX license identifier, and provenance for each third-party asset.

Use data-only content. Declare dependencies and the supported game version. Run `python tools/validate_catalog.py` from the repository root with Python 3.11 or newer. The same check runs in GitHub Actions and validates manifest fields, IDs, version syntax, SPDX licenses, provenance, supported file extensions, JSON syntax, and PNG headers and dimensions. Full schema and dependency validation, sprite lint, and DCO enforcement are planned.

Rights holders can request removal through the catalog maintainers. Include the mod ID and version, the affected material, and a description of the rights issue.
