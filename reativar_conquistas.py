#!/usr/bin/env python3
# HEARTZIN UNLOCKER - Bedrock Achievement Reactivator
# Credits: @Heartzin | https://t.me/Heartzin
# Based on 058f9cf1/minecraft_bedrock_reenable_achievements
import pathlib, struct, sys, json, shutil, os
from amulet_nbt import load, TAG_Byte, TAG_Int

WORLDS_ROOT = pathlib.Path.home() / "AppData/Roaming/Minecraft Bedrock/Users"

FLAGS_BYTE = [
    "cheatsEnabled",
    "commandsEnabled",
    "hasBeenLoadedInCreative",
    "hasLockedBehaviorPack",
    "hasLockedResourcePack",
    "isFromLockedTemplate",
    "isWorldTemplateOptionLocked",
]

# clean visual (no ANSI to avoid console bugs)
def c(k, t): return t

def header():
    print(r"  _   _ _____   _    ____ _____")
    print(r" | | | | ____| / \  |  _ \_   _|")
    print(r" | |_| |  _|  / _ \ | |_) || |")
    print(r" |  _  | |___ / ___ \|  _ < | |")
    print(r" |_| |_|_____/_/   \_\_| \_\|_|")
    print()
    print("  -- BEDROCK ACHIEVEMENT REACTIVATOR --")
    print("  Credits: @Heartzin  |  t.me/Heartzin  |  base: github.com/058f9cf1")
    print("  " + "-"*58)
    print()

def patch_level_dat(level_path: pathlib.Path, remove_packs=False):
    data = level_path.read_bytes()
    if len(data) < 8:
        print(f"  [ERROR] level.dat too small: {level_path}")
        return False
    ver, length = struct.unpack("<ii", data[:8])
    nbt_bytes = data[8:8+length]
    extra = data[8+length:]

    tag = load(nbt_bytes, little_endian=True, compressed=False)
    root = tag.tag
    changed = []

    if "GameType" in root and int(root["GameType"]) != 0:
        root["GameType"] = TAG_Int(0)
        changed.append("GameType->Survival")
    for k in FLAGS_BYTE:
        if k in root and int(root[k]) != 0:
            root[k] = TAG_Byte(0)
            changed.append(f"{k}->0")
    if "experiments" in root:
        ex = root["experiments"]
        for ek in ["experiments_ever_used", "saved_with_toggled_experiments"]:
            if ek in ex and int(ex[ek]) != 0:
                ex[ek] = TAG_Byte(0)
                changed.append(f"experiments.{ek}->0")

    if not changed and not remove_packs:
        print("  [OK] already clean (nothing to change)")
        return True

    bak = level_path.with_name("level.dat.bak")
    if not bak.exists():
        shutil.copy2(level_path, bak)
        print(f"  backup: {bak.name}")

    new_nbt = tag.save_to(little_endian=True, compressed=False)
    out = struct.pack("<ii", ver, len(new_nbt)) + new_nbt + extra
    level_path.write_bytes(out)
    if changed:
        print(f"  [OK] flags: {', '.join(changed)}")
    else:
        print("  [OK] flags already ok")

    if remove_packs:
        wbp = level_path.parent / "world_behavior_packs.json"
        if wbp.exists():
            try:
                arr = json.loads(wbp.read_text(encoding="utf-8").strip() or "[]")
            except: arr = []
            if arr:
                bak2 = wbp.with_name("world_behavior_packs.json.bak")
                if not bak2.exists(): shutil.copy2(wbp, bak2)
                wbp.write_text("[]", encoding="utf-8")
                print(f"  * world_behavior_packs.json cleared ({len(arr)} pack(s) removed)")
            else:
                print("  world_behavior_packs.json already empty")
        old = level_path.parent / "level.dat_old"
        if old.exists():
            try: old.unlink()
            except: pass
    return True

