# Heart Unlocker — Bedrock Achievement Reactivator

**Restore achievements on Minecraft Bedrock worlds that used cheats, Creative mode or Behavior Packs — without losing your world.**

Credits: **@Heartzin** — https://t.me/Heartzin  
Based on [058f9cf1/minecraft_bedrock_reenable_achievements](https://github.com/058f9cf1/minecraft_bedrock_reenable_achievements) — rewritten with a clean interactive menu, backup and pack handling.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey) ![License](https://img.shields.io/badge/License-GPL--3.0-green)

---

## Features

- **One-click reactivation** — resets `hasBeenLoadedInCreative`, `cheatsEnabled`, `commandsEnabled`, `hasLockedBehaviorPack`, `hasLockedResourcePack`, `isFromLockedTemplate` and `GameType` to Survival
- **Smart pack handling** — detects `world_behavior_packs.json`; asks if you want to keep or remove packs (keeping packs still blocks achievements on modern Bedrock)
- **Interactive menu** — lists all local worlds (`%AppData%\Minecraft Bedrock\Users\*\games\com.mojang\minecraftWorlds`), shows `BLOCKED / OK` status and pack count; stays in menu until you type `Quit`
- **Manual / any drive** — choose `[M] Manual path` and paste a world folder, `level.dat`, `.mcworld` or `.zip` from any drive (e.g. `D:\MyWorld`, `E:\backup.mcworld`) or just drag & drop the file onto the EXE
- **Batch mode** — `0` reactivates every world at once, or pass paths as args / drag & drop `.mcworld` / `level.dat`
- **Safe** — creates `level.dat.bak` and `world_behavior_packs.json.bak` on first run; never overwrites existing backups

## Requirements

- Windows 10/11 + Minecraft for Windows (Bedrock)
- Python 3.8+ with `amulet-nbt` and `amulet-core`:
  ```powershell
  py -3 -m pip install amulet-nbt amulet-core
  ```
- Or just use the standalone `HeartUnlocker.exe` in `dist/` (no Python needed)

## Quick Start

### Option A — Python (one-liner via GitHub)

```powershell
# install directly from GitHub
py -3 -m pip install git+https://github.com/Hearttsu63/HeartzinUnlocker.git

# run
heart-unlocker
# or
py -3 -m heart_unlocker
```

### Option B — EXE (no Python needed)

1. Close Minecraft completely
2. Double-click `dist\HeartUnlocker.exe`
3. Choose world number (`0` for all) → if packs detected, choose `y` to remove them → Enter

### Option C — Termux (Android)

```bash
pkg update && pkg install python git -y
pip install amulet-nbt amulet-core
pip install git+https://github.com/Hearttsu63/HeartzinUnlocker.git
termux-setup-storage
heart-unlocker
# then choose [M] Manual path and paste:
# /storage/emulated/0/games/com.mojang/minecraftWorlds/My World
# or /storage/emulated/0/Android/data/com.mojang.minecraftpe/files/games/com.mojang/minecraftWorlds/...
```

## Secondary Commands

```powershell
# force remove packs without asking
heart-unlocker --remove-packs
# also works with old flag
heart-unlocker --limpar-packs

# single world / drag & drop (any drive, .mcworld, .zip, folder, level.dat)
heart-unlocker "D:\Games\Minecraft\MyWorld"
heart-unlocker "E:\backup.mcworld"
heart-unlocker "C:\...\minecraftWorlds\My World\level.dat"

# batch: drag multiple files onto the EXE or pass multiple paths
heart-unlocker "C:\world1" "D:\world2.mcworld"

# manual path inside menu: choose [M] and paste any path above
```

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
