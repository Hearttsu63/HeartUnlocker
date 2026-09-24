#!/usr/bin/env python3
# HEART UNLOCKER - Bedrock Achievement Reactivator
# Credits: @Heartzin | https://t.me/Heartzin
# Based on 058f9cf1/minecraft_bedrock_reenable_achievements
import pathlib, struct, sys, json, shutil, os, time, random, zipfile, tempfile
from amulet_nbt import load, TAG_Byte, TAG_Int

if sys.platform == 'win32':
    try:
        os.system('chcp 65001 >nul 2>&1')
        sys.stdout.reconfigure(encoding='utf-8')
    except: pass

WORLDS_ROOT = pathlib.Path.home() / "AppData/Roaming/Minecraft Bedrock/Users"

def get_possible_roots():
    roots=[]
    # Windows default (C:)
    roots.append(WORLDS_ROOT)
    if os.name == "nt":
        # scan all drives for alternative locations (D:, E:, etc.)
        for c in range(65, 91):
            drive = pathlib.Path(f"{chr(c)}:/")
            try:
                if not drive.exists(): continue
            except: continue
            for cand in [
                drive / "games/com.mojang/minecraftWorlds",
                drive / "Minecraft Bedrock/Users",
                drive / "Minecraft Bedrock/games/com.mojang/minecraftWorlds",
            ]:
                try:
                    if cand.exists() and cand not in roots:
                        roots.append(cand)
                except: pass
        # also check common custom location: %AppData% on other drives via USERPROFILE
        for env in ["APPDATA", "LOCALAPPDATA"]:
            p=os.environ.get(env)
            if p:
                cand=pathlib.Path(p).parent / "Minecraft Bedrock/Users"
                if cand.exists() and cand not in roots:
                    roots.append(cand)
    else:
        # Termux / Android / Linux
        for cand in [
            pathlib.Path("/storage/emulated/0/games/com.mojang/minecraftWorlds"),
            pathlib.Path("/storage/emulated/0/Android/data/com.mojang.minecraftpe/files/games/com.mojang/minecraftWorlds"),
            pathlib.Path.home() / "storage/shared/games/com.mojang/minecraftWorlds",
            pathlib.Path("/data/data/com.mojang.minecraftpe/files/games/com.mojang/minecraftWorlds"),
            pathlib.Path.home() / "games/com.mojang/minecraftWorlds",
        ]:
            try:
                if cand.exists() and cand not in roots:
                    roots.append(cand)
            except: pass
    return roots