def listar_mundos():
    mundos=[]
    if not WORLDS_ROOT.exists(): return []
    for user in WORLDS_ROOT.iterdir():
        if not user.is_dir(): continue
        mp = user / "games/com.mojang/minecraftWorlds"
        if not mp.is_dir(): continue
        for w in mp.iterdir():
            if w.is_dir() and (w/"level.dat").exists():
                mundos.append(w)
    mundos.sort()
    return mundos

def mundo_info(w: pathlib.Path):
    ln = (w/"levelname.txt").read_text(encoding="utf-8").strip() if (w/"levelname.txt").exists() else w.name
    try:
        data=(w/"level.dat").read_bytes()
        ver,length=struct.unpack("<ii",data[:8])
        tag=load(data[8:8+length], little_endian=True, compressed=False)
        root=tag.tag
        hb=int(root.get("hasBeenLoadedInCreative",0))
        ce=int(root.get("cheatsEnabled",0))
        cmd=int(root.get("commandsEnabled",0))
        blocked = (hb==1 or ce==1 or cmd==1)
    except: blocked=None
    try:
        j=json.loads((w/"world_behavior_packs.json").read_text(encoding="utf-8"))
        packs=len(j) if isinstance(j,list) else 0
    except: packs=0
    return ln, blocked, packs

def main():
    header()
    force_remove = "--remove-packs" in sys.argv or "--limpar-packs" in sys.argv or "--limpar" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    targets=[]
    if args:
        for a in args:
            p=pathlib.Path(a)
            if p.is_file() and p.name=="level.dat": targets.append(p.parent)
            elif p.is_dir() and (p/"level.dat").exists(): targets.append(p)
            else: print(f"Ignored: {a}")
        remove = force_remove
    else:
        mundos=listar_mundos()
        if not mundos:
            print("  No worlds found. Create a world first.")
            input("  Press Enter to exit..."); sys.exit(1)

        print("  YOUR WORLDS:\n")
        print(f"  {'#':<3} {'Name':<28} {'Status':<12} {'Packs'}")
        print("  " + "-"*56)
        for i,w in enumerate(mundos,1):
            ln, blocked, packs = mundo_info(w)
            status = "* BLOCKED" if blocked else "* OK" if blocked==False else "* ?"
            packs_s = f"{packs} pack(s)" if packs else "-"
            print(f"  {str(i).rjust(2)}  {ln[:28].ljust(28)} {status.ljust(12)} {packs_s}")
        print()
        try:
            sel=int(input(f"  Choose world (1-{len(mundos)}) or 0 for ALL > ").strip() or "0")
        except: sel=0
        if sel==0: targets=mundos
        elif 1 <= sel <= len(mundos): targets=[mundos[sel-1]]
        else: print("  Invalid selection"); sys.exit(1)

        if force_remove:
            remove=True
        else:
            has_packs = any(mundo_info(w)[2]>0 for w in targets)
            if has_packs:
                print()
                print("  [!] Some worlds have Behavior Pack installed.")
                print("     Even after reactivation, keeping packs still blocks achievements.")
                print("     Remove packs from world? (Bar addon will be removed, but achievements return)")
                r=input("  Remove packs? [y/N] > ").strip().lower()
                remove = r in ("y","yes")
                if remove:
                    print("  -> packs will be removed together with reactivation")
                else:
                    print("  -> packs kept (only flags will be reset)")
            else:
                remove=False

        print()
        print("  [!] Close Minecraft before continuing!")
        input("  Press Enter to reactivate...")

    if not targets:
        print("  Nothing selected."); sys.exit(1)

    print()
    for w in targets:
        ln,_,_=mundo_info(w)
        print(f"  -> {w.name}  \"{ln}\"")
        patch_level_dat(w/"level.dat", remove_packs=remove)

    print()
    print("  == [OK] Done! Open the world and achievements will count again. ==")
    if remove:
        print("     Packs removed. Reinstall Bar addon when you need Creative again.")
    else:
        if any(mundo_info(w)[2]>0 for w in targets):
            print("     Tip: if still blocked, run again and choose to remove packs.")
    print("  --  Made with <3 by @Heartzin --  t.me/Heartzin  --")
    input("  Press Enter to exit...")

if __name__=="__main__":
    main()
