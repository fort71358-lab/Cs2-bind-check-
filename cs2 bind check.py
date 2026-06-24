import os
import string
import re

# ---------- Поиск Steam ----------

steam_folders = []

for drive in string.ascii_uppercase:
    drive = drive + ":\\"

    if not os.path.exists(drive):
        continue

    print(f"Проверяю {drive}")

    try:
        for root, dirs, files in os.walk(drive):

            if "userdata" in dirs:
                userdata = os.path.join(root, "userdata")

                if os.path.exists(userdata):
                    steam_folders.append(userdata)

    except:
        pass

if not steam_folders:
    print("Steam не найден!")
    exit()

print("\nНайден Steam:\n")

for folder in steam_folders:
    print(folder)

print()

# ---------- Стандартные бинды ----------

default_binds = {
    "W":"+forward",
    "A":"+left",
    "S":"+back",
    "D":"+right",
    "SPACE":"+jump",
    "CTRL":"+duck",
    "SHIFT":"+sprint",
    "E":"+use",
    "R":"+reload",
    "MOUSE1":"+attack",
    "MOUSE2":"+attack2"
}

# ---------- Поиск аккаунтов ----------

for userdata in steam_folders:

    for account in os.listdir(userdata):

        cfg = os.path.join(
            userdata,
            account,
            "730",
            "local",
            "cfg"
        )

        if not os.path.exists(cfg):
            continue

        print("="*60)
        print("SteamID:", account)
        print(cfg)
        print("="*60)

        binds = default_binds.copy()

        keys = os.path.join(cfg,"cs2_user_keys_0_slot0.vcfg")
        convars = os.path.join(cfg,"cs2_user_convars_0_slot0.vcfg")

        # ---------- БИНДЫ ----------

        if os.path.exists(keys):

            with open(keys,"r",encoding="utf-8") as f:
                txt = f.read()

            for key,val in re.findall(r'"([^"]+)"\s*"([^"]+)"',txt):

                if key=="bindings":
                    continue

                binds[key]=val

        # ---------- SENSITIVITY ----------

        sensitivity="По умолчанию"

        if os.path.exists(convars):

            with open(convars,"r",encoding="utf-8") as f:
                txt=f.read()

            m=re.search(r'"sensitivity"\s*"([^"]+)"',txt)

            if m:
                sensitivity=m.group(1)

        print("\nSensitivity:",sensitivity)
        print()

        for k in sorted(binds):
            print(f"{k:12} -> {binds[k]}")

        print()
print("\nГотово!")

input("\nНажмите Enter, чтобы закрыть программу...")
