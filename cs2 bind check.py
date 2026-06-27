import os
import re
import string
import threading
import queue
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG = "#111111"
ORANGE = "#ff7a00"

log_queue = queue.Queue()


# ---------------- PARSER ----------------

def parse_vcfg_keys(path):
    binds = {}

    if not os.path.exists(path):
        return binds

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    for k, v in re.findall(r'"([^"]+)"\s*"([^"]+)"', text):
        if k == "bindings":
            continue
        binds[k] = v

    return binds


def parse_sensitivity(path):
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    m = re.search(r'"sensitivity"\s*"([^"]+)"', text)
    return m.group(1) if m else None


# ---------------- APP ----------------

class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("CS2 Bind Checker")
        self.geometry("1100x700")
        self.configure(fg_color=BG)

        self.accounts = {}

        self.create_ui()
        self.after(100, self.update_log)

    def create_ui(self):

        self.tabs = ctk.CTkTabview(self, fg_color=BG)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_tab = self.tabs.add("Лог")

        self.log_box = ctk.CTkTextbox(self.log_tab, fg_color="#1a1a1a")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)

        bottom = ctk.CTkFrame(self, fg_color=BG)
        bottom.pack(fill="x", padx=10, pady=5)

        self.btn = ctk.CTkButton(
            bottom,
            text="Сканировать",
            fg_color=ORANGE,
            command=self.start_scan
        )
        self.btn.pack(side="left")

        self.status = ctk.CTkLabel(bottom, text="Готово", text_color="gray")
        self.status.pack(side="right")

    # -------- LOG --------

    def log(self, text):
        log_queue.put(text)

    def update_log(self):
        while not log_queue.empty():
            msg = log_queue.get()
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")

        self.after(100, self.update_log)

    # -------- SCAN --------

    def start_scan(self):
        self.btn.configure(state="disabled")
        threading.Thread(target=self.scan, daemon=True).start()

    def scan(self):

        steam_paths = []

        for d in string.ascii_uppercase:
            drive = d + ":\\"
            if not os.path.exists(drive):
                continue

            self.log(f"Проверяю диск {drive}")

            for base in [
                "Steam",
                "SteamLibrary",
                "Program Files\\Steam",
                "Program Files (x86)\\Steam"
            ]:
                path = os.path.join(drive, base, "userdata")

                if os.path.exists(path):
                    self.log(f"Найден Steam: {path}")
                    steam_paths.append(path)

        if not steam_paths:
            self.log("Steam не найден")
            return

        for userdata in steam_paths:
            self.scan_accounts(userdata)

        self.status.configure(text="Готово")
        self.btn.configure(state="normal")

    # -------- ACCOUNTS --------

    def scan_accounts(self, userdata):

        for acc in os.listdir(userdata):

            cfg = os.path.join(userdata, acc, "730", "local", "cfg")

            if not os.path.exists(cfg):
                continue

            self.log(f"Аккаунт найден: {acc}")

            self.create_tab(acc, cfg)

    # -------- UI TAB --------

    def create_tab(self, account, cfg):

        if account in self.accounts:
            return

        tab = self.tabs.add(account)
        self.accounts[account] = tab

        label = ctk.CTkLabel(tab, text=f"Steam: {account}")
        label.pack(pady=10)

        info = ctk.CTkLabel(tab, text="")
        info.pack()

        tree = ttk.Treeview(tab, columns=("k", "v"), show="headings")
        tree.heading("k", text="Key")
        tree.heading("v", text="Bind")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        keys = parse_vcfg_keys(os.path.join(cfg, "cs2_user_keys_0_slot0.vcfg"))
        sens = parse_sensitivity(os.path.join(cfg, "cs2_user_convars_0_slot0.vcfg"))

        info.configure(text=f"Sensitivity: {sens}")

        for k, v in sorted(keys.items()):
            tree.insert("", "end", values=(k, v))


# ---------------- RUN ----------------

if __name__ == "__main__":
    app = App()
    app.mainloop()
