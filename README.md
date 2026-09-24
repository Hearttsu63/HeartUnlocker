# HeartzinUnlocker — Bedrock Achievement Reactivator

**Restore achievements on Minecraft Bedrock worlds that used cheats, Creative mode or Behavior Packs — without losing your world.**

Credits: **@Heartzin** — https://t.me/Heartzin  
Based on [058f9cf1/minecraft_bedrock_reenable_achievements](https://github.com/058f9cf1/minecraft_bedrock_reenable_achievements) — rewritten with a clean interactive menu, backup and pack handling.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey) ![License](https://img.shields.io/badge/License-GPL--3.0-green)

---

## Features

- **One-click reactivation** — resets `hasBeenLoadedInCreative`, `cheatsEnabled`, `commandsEnabled`, `hasLockedBehaviorPack`, `hasLockedResourcePack`, `isFromLockedTemplate` and `GameType` to Survival
- **Smart pack handling** — detects `world_behavior_packs.json`; asks if you want to keep or remove packs (keeping packs still blocks achievements on modern Bedrock)
- **Interactive menu** — lists all local worlds (`%AppData%\Minecraft Bedrock\Users\*\games\com.mojang\minecraftWorlds`), shows `BLOCKED / OK` status and pack count
- **Batch mode** — `0` reactivates every world at once, or pass paths as args / drag & drop `.mcworld` / `level.dat`
- **Safe** — creates `level.dat.bak` and `world_behavior_packs.json.bak` on first run; never overwrites existing backups

## Requirements

- Windows 10/11 + Minecraft for Windows (Bedrock)
- Python 3.8+ with `amulet-nbt` and `amulet-core`:
  ```powershell
  py -3 -m pip install amulet-nbt amulet-core
  ```
- Or just use the standalone `HeartzinUnlocker.exe` in `dist/` (no Python needed)

## Quick Start

### Option A — Python (one-liner via GitHub)

```powershell
# install directly from GitHub
py -3 -m pip install git+https://github.com/Hearttsu63/HeartzinUnlocker.git

# run
heartzin-unlocker
# or
py -3 -m reativar_conquistas

# force remove packs:
py -3 -m heartzin_unlocker --remove-packs
# single world / drag & drop:
py -3 reativar_conquistas.py "C:\...\minecraftWorlds\My World"
```

### Option B — EXE (no Python needed)

1. Close Minecraft completely
2. Double-click `dist\HeartzinUnlocker.exe`
3. Choose world number (`0` for all) → if packs detected, choose `y` to remove them → Enter

## How it works

`level.dat` is `8-byte header (version + length) + little-endian NBT`. The tool loads it with `amulet_nbt`, zeroes the blocking flags, repacks the header and writes back. Auto-creates `.bak` files. Removing packs clears `world_behavior_packs.json` to `[]` and deletes `level.dat_old`.

Flags reset: `GameType`, `cheatsEnabled`, `commandsEnabled`, `hasBeenLoadedInCreative`, `hasLockedBehaviorPack`, `hasLockedResourcePack`, `isFromLockedTemplate`, `isWorldTemplateOptionLocked`, `experiments_ever_used`, `saved_with_toggled_experiments`.

## Disclaimer

Back up your worlds before use. Works on Bedrock 1.21.130+. Not affiliated with Mojang/Microsoft.

## Credits

- Original idea: [058f9cf1](https://github.com/058f9cf1)
- Rewritten & extended by **@Heartzin** — https://t.me/Heartzin

---

Made with <3 by @Heartzin
