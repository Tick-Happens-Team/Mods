---
name: validate-mod
description: Review or prepare a community mod submission for the TickHappens Mods catalog (data-only mods under mods/<id>/). Use when a PR adds or updates a mod, or when packaging example mods.
---

Follow the workspace AGENTS.md, CONTRIBUTING.md and the mod format in Game/docs/MODDING.md (content JSON shapes match Game/content/core: characters, items with rarity and stat mods, enemies, waves, rules).

1. Layout: `mods/<id>/mod.toml`, `preview.png` (256×144), `content/**` (JSON, PNG + `.sprite.json`, OGG), `README.md`. No code, no symlinks; allowed extensions: .toml .json .png .ogg .md.
2. Manifest: lowercase `id` that never changes, semver `version`, `game` range, SPDX `license` from the allowlist (CC0-1.0, CC-BY-4.0, CC-BY-SA-4.0, MIT, MPL-2.0), `multiplayer` = required | client-only, `[provenance]` with `ai_generated` and every third-party source.
3. Run `python tools/validate_catalog.py` from the repository root (Python 3.11+); it must pass. CI runs the same check.
4. Load-test the content against the game: copy the mod's `content/` next to a copy of `Game/content/core` in `D:\tickhappens\.tmp\modcheck\` and load it with the Game ContentLoader (Game `build-test` skill); every validation error names the file, id and field.
5. Sprites must pass Game AssetTool lint (`dotnet run --project tools/TickHappens.AssetTool -- lint <png> <fw> <fh>` from Game): no off-palette colors, no soft alpha, no upscaled art.
6. Reject content that copies third-party IP, lacks provenance, or targets real people. Rights holders can request removal (CONTRIBUTING.md).
Report findings as a PR review; never merge without the owner's approval.