FLAGS_BYTE = [
    "cheatsEnabled",
    "commandsEnabled",
    "hasBeenLoadedInCreative",
    "hasLockedBehaviorPack",
    "hasLockedResourcePack",
    "isFromLockedTemplate",
    "isWorldTemplateOptionLocked",
]

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    DIM = '\033[2m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    BG_GREEN = '\033[42m'
    BG_BLACK = '\033[40m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def loading_animation(msg, duration=0.6):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    end = time.time() + duration
    i=0
    while time.time() < end:
        print(f"\r{Colors.GREEN}{frames[i%len(frames)]}{Colors.RESET} {msg}", end="")
        time.sleep(0.08); i+=1
    print(f"\r{Colors.GREEN}[✓]{Colors.RESET} {msg} {Colors.GREEN}DONE{Colors.RESET}  ")

def cyber_divider():
    print(f"{Colors.GREEN}{'═'*62}{Colors.RESET}")

def cyber_box(text, color=Colors.GREEN):
    print(f"{color}╔{'═'*(len(text)+4)}╗{Colors.RESET}")
    print(f"{color}║  {Colors.BOLD}{text}{Colors.RESET}{color}  ║{Colors.RESET}")
    print(f"{color}╚{'═'*(len(text)+4)}╝{Colors.RESET}")

def print_banner():
    art = r"""
 █ █ █▀▀ █▀█ █▀█ ▀█▀      █ █ █▀▄█ █   █▀█ █▀▀ █ █ █▀▀ █▀█
 █▀▓ ▓▀  █▀▓ ▓▀▄  ▓░      █ ▓ █  ▓ ▓░  █ ▓ ▓░  ▓▀▄ ▓▀  ▓▀▄
 ▀ ▀ ▀▀▀ ▀ ▀ ▀ ▀  ▀       ▀▀▀ ▀  ▀ ▀▀▀ ▀▀▀ ▀▀▀ ▀ ▀ ▀▀▀ ▀ ▀
"""
    banner = f"{Colors.GREEN}{Colors.BOLD}{art}{Colors.RESET}{Colors.DIM}              [  BEDROCK ACHIEVEMENT REACTIVATOR  ]{Colors.RESET}\n{Colors.DIM}              Credits: @Heartzin  |  t.me/Heartzin{Colors.RESET}\n"
    print(banner)

def patch_level_dat(level_path: pathlib.Path, remove_packs=False):
    data = level_path.read_bytes()
    if len(data) < 8:
        print(f"{Colors.RED}  [ERROR] level.dat too small: {level_path}{Colors.RESET}")
        return False
    ver, length = struct.unpack("<ii", data[:8])
    nbt_bytes = data[8:8+length]
    extra = data[8+length:]
    tag = load(nbt_bytes, little_endian=True, compressed=False)
    root = tag.tag
    changed=[]
    if "GameType" in root and int(root["GameType"]) != 0:
        root["GameType"] = TAG_Int(0)
        changed.append("GameType->Survival")
    for k in FLAGS_BYTE:
        if k in root and int(root[k]) != 0:
            root[k] = TAG_Byte(0)
            changed.append(f"{k}->0")
    if "experiments" in root:
        ex=root["experiments"]
        for ek in ["experiments_ever_used","saved_with_toggled_experiments"]:
            if ek in ex and int(ex[ek])!=0:
                ex[ek]=TAG_Byte(0)
                changed.append(f"experiments.{ek}->0")
    if not changed and not remove_packs:
        print(f"{Colors.GREEN}  [OK] already clean{Colors.RESET}")
        return True
    bak=level_path.with_name("level.dat.bak")
    if not bak.exists():
        shutil.copy2(level_path,bak)
        print(f"{Colors.DIM}  backup: {bak.name}{Colors.RESET}")
    new_nbt=tag.save_to(little_endian=True, compressed=False)
    out=struct.pack("<ii",ver,len(new_nbt))+new_nbt+extra
    level_path.write_bytes(out)
    if changed:
        print(f"{Colors.GREEN}  [OK] flags: {', '.join(changed)}{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}  [OK] flags already ok{Colors.RESET}")
    if remove_packs:
        wbp=level_path.parent/"world_behavior_packs.json"
        if wbp.exists():
            try: arr=json.loads(wbp.read_text(encoding="utf-8").strip() or "[]")
            except: arr=[]
            if arr:
                bak2=wbp.with_name("world_behavior_packs.json.bak")
                if not bak2.exists(): shutil.copy2(wbp,bak2)
                wbp.write_text("[]",encoding="utf-8")
                print(f"{Colors.YELLOW}  * world_behavior_packs.json cleared ({len(arr)} pack(s) removed){Colors.RESET}")
            else:
                print(f"{Colors.DIM}  world_behavior_packs.json already empty{Colors.RESET}")
        old=level_path.parent/"level.dat_old"
        if old.exists():
            try: old.unlink()
            except: pass
    return True

def listar_mundos():
    mundos=[]
    seen=set()
    for root in get_possible_roots():
        try:
            if not root.exists(): continue
        except: continue
        # direct minecraftWorlds folder (Termux / any drive)
        if root.name == "minecraftWorlds":
            try:
                for w in root.iterdir():
                    if w.is_dir() and (w/"level.dat").exists():
                        rp=str(w.resolve())
                        if rp not in seen:
                            seen.add(rp); mundos.append(w)
            except: pass
            continue
        # Users folder (Windows)
        if root.name == "Users":
            try:
                for user in root.iterdir():
                    if not user.is_dir(): continue
                    mp=user/"games/com.mojang/minecraftWorlds"
                    if not mp.is_dir(): continue
                    for w in mp.iterdir():
                        if w.is_dir() and (w/"level.dat").exists():
                            rp=str(w.resolve())
                            if rp not in seen:
                                seen.add(rp); mundos.append(w)
            except: pass
            continue
        # fallback: search for minecraftWorlds under this root
        try:
            for mp in root.rglob("minecraftWorlds"):
                if not mp.is_dir(): continue
                for w in mp.iterdir():
                    if w.is_dir() and (w/"level.dat").exists():
                        rp=str(w.resolve())
                        if rp not in seen:
                            seen.add(rp); mundos.append(w)
        except: pass
    mundos.sort(key=lambda p: str(p).lower())
    return mundos

def mundo_info(w: pathlib.Path):
    ln=(w/"levelname.txt").read_text(encoding="utf-8").strip() if (w/"levelname.txt").exists() else w.name
    try:
        data=(w/"level.dat").read_bytes()
        ver,length=struct.unpack("<ii",data[:8])
        tag=load(data[8:8+length], little_endian=True, compressed=False)
        root=tag.tag
        hb=int(root.get("hasBeenLoadedInCreative",0))
        ce=int(root.get("cheatsEnabled",0))
        cmd=int(root.get("commandsEnabled",0))
        blocked=(hb==1 or ce==1 or cmd==1)
    except: blocked=None
    try:
        j=json.loads((w/"world_behavior_packs.json").read_text(encoding="utf-8"))
        packs=len(j) if isinstance(j,list) else 0
    except: packs=0
    return ln,blocked,packs

def handle_zip_file(zip_path: pathlib.Path, remove_packs=False):
    if not zipfile.is_zipfile(zip_path):
        print(f"{Colors.RED}  Not a valid zip/mcworld: {zip_path}{Colors.RESET}")
        return False
    tmpdir = pathlib.Path(tempfile.gettempdir()) / "heartzin_unlock"
    if tmpdir.exists(): shutil.rmtree(tmpdir)
    tmpdir.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(tmpdir)
        # find level.dat inside tmpdir
        level_dat = None
        for p in tmpdir.rglob("level.dat"):
            level_dat = p
            break
        if not level_dat or not level_dat.exists():
            print(f"{Colors.RED}  No level.dat found in archive{Colors.RESET}")
            return False
        world_dir = level_dat.parent
        print(f"{Colors.GREEN}  -> Patching {world_dir.name} inside archive{Colors.RESET}")
        patch_level_dat(level_dat, remove_packs=remove_packs)
        # also handle world_behavior_packs.json if remove_packs
        if remove_packs:
            wbp = world_dir / "world_behavior_packs.json"
            if wbp.exists():
                try:
                    arr=json.loads(wbp.read_text(encoding="utf-8").strip() or "[]")
                except: arr=[]
                if arr:
                    wbp.write_text("[]", encoding="utf-8")
        # recompress
        # mcworld is just zip with .mcworld extension
        # create new zip in temp then move
        tmp_zip = zip_path.with_suffix(".tmp")
        with zipfile.ZipFile(tmp_zip, 'w', zipfile.ZIP_DEFLATED) as z:
            for f in tmpdir.rglob("*"):
                if f.is_file():
                    z.write(f, f.relative_to(tmpdir))
        shutil.move(str(tmp_zip), str(zip_path))
        print(f"{Colors.GREEN}  [OK] Archive updated: {zip_path}{Colors.RESET}")
        return True
    finally:
        if tmpdir.exists(): shutil.rmtree(tmpdir)

def main():
    # CLI batch mode: if args given, do single run and exit (drag & drop support - any drive, .mcworld, .zip, folder, level.dat)
    force_remove="--remove-packs" in sys.argv or "--limpar-packs" in sys.argv or "--limpar" in sys.argv
    args=[a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        has_work=False
        for a in args:
            p=pathlib.Path(a.strip().strip('"').strip("'"))
            if p.is_file() and p.suffix.lower() in (".mcworld",".zip") and zipfile.is_zipfile(p):
                handle_zip_file(p, remove_packs=force_remove)
                has_work=True
            elif p.is_file() and p.name=="level.dat":
                patch_level_dat(p, remove_packs=force_remove)
                has_work=True
            elif p.is_dir() and (p/"level.dat").exists():
                patch_level_dat(p/"level.dat", remove_packs=force_remove)
                has_work=True
            elif p.is_file() and p.name=="level.dat":
                patch_level_dat(p, remove_packs=force_remove)
                has_work=True
            else:
                # try as world dir passed as level.dat parent
                pp=pathlib.Path(a)
                if pp.is_dir() and (pp/"level.dat").exists():
                    patch_level_dat(pp/"level.dat", remove_packs=force_remove)
                    has_work=True
                else:
                    print(f"{Colors.RED}Ignored: {a}{Colors.RESET}")
        if not has_work:
            print(f"{Colors.RED}Nothing to do.{Colors.RESET}"); sys.exit(1)
        print(f"\n{Colors.GREEN}Done!{Colors.RESET}")
        return

    # Interactive cyberpunk menu loop
    while True:
        clear_screen()
        print_banner()
        cyber_divider()
        mundos=listar_mundos()
        if not mundos:
            print(f"{Colors.RED}  No worlds found. Create a world first.{Colors.RESET}")
            input("  Press Enter to exit..."); return

        print(f"{Colors.BOLD}  YOUR WORLDS:{Colors.RESET}\n")
        print(f"{Colors.DIM}  {'#':<3} {'Name':<28} {'Status':<12} {'Packs'}{Colors.RESET}")
        print(f"{Colors.GREEN}  {'-'*56}{Colors.RESET}")
        for i,w in enumerate(mundos,1):
            ln,blocked,packs=mundo_info(w)
            if blocked: status=f"{Colors.RED}* BLOCKED{Colors.RESET}"
            elif blocked==False: status=f"{Colors.GREEN}* OK{Colors.RESET}"
            else: status=f"{Colors.DIM}* ?{Colors.RESET}"
            packs_s=f"{Colors.YELLOW}{packs} pack(s){Colors.RESET}" if packs else f"{Colors.DIM}-{Colors.RESET}"
            # strip ANSI for length calc, but print with colors
            print(f"  {Colors.GREEN}{str(i).rjust(2)}{Colors.RESET}  {ln[:28].ljust(28)} {status}  {packs_s}")

        print(f"\n{Colors.DIM}  [0] ALL  |  [M] Manual path (any drive / .mcworld / .zip)  |  [Q] Quit{Colors.RESET}")
        cyber_divider()
        sel=input(f"{Colors.BOLD}{Colors.GREEN}  Choose > {Colors.RESET}").strip().lower()
        if sel in ("q","quit","exit"):
            print(f"{Colors.GREEN}\n  Bye! Made with <3 by @Heartzin{Colors.RESET}")
            break
        # Manual path - send world file from any drive
        if sel in ("m","manual"):
            manual=input(f"{Colors.BOLD}  Paste world path (folder, level.dat, .mcworld, .zip) > {Colors.RESET}").strip().strip('"').strip("'")
            if not manual or manual.lower() in ("q","quit","exit"):
                continue
            p=pathlib.Path(manual)
            # zip / mcworld
            if p.is_file() and p.suffix.lower() in (".mcworld",".zip") and zipfile.is_zipfile(p):
                # ask about packs for zip
                remove = force_remove
                if not remove:
                    r=input(f"{Colors.BOLD}  Remove packs from archive? [y/N] > {Colors.RESET}").strip().lower()
                    remove=r in ("y","yes")
                cyber_box("REACTIVATING ARCHIVE", Colors.GREEN)
                loading_animation("Patching archive", 0.7)
                handle_zip_file(p, remove_packs=remove)
                print(f"\n{Colors.GREEN}{'═'*62}{Colors.RESET}")
                print(f"{Colors.BOLD}{Colors.GREEN}  [OK] Archive done!{Colors.RESET}")
                print(f"{Colors.GREEN}{'═'*62}{Colors.RESET}")
                nxt=input(f"\n{Colors.BOLD}  Press Enter to return to menu (or type quit) > {Colors.RESET}").strip().lower()
                if nxt in ("q","quit","exit"):
                    print(f"{Colors.GREEN}  Bye!{Colors.RESET}"); break
                continue
            elif p.is_file() and p.name=="level.dat":
                targets=[p.parent]
            elif p.is_dir() and (p/"level.dat").exists():
                targets=[p]
            else:
                print(f"{Colors.RED}  Invalid path. Use a world folder, level.dat or .mcworld/.zip{Colors.RESET}"); time.sleep(1.5); continue
        else:
            try:
                sel_int=int(sel)
            except:
                print(f"{Colors.RED}  Invalid input{Colors.RESET}"); time.sleep(1); continue
            if sel_int==0:
                targets=mundos
            elif 1 <= sel_int <= len(mundos):
                targets=[mundos[sel_int-1]]
            else:
                print(f"{Colors.RED}  Invalid selection{Colors.RESET}"); time.sleep(1); continue

        # detect packs
        if force_remove:
            remove=True
        else:
            has_packs=any(mundo_info(w)[2]>0 for w in targets)
            if has_packs:
                print(f"\n{Colors.YELLOW}  [!] Some worlds have Behavior Pack installed.{Colors.RESET}")
                print(f"{Colors.DIM}     Keeping packs still blocks achievements.{Colors.RESET}")
                r=input(f"{Colors.BOLD}  Remove packs? [y/N] > {Colors.RESET}").strip().lower()
                if r in ("q","quit","exit"):
                    continue
                remove=r in ("y","yes")
                if remove:
                    print(f"{Colors.YELLOW}  -> packs will be removed{Colors.RESET}")
                else:
                    print(f"{Colors.DIM}  -> packs kept (only flags){Colors.RESET}")
            else:
                remove=False

        print(f"\n{Colors.RED}  [!] Close Minecraft before continuing!{Colors.RESET}")
        cont=input(f"{Colors.DIM}  Press Enter to reactivate (or type quit to cancel) > {Colors.RESET}").strip().lower()
        if cont in ("q","quit","exit"):
            continue

        print()
        cyber_box("REACTIVATING", Colors.GREEN)
        loading_animation("Patching level.dat", 0.7)
        for w in targets:
            ln,_,_=mundo_info(w)
            print(f"{Colors.GREEN}  -> {w.name}{Colors.RESET}  \"{ln}\"")
            patch_level_dat(w/"level.dat", remove_packs=remove)

        print(f"\n{Colors.GREEN}{'═'*62}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}  [OK] Done! Open the world and achievements will count again.{Colors.RESET}")
        if remove:
            print(f"{Colors.DIM}     Packs removed. Reinstall Bar addon when you need Creative again.{Colors.RESET}")
        else:
            if any(mundo_info(w)[2]>0 for w in targets):
                print(f"{Colors.YELLOW}     Tip: if still blocked, run again and choose to remove packs.{Colors.RESET}")
        print(f"{Colors.GREEN}{'═'*62}{Colors.RESET}")
        print(f"{Colors.DIM}  Made with <3 by @Heartzin -- t.me/Heartzin{Colors.RESET}")
        nxt=input(f"\n{Colors.BOLD}  Press Enter to return to menu (or type quit) > {Colors.RESET}").strip().lower()
        if nxt in ("q","quit","exit"):
            print(f"{Colors.GREEN}  Bye!{Colors.RESET}"); break

if __name__=="__main__":
    main()
