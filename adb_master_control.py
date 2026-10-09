#!/usr/bin/env python3
# =============================================================================
#
#   ░█████╗░██████╗░██████╗░  ███╗░░░███╗░█████╗░░██████╗████████╗███████╗██████╗░
#   ██╔══██╗██╔══██╗██╔══██╗  ████╗░████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗
#   ███████║██║░░██║██████╦╝  ██╔████╔██║███████║╚█████╗░░░░██║░░░█████╗░░██████╔╝
#   ██╔══██║██║░░██║██╔══██╗  ██║╚██╔╝██║██╔══██║░╚═══██╗░░░██║░░░██╔══╝░░██╔══██╗
#   ██║░░██║██████╔╝██████╦╝  ██║░╚═╝░██║██║░░██║██████╔╝░░░██║░░░███████╗██║░░██║
#   ╚═╝░░╚═╝╚═════╝░╚═════╝░  ╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░╚══════╝╚═╝░░╚═╝
#
#   ░█████╗░░█████╗░███╗░░██╗████████╗██████╗░░█████╗░██╗░░░░░
#   ██╔══██╗██╔══██╗████╗░██║╚══██╔══╝██╔══██╗██╔══██╗██║░░░░░
#   ██║░░╚═╝██║░░██║██╔██╗██║░░░██║░░░██████╔╝██║░░██║██║░░░░░
#   ██║░░██╗██║░░██║██║╚████║░░░██║░░░██╔══██╗██║░░██║██║░░░░░
#   ╚█████╔╝╚█████╔╝██║░╚███║░░░██║░░░██║░░██║╚█████╔╝███████╗
#   ░╚════╝░░╚════╝░╚═╝░░╚══╝░░░╚═╝░░░╚═╝░░╚═╝░╚════╝░╚══════╝
#
#   Version  : 2.0 ELITE
#   Auteur   : SPECTRA  |  github.com/exploit4040
#   
#   
#   
#
#   Installation :
#       pip install customtkinter matplotlib
#
#   Lancement :
#       python adb_master_control.py
# =============================================================================

import subprocess
import sys
import os
import threading
import time
import re
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime


def _ensure(pkg):
    try:
        __import__(pkg)
    except ImportError:
        print(f"[*] Installation de {pkg}...")
        subprocess.run([sys.executable, "-m", "pip", "install", pkg],
                       check=True, capture_output=True)

_ensure("customtkinter")
_ensure("matplotlib")

import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ── Thème global ─────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

C = {
    "bg":       "#080c10",
    "panel":    "#0d1117",
    "card":     "#161b22",
    "card2":    "#1c2330",
    "border":   "#30363d",
    "green":    "#00d084",
    "blue":     "#388bfd",
    "red":      "#f85149",
    "yellow":   "#e3b341",
    "purple":   "#bc8cff",
    "orange":   "#f0883e",
    "cyan":     "#39d0d8",
    "text":     "#e6edf3",
    "dim":      "#7d8590",
    "terminal": "#00ff41",
}

GPS_PKG = "com.google.android.gms"


# =============================================================================
#  COUCHE ADB
# =============================================================================
class ADBCore:
    """Gère toutes les interactions avec ADB."""

    def __init__(self):
        self.connected   = False
        self.device_info = {}
        self.log_file    = f"adb_master_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # ── Exécution ─────────────────────────────────────────────────────────
    def run(self, command: str, timeout: int = 15):
        """Exécute une commande ADB brute (ex: 'devices', 'pull /sdcard/f ./f')."""
        try:
            result = subprocess.run(
                ["adb"] + command.split(),
                capture_output=True, text=True, timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return None

    def shell(self, command: str, timeout: int = 15):
        """Exécute 'adb shell <command>'."""
        try:
            result = subprocess.run(
                ["adb", "shell"] + command.split(),
                capture_output=True, text=True, timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return None

    def shell_raw(self, command: str, timeout: int = 15):
        """Exécute 'adb shell' avec commande non-splitée (préserve les espaces/guillemets)."""
        try:
            result = subprocess.run(
                f"adb shell {command}",
                capture_output=True, text=True, timeout=timeout, shell=True
            )
            return result
        except Exception:
            return None

    # ── Log fichier ────────────────────────────────────────────────────────
    def log(self, msg: str):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"[{ts}] {msg}\n")
        except Exception:
            pass

    # ── Connexion ─────────────────────────────────────────────────────────
    def check_adb_installed(self) -> bool:
        try:
            subprocess.run(["adb", "--version"],
                           capture_output=True, check=True, timeout=5)
            return True
        except Exception:
            return False

    def connect(self) -> bool:
        r = self.run("devices", timeout=8)
        if not r:
            self.connected = False
            return False
        for line in r.stdout.strip().split("\n"):
            if "device" in line and not line.startswith("List"):
                self.connected = True
                self._fetch_device_info()
                self.log(f"Connecté: {self.device_info.get('model','?')}")
                return True
        self.connected = False
        return False

    def _fetch_device_info(self):
        props = {
            "model":    "getprop ro.product.model",
            "brand":    "getprop ro.product.brand",
            "android":  "getprop ro.build.version.release",
            "sdk":      "getprop ro.build.version.sdk",
            "cpu":      "getprop ro.product.cpu.abi",
            "serial":   "getprop ro.serialno",
            "rom":      "getprop ro.build.display.id",
            "board":    "getprop ro.product.board",
        }
        for k, cmd in props.items():
            r = self.shell(cmd, timeout=5)
            self.device_info[k] = r.stdout.strip() if r and r.stdout.strip() else "?"

    # ── Helpers données ────────────────────────────────────────────────────
    def battery_level(self):
        r = self.shell("dumpsys battery")
        if r and r.stdout:
            m = re.search(r"level:\s*(\d+)", r.stdout)
            if m:
                return int(m.group(1))
        return None

    def battery_temp(self):
        r = self.shell("dumpsys battery")
        if r and r.stdout:
            m = re.search(r"temperature:\s*(\d+)", r.stdout)
            if m:
                return round(int(m.group(1)) / 10, 1)
        return None

    def battery_status(self) -> str:
        r = self.shell("dumpsys battery")
        if r and r.stdout:
            m = re.search(r"status:\s*(\d+)", r.stdout)
            if m:
                return {"1": "INCONNU", "2": "⚡ EN CHARGE",
                        "3": "🔋 DÉCHARGE", "4": "NON CHARGE",
                        "5": "✅ PLEIN"}.get(m.group(1), "?")
        return "?"

    def list_packages(self, flag: str = "") -> list:
        r = self.shell(f"pm list packages {flag}".strip())
        if r and r.stdout:
            return [l.replace("package:", "").strip()
                    for l in r.stdout.strip().split("\n") if l.strip()]
        return []

    def gps_status(self) -> str:
        """Retourne 'ENABLED', 'DISABLED', 'NOT_FOUND'."""
        r_d = self.shell(f"pm list packages -d {GPS_PKG}")
        r_e = self.shell(f"pm list packages -e {GPS_PKG}")
        if r_d and GPS_PKG in r_d.stdout:
            return "DISABLED"
        if r_e and GPS_PKG in r_e.stdout:
            return "ENABLED"
        return "NOT_FOUND"


# =============================================================================
#  APPLICATION PRINCIPALE
# =============================================================================
class ADBMasterApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.adb             = ADBCore()
        self.monitor_running = False
        self.logcat_running  = False
        self._time_pts: list = []
        self._batt_pts: list = []
        self._monitor_t0     = 0.0
        self._fill           = None
        self.term_history    : list = []
        self.term_hist_idx   : int  = 0
        self.pages           : dict = {}
        self.nav_btns        : dict = {}
        self.current_page    : str  = ""

        self.title("⚡  ADB MASTER CONTROL  v2.0 ELITE  —  ML | exploit4040")
        self.geometry("1360x820")
        self.minsize(1100, 720)
        self.configure(fg_color=C["bg"])

        self._build_ui()
        self._auto_connect()

    # =========================================================================
    #  HELPERS UI
    # =========================================================================
    def _thread(self, fn, *args):
        threading.Thread(target=fn, args=args, daemon=True).start()

    def _darken(self, hex_c: str) -> str:
        h = hex_c.lstrip("#")
        rgb = tuple(max(0, int(h[i:i+2], 16) - 40) for i in (0, 2, 4))
        return "#{:02x}{:02x}{:02x}".format(*rgb)

    def _log(self, textbox: ctk.CTkTextbox, msg: str):
        """Insère une ligne horodatée dans un CTkTextbox (thread-safe)."""
        ts = datetime.now().strftime("%H:%M:%S")
        def _do():
            textbox.configure(state="normal")
            textbox.insert("end", f"[{ts}] {msg}\n")
            textbox.see("end")
            textbox.configure(state="disabled")
        self.after(0, _do)

    def _shell_log(self, cmd: str, textbox: ctk.CTkTextbox):
        """Lance 'adb shell <cmd>' et logue le résultat."""
        def _run():
            r = self.adb.shell(cmd)
            out = r.stdout.strip()[:400] if r and r.stdout else "(pas de sortie)"
            self._log(textbox, f"$ {cmd}\n  → {out}")
            self.adb.log(f"shell: {cmd}")
        self._thread(_run)

    def _btn(self, parent, text: str, cmd, row: int, col: int,
             color=None, cspan: int = 1, height: int = 36) -> ctk.CTkButton:
        color = color or C["blue"]
        b = ctk.CTkButton(
            parent, text=text, command=cmd,
            fg_color=color, hover_color=self._darken(color),
            font=ctk.CTkFont(size=11), height=height, corner_radius=8
        )
        b.grid(row=row, column=col, columnspan=cspan,
               padx=6, pady=4, sticky="ew")
        return b

    def _textbox(self, parent, height: int = 140) -> ctk.CTkTextbox:
        tb = ctk.CTkTextbox(
            parent, fg_color=C["bg"], text_color=C["green"],
            font=ctk.CTkFont(family="Courier New", size=10),
            height=height, state="disabled"
        )
        return tb

    def _card(self, parent, row: int, col: int,
              title: str = "", cspan: int = 1) -> ctk.CTkFrame:
        c = ctk.CTkFrame(parent, fg_color=C["card"], corner_radius=10)
        c.grid(row=row, column=col, columnspan=cspan,
               padx=8, pady=6, sticky="nsew")
        if title:
            ctk.CTkLabel(c, text=title,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=C["dim"]
            ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")
        return c

    def _make_page(self, key: str, title: str, icon: str = "") -> ctk.CTkScrollableFrame:
        frame = ctk.CTkScrollableFrame(self._main, fg_color=C["bg"])
        frame.grid_columnconfigure(0, weight=1)
        self.pages[key] = frame

        hdr = ctk.CTkFrame(frame, fg_color=C["panel"], corner_radius=10)
        hdr.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 6))
        hdr.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(hdr,
            text=f"{icon}  {title}",
            font=ctk.CTkFont(family="Courier New", size=17, weight="bold"),
            text_color=C["green"]
        ).grid(row=0, column=0, padx=18, pady=12, sticky="w")

        badge = ctk.CTkLabel(hdr,
            text="ML | exploit4040",
            font=ctk.CTkFont(size=9), text_color=C["dim"])
        badge.grid(row=0, column=1, padx=4, pady=12, sticky="e")

        ts_lbl = ctk.CTkLabel(hdr, text="",
            font=ctk.CTkFont(family="Courier New", size=9),
            text_color=C["dim"])
        ts_lbl.grid(row=0, column=2, padx=18, pady=12, sticky="e")

        def _tick(lbl=ts_lbl):
            lbl.configure(text=datetime.now().strftime("%d/%m/%Y  %H:%M:%S"))
            lbl.after(1000, _tick)
        _tick()

        return frame

    # =========================================================================
    #  NAVIGATION
    # =========================================================================
    def _show(self, key: str):
        if self.current_page in self.pages:
            self.pages[self.current_page].grid_remove()
        if key in self.pages:
            self.pages[key].grid(row=0, column=0, sticky="nsew")
            self.current_page = key
        for k, b in self.nav_btns.items():
            b.configure(
                fg_color=C["card2"] if k == key else "transparent",
                text_color=C["green"] if k == key else C["text"]
            )
        if key == "monitor":
            self._start_monitor()

    # =========================================================================
    #  CONSTRUCTION UI PRINCIPALE
    # =========================================================================
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Zone principale (droite)
        self._main = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        self._main.grid(row=0, column=1, sticky="nsew")
        self._main.grid_columnconfigure(0, weight=1)
        self._main.grid_rowconfigure(0, weight=1)

        self._build_sidebar()

        # Construire toutes les pages
        self._pg_dashboard()
        self._pg_system()
        self._pg_hardware()
        self._pg_network()
        self._pg_apps()
        self._pg_googleplay()
        self._pg_security()
        self._pg_developer()
        self._pg_data()
        self._pg_custom()
        self._pg_automation()
        self._pg_monitor()
        self._pg_terminal()

        self._show("dashboard")

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=240, fg_color=C["panel"], corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_columnconfigure(0, weight=1)
        sb.grid_rowconfigure(31, weight=1)

        # ── Logo ──────────────────────────────────────────────────────────
        logo_f = ctk.CTkFrame(sb, fg_color=C["card"], corner_radius=10)
        logo_f.grid(row=0, column=0, padx=12, pady=(16, 6), sticky="ew")

        ctk.CTkLabel(logo_f,
            text="⚡  ADB MASTER",
            font=ctk.CTkFont(family="Courier New", size=15, weight="bold"),
            text_color=C["green"]
        ).grid(row=0, column=0, padx=14, pady=(10, 2))

        ctk.CTkLabel(logo_f,
            text="v2.0 ELITE",
            font=ctk.CTkFont(family="Courier New", size=10),
            text_color=C["yellow"]
        ).grid(row=1, column=0, padx=14, pady=(0, 2))

        ctk.CTkLabel(logo_f,
            text="ML | exploit4040",
            font=ctk.CTkFont(size=9),
            text_color=C["dim"]
        ).grid(row=2, column=0, padx=14, pady=(0, 10))

        # ── Badge connexion ────────────────────────────────────────────────
        self.conn_badge = ctk.CTkLabel(sb,
            text="●  DÉCONNECTÉ",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=C["red"],
            fg_color=C["card"], corner_radius=6)
        self.conn_badge.grid(row=1, column=0, padx=14, pady=3, sticky="ew")

        # ── Bouton connecter ───────────────────────────────────────────────
        ctk.CTkButton(sb,
            text="🔌  Connecter / Rafraîchir",
            command=lambda: self._thread(self._connect_thread),
            fg_color=C["green"], hover_color=self._darken(C["green"]),
            text_color="#000",
            font=ctk.CTkFont(weight="bold"), height=36
        ).grid(row=2, column=0, padx=14, pady=(3, 10), sticky="ew")

        # Séparateur
        ctk.CTkFrame(sb, height=1, fg_color=C["border"]).grid(
            row=3, column=0, sticky="ew", padx=14, pady=2)

        # ── Navigation ────────────────────────────────────────────────────
        nav_items = [
            ("dashboard",  "🖥️",  "Dashboard"),
            ("system",     "📱",  "Système"),
            ("hardware",   "🔧",  "Hardware"),
            ("network",    "📶",  "Réseau"),
            ("apps",       "📦",  "Applications"),
            ("googleplay", "🛡️",  "Google Play Services"),
            ("security",   "🔒",  "Sécurité"),
            ("developer",  "⚙️",  "Options Développeur"),
            ("data",       "💾",  "Données & Stockage"),
            ("custom",     "🎨",  "Personnalisation"),
            ("automation", "🔄",  "Automatisation"),
            ("monitor",    "📊",  "Moniteur Live"),
            ("terminal",   "⚡",  "Terminal ADB"),
        ]
        for i, (key, icon, label) in enumerate(nav_items):
            btn = ctk.CTkButton(sb,
                text=f"{icon}   {label}",
                anchor="w",
                command=lambda k=key: self._show(k),
                fg_color="transparent",
                text_color=C["text"],
                hover_color=C["card"],
                font=ctk.CTkFont(size=11), height=36,
                border_spacing=10
            )
            btn.grid(row=4+i, column=0, padx=8, pady=1, sticky="ew")
            self.nav_btns[key] = btn

        # ── Info appareil ──────────────────────────────────────────────────
        ctk.CTkFrame(sb, height=1, fg_color=C["border"]).grid(
            row=31, column=0, sticky="ew", padx=14, pady=4)

        self.dev_lbl = ctk.CTkLabel(sb,
            text="Aucun appareil\nConnecte ton téléphone",
            font=ctk.CTkFont(size=9), text_color=C["dim"],
            justify="left", wraplength=210)
        self.dev_lbl.grid(row=32, column=0, padx=14, pady=(4, 16), sticky="w")

    # =========================================================================
    #  PAGE: DASHBOARD
    # =========================================================================
    def _pg_dashboard(self):
        p = self._make_page("dashboard", "DASHBOARD", "🖥️")
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # ── 4 cartes stats ────────────────────────────────────────────────
        self.dash_vals: dict = {}
        stat_defs = [
            ("model",   "📱 Modèle",      "---",  C["green"]),
            ("android", "🤖 Android",      "---",  C["blue"]),
            ("battery", "🔋 Batterie",     "---%", C["green"]),
            ("cpu",     "💻 CPU / ABI",    "---",  C["purple"]),
        ]
        for i, (key, title, default, col) in enumerate(stat_defs):
            sc = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=10)
            sc.grid(row=1, column=i, padx=8, pady=6, sticky="nsew")
            ctk.CTkLabel(sc, text=title,
                font=ctk.CTkFont(size=10), text_color=C["dim"]
            ).grid(row=0, column=0, padx=14, pady=(10, 2), sticky="w")
            lbl = ctk.CTkLabel(sc, text=default,
                font=ctk.CTkFont(family="Courier New", size=13, weight="bold"),
                text_color=col)
            lbl.grid(row=1, column=0, padx=14, pady=(2, 12), sticky="w")
            self.dash_vals[key] = lbl

        # ── Actions rapides ───────────────────────────────────────────────
        qa = ctk.CTkFrame(p, fg_color=C["panel"], corner_radius=10)
        qa.grid(row=2, column=0, columnspan=4, padx=8, pady=6, sticky="ew")
        qa.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        ctk.CTkLabel(qa, text="⚡  ACTIONS RAPIDES",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["dim"]
        ).grid(row=0, column=0, columnspan=6, padx=14, pady=(10, 4), sticky="w")

        quick = [
            ("📸 Screenshot",   self._quick_screenshot,                                         C["blue"]),
            ("🔄 Reboot",       lambda: self._shell_log("reboot", self.dash_log),               C["yellow"]),
            ("🧹 Vider Cache",  lambda: self._shell_log("pm trim-caches 999g", self.dash_log),  C["green"]),
            ("📶 WiFi ON",      lambda: self._shell_log("svc wifi enable", self.dash_log),      C["green"]),
            ("📴 WiFi OFF",     lambda: self._shell_log("svc wifi disable", self.dash_log),     C["red"]),
            ("🌙 Dark Mode",    lambda: self._shell_log("settings put secure ui_night_mode 2",  self.dash_log), C["purple"]),
        ]
        for i, (label, fn, color) in enumerate(quick):
            ctk.CTkButton(qa, text=label, command=fn,
                fg_color=color, hover_color=self._darken(color),
                font=ctk.CTkFont(size=11), height=42, corner_radius=8
            ).grid(row=1, column=i, padx=6, pady=(4, 12), sticky="ew")

        # ── Info device étendue ───────────────────────────────────────────
        info_c = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=10)
        info_c.grid(row=3, column=0, columnspan=2, padx=8, pady=6, sticky="nsew")
        info_c.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(info_c, text="📋  INFO APPAREIL",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["dim"]
        ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")

        self.dash_info_box = self._textbox(info_c, 130)
        self.dash_info_box.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        self._btn(info_c, "🔄 Actualiser Info",
                  lambda: self._thread(self._refresh_dashboard), 2, 0, C["blue"])

        # ── Journal ───────────────────────────────────────────────────────
        log_c = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=10)
        log_c.grid(row=3, column=2, columnspan=2, padx=8, pady=6, sticky="nsew")
        log_c.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(log_c, text="📝  JOURNAL D'ACTIVITÉ",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["dim"]
        ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")

        self.dash_log = self._textbox(log_c, 130)
        self.dash_log.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        self._btn(log_c, "🗑️ Effacer Journal",
                  lambda: self._clear_tb(self.dash_log), 2, 0, C["yellow"])

    def _refresh_dashboard(self):
        d = self.adb.device_info
        self.dash_vals["model"].configure(
            text=f"{d.get('brand','')} {d.get('model','?')}")
        self.dash_vals["android"].configure(
            text=f"Android {d.get('android','?')} (SDK {d.get('sdk','?')})")
        self.dash_vals["cpu"].configure(text=d.get("cpu", "?"))

        batt = self.adb.battery_level()
        if batt is not None:
            col = C["green"] if batt > 50 else (C["yellow"] if batt > 20 else C["red"])
            self.dash_vals["battery"].configure(text=f"{batt}%", text_color=col)

        # Info box
        lines = (
            f"  Marque     : {d.get('brand','?')}\n"
            f"  Modèle     : {d.get('model','?')}\n"
            f"  Android    : {d.get('android','?')}\n"
            f"  SDK        : {d.get('sdk','?')}\n"
            f"  CPU        : {d.get('cpu','?')}\n"
            f"  Série      : {d.get('serial','?')}\n"
            f"  ROM        : {d.get('rom','?')}\n"
            f"  Board      : {d.get('board','?')}\n"
        )
        self.dash_info_box.configure(state="normal")
        self.dash_info_box.delete("1.0", "end")
        self.dash_info_box.insert("end", lines)
        self.dash_info_box.configure(state="disabled")

        self._log(self.dash_log,
            f"✅ Connecté: {d.get('brand','')} {d.get('model','?')} "
            f"| Android {d.get('android','?')}")

    def _quick_screenshot(self):
        def _run():
            self.adb.shell("screencap -p /sdcard/_adb_ss.png")
            time.sleep(0.8)
            self.adb.run("pull /sdcard/_adb_ss.png ./screenshot_adb.png")
            self._log(self.dash_log, "📸 Screenshot sauvegardé → ./screenshot_adb.png")
        self._thread(_run)

    def _clear_tb(self, tb: ctk.CTkTextbox):
        tb.configure(state="normal")
        tb.delete("1.0", "end")
        tb.configure(state="disabled")

    # =========================================================================
    #  PAGE: SYSTÈME
    # =========================================================================
    def _pg_system(self):
        p = self._make_page("system", "PARAMÈTRES SYSTÈME", "📱")
        p.grid_columnconfigure((0, 1), weight=1)

        # Sortie
        out_f = ctk.CTkFrame(p, fg_color=C["panel"], corner_radius=10)
        out_f.grid(row=4, column=0, columnspan=2, padx=8, pady=8, sticky="ew")
        out_f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(out_f, text="📤  SORTIE",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["dim"]
        ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")
        self.sys_out = self._textbox(out_f, 130)
        self.sys_out.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # ── Redémarrages ──────────────────────────────────────────────────
        rc = self._card(p, 1, 0, "⚡ REDÉMARRAGES & ALIMENTATION")
        rc.grid_columnconfigure(0, weight=1)
        reboot_cmds = [
            ("🔄 Redémarrer Normal",      "reboot",           C["yellow"]),
            ("🔧 Mode Recovery",          "reboot recovery",  C["red"]),
            ("🔓 Mode Bootloader",        "reboot bootloader",C["red"]),
            ("⏻  Éteindre",               "reboot -p",        C["red"]),
            ("🔥 Redémarrer SysUI",       "killall com.android.systemui", C["orange"]),
        ]
        for i, (lbl, cmd, col) in enumerate(reboot_cmds):
            self._btn(rc, lbl, lambda c=cmd: self._shell_log(c, self.sys_out),
                      i+1, 0, col)

        # ── Paramètres ────────────────────────────────────────────────────
        pc = self._card(p, 1, 1, "⚙️ NAVIGUER VERS PARAMÈTRES")
        pc.grid_columnconfigure(0, weight=1)
        settings_cmds = [
            ("🔧 Tous les Paramètres",    "am start -a android.settings.SETTINGS",                     C["blue"]),
            ("📱 À Propos du Téléphone",  "am start -a android.settings.DEVICE_INFO_SETTINGS",         C["blue"]),
            ("👨‍💻 Options Développeur",   "am start -a android.settings.APPLICATION_DEVELOPMENT_SETTINGS", C["blue"]),
            ("🌐 Langue & Région",        "am start -a android.settings.LOCALE_SETTINGS",              C["blue"]),
            ("📅 Date & Heure",           "am start -a android.settings.DATE_SETTINGS",                C["blue"]),
            ("🔄 Mise à Jour Système",    "am start -a android.settings.SYSTEM_UPDATE_SETTINGS",       C["blue"]),
            ("🔒 Sécurité",               "am start -a android.settings.SECURITY_SETTINGS",            C["blue"]),
            ("🔔 Sons & Notifications",   "am start -a android.settings.SOUND_SETTINGS",               C["blue"]),
        ]
        for i, (lbl, cmd, col) in enumerate(settings_cmds):
            self._btn(pc, lbl, lambda c=cmd: self._shell_log(c, self.sys_out),
                      i+1, 0, col)

        # ── Nettoyage système ─────────────────────────────────────────────
        cl = self._card(p, 2, 0, "🧹 NETTOYAGE SYSTÈME", cspan=2)
        cl.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        clean_cmds = [
            ("🗑️ Vider Cache Sys.",    "pm trim-caches 999g",                 C["yellow"]),
            ("⏹️ Arrêter Toutes Apps", "am kill-all",                          C["yellow"]),
            ("🔄 Sync Forçée",         "content call --uri content://settings",C["blue"]),
            ("📊 Mémoire",             "dumpsys meminfo | head -30",           C["purple"]),
            ("🌡️ Température CPU",     "cat /sys/class/thermal/thermal_zone0/temp", C["orange"]),
        ]
        for i, (lbl, cmd, col) in enumerate(clean_cmds):
            self._btn(cl, lbl, lambda c=cmd: self._shell_log(c, self.sys_out),
                      1, i, col)

        # ── Props système ─────────────────────────────────────────────────
        props_c = self._card(p, 3, 0, "🔬 PROPRIÉTÉS SYSTÈME", cspan=2)
        props_c.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        props_cmds = [
            ("📱 Modèle",      "getprop ro.product.model",           C["green"]),
            ("🤖 Android",     "getprop ro.build.version.release",   C["green"]),
            ("🏭 Fabricant",   "getprop ro.product.manufacturer",    C["green"]),
            ("📡 Radio",       "getprop gsm.version.baseband",       C["blue"]),
            ("🔑 Fingerprint", "getprop ro.build.fingerprint",       C["purple"]),
        ]
        for i, (lbl, cmd, col) in enumerate(props_cmds):
            self._btn(props_c, lbl, lambda c=cmd: self._shell_log(c, self.sys_out),
                      1, i, col)

    # =========================================================================
    #  PAGE: HARDWARE
    # =========================================================================
    def _pg_hardware(self):
        p = self._make_page("hardware", "CONTRÔLE HARDWARE", "🔧")
        p.grid_columnconfigure((0, 1, 2), weight=1)

        # Sortie
        out_f = ctk.CTkFrame(p, fg_color=C["panel"], corner_radius=10)
        out_f.grid(row=4, column=0, columnspan=3, padx=8, pady=8, sticky="ew")
        out_f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(out_f, text="📤  SORTIE HARDWARE",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["dim"]
        ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")
        self.hw_out = self._textbox(out_f, 110)
        self.hw_out.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # ── Luminosité ────────────────────────────────────────────────────
        bc = self._card(p, 1, 0, "☀️ LUMINOSITÉ")
        bc.grid_columnconfigure(0, weight=1)

        self.bright_val_lbl = ctk.CTkLabel(bc, text="70%",
            font=ctk.CTkFont(family="Courier New", size=28, weight="bold"),
            text_color=C["yellow"])
        self.bright_val_lbl.grid(row=1, column=0, pady=(6, 2))

        self.bright_sl = ctk.CTkSlider(bc, from_=0, to=100,
            progress_color=C["yellow"], button_color=C["yellow"],
            command=self._on_bright_slide)
        self.bright_sl.set(70)
        self.bright_sl.grid(row=2, column=0, padx=14, pady=6, sticky="ew")

        bright_btns = ctk.CTkFrame(bc, fg_color="transparent")
        bright_btns.grid(row=3, column=0, padx=8, pady=(0, 12), sticky="ew")
        bright_btns.grid_columnconfigure((0, 1, 2, 3), weight=1)
        for j, (lbl, val, col) in enumerate([
            ("MIN",  0,   C["red"]),
            ("25%",  25,  C["yellow"]),
            ("75%",  75,  C["blue"]),
            ("MAX",  100, C["green"]),
        ]):
            ctk.CTkButton(bright_btns, text=lbl,
                command=lambda v=val: self._set_bright(v),
                fg_color=col, hover_color=self._darken(col),
                font=ctk.CTkFont(size=10), height=30
            ).grid(row=0, column=j, padx=3, sticky="ew")

        bright_auto_row = ctk.CTkFrame(bc, fg_color="transparent")
        bright_auto_row.grid(row=4, column=0, padx=8, pady=(0, 12), sticky="ew")
        bright_auto_row.grid_columnconfigure((0, 1), weight=1)
        self._btn(bright_auto_row, "🔆 AUTO ON",
                  lambda: self._shell_log("settings put system screen_brightness_mode 1", self.hw_out),
                  0, 0, C["green"])
        self._btn(bright_auto_row, "🔅 AUTO OFF",
                  lambda: self._shell_log("settings put system screen_brightness_mode 0", self.hw_out),
                  0, 1, C["red"])

        # ── Volume ────────────────────────────────────────────────────────
        vc = self._card(p, 1, 1, "🔊 VOLUME")
        vc.grid_columnconfigure(0, weight=1)

        self.vol_val_lbl = ctk.CTkLabel(vc, text="8 / 15",
            font=ctk.CTkFont(family="Courier New", size=28, weight="bold"),
            text_color=C["blue"])
        self.vol_val_lbl.grid(row=1, column=0, pady=(6, 2))

        self.vol_sl = ctk.CTkSlider(vc, from_=0, to=15,
            progress_color=C["blue"], button_color=C["blue"],
            command=self._on_vol_slide)
        self.vol_sl.set(8)
        self.vol_sl.grid(row=2, column=0, padx=14, pady=6, sticky="ew")

        for j, (lbl, cmd, col) in enumerate([
            ("🔕 Silencieux",  "settings put system mode_ringer 0", C["red"]),
            ("📳 Vibration",   "settings put system mode_ringer 1", C["yellow"]),
            ("🔔 Normal",      "settings put system mode_ringer 2", C["green"]),
        ]):
            self._btn(vc, lbl, lambda c=cmd: self._shell_log(c, self.hw_out),
                      j+3, 0, col, height=32)

        # ── Batterie ──────────────────────────────────────────────────────
        btc = self._card(p, 1, 2, "🔋 BATTERIE")
        btc.grid_columnconfigure(0, weight=1)

        self.hw_batt_lbl = ctk.CTkLabel(btc, text="---%",
            font=ctk.CTkFont(family="Courier New", size=30, weight="bold"),
            text_color=C["green"])
        self.hw_batt_lbl.grid(row=1, column=0, pady=(8, 2))

        self.hw_temp_lbl = ctk.CTkLabel(btc, text="🌡️  ---°C",
            font=ctk.CTkFont(size=12), text_color=C["yellow"])
        self.hw_temp_lbl.grid(row=2, column=0, pady=2)

        self.hw_status_lbl = ctk.CTkLabel(btc, text="--- ",
            font=ctk.CTkFont(size=10), text_color=C["dim"])
        self.hw_status_lbl.grid(row=3, column=0, pady=2)

        self._btn(btc, "🔄 Actualiser",     self._refresh_battery, 4, 0, C["green"])
        self._btn(btc, "📊 Détails Battery", lambda: self._shell_log("dumpsys battery", self.hw_out), 5, 0, C["blue"])

        # ── Écran & Affichage ─────────────────────────────────────────────
        dc = self._card(p, 2, 0, "🖥️ ÉCRAN & AFFICHAGE", cspan=3)
        dc.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        disp_cmds = [
            ("🔄 Rotation AUTO",   "settings put system accelerometer_rotation 1", C["blue"]),
            ("🔒 Rotation OFF",    "settings put system accelerometer_rotation 0", C["yellow"]),
            ("💡 Écran ON",        "input keyevent 224",                           C["green"]),
            ("🌑 Écran OFF",       "input keyevent 223",                           C["red"]),
            ("⚡ 60Hz",            "settings put system peak_refresh_rate 60",     C["blue"]),
            ("⚡ 90Hz",            "settings put system peak_refresh_rate 90",     C["cyan"]),
            ("⚡ 120Hz",           "settings put system peak_refresh_rate 120",    C["purple"]),
            ("📐 Résolution",      "wm size",                                      C["dim"]),
        ]
        for i, (lbl, cmd, col) in enumerate(disp_cmds):
            self._btn(dc, lbl, lambda c=cmd: self._shell_log(c, self.hw_out),
                      1, i, col)

        # ── Touches & Actions ─────────────────────────────────────────────
        kc = self._card(p, 3, 0, "⌨️ TOUCHES & ACTIONS", cspan=3)
        kc.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        key_cmds = [
            ("⬅️ Retour",        "input keyevent 4",  C["dim"]),
            ("🏠 Accueil",        "input keyevent 3",  C["blue"]),
            ("📋 Récents",        "input keyevent 187",C["blue"]),
            ("🔊 Vol+",           "input keyevent 24", C["green"]),
            ("🔉 Vol-",           "input keyevent 25", C["green"]),
            ("📸 Photo",          "input keyevent 27", C["purple"]),
            ("🔒 Verrouiller",    "input keyevent 26", C["yellow"]),
            ("🌙 Veille",         "input keyevent 223",C["red"]),
        ]
        for i, (lbl, cmd, col) in enumerate(key_cmds):
            self._btn(kc, lbl, lambda c=cmd: self._shell_log(c, self.hw_out),
                      1, i, col)

    def _on_bright_slide(self, v):
        self.bright_val_lbl.configure(text=f"{int(v)}%")

    def _set_bright(self, pct: int):
        self.bright_sl.set(pct)
        self.bright_val_lbl.configure(text=f"{pct}%")
        val = int((pct * 255) / 100)
        self._shell_log(f"settings put system screen_brightness {val}", self.hw_out)

    def _on_vol_slide(self, v):
        vol = int(v)
        self.vol_val_lbl.configure(text=f"{vol} / 15")
        self._shell_log(f"media volume --stream 3 --set {vol}", self.hw_out)

    def _refresh_battery(self):
        def _run():
            lvl    = self.adb.battery_level()
            temp   = self.adb.battery_temp()
            status = self.adb.battery_status()
            if lvl is not None:
                col = C["green"] if lvl > 50 else (C["yellow"] if lvl > 20 else C["red"])
                self.hw_batt_lbl.configure(text=f"{lvl}%", text_color=col)
                self.dash_vals["battery"].configure(text=f"{lvl}%", text_color=col)
            if temp is not None:
                self.hw_temp_lbl.configure(text=f"🌡️  {temp}°C")
            if status:
                self.hw_status_lbl.configure(text=status)
        self._thread(_run)

    # =========================================================================
    #  PAGE: RÉSEAU
    # =========================================================================
    def _pg_network(self):
        p = self._make_page("network", "CONTRÔLE RÉSEAU", "📶")
        p.grid_columnconfigure((0, 1, 2), weight=1)

        out_f = ctk.CTkFrame(p, fg_color=C["panel"], corner_radius=10)
        out_f.grid(row=3, column=0, columnspan=3, padx=8, pady=8, sticky="ew")
        out_f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(out_f, text="📤  SORTIE RÉSEAU",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["dim"]
        ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")
        self.net_out = self._textbox(out_f, 160)
        self.net_out.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        groups = [
            ("📶 WiFi", [
                ("✅ WiFi ON",           "svc wifi enable",                              C["green"]),
                ("❌ WiFi OFF",          "svc wifi disable",                             C["red"]),
                ("🔍 Scan SSID",         "dumpsys wifi | grep SSID",                    C["blue"]),
                ("📡 IP wlan0",          "ip addr show wlan0",                           C["blue"]),
                ("🌍 Ping Google",       "ping -c 3 8.8.8.8",                           C["green"]),
                ("🔗 Infos Connexion",   "dumpsys connectivity | head -30",             C["purple"]),
            ]),
            ("📱 Données Mobiles", [
                ("✅ Données ON",        "svc data enable",                              C["green"]),
                ("❌ Données OFF",       "svc data disable",                             C["red"]),
                ("✈️ Mode Avion ON",     "settings put global airplane_mode_on 1",      C["yellow"]),
                ("✈️ Mode Avion OFF",    "settings put global airplane_mode_on 0",      C["green"]),
                ("4G / LTE",             "settings put global preferred_network_mode 12",C["blue"]),
                ("3G",                   "settings put global preferred_network_mode 8", C["blue"]),
            ]),
            ("🔵 Bluetooth & Hotspot", [
                ("🔵 Bluetooth",          "am start -a android.settings.BLUETOOTH_SETTINGS",C["purple"]),
                ("🌐 Hotspot",            "am start -n com.android.settings/.TetherSettings",C["blue"]),
                ("📊 Netstat",            "netstat",                                          C["cyan"]),
                ("🔍 DNS",               "getprop net.dns1",                                 C["dim"]),
                ("📶 Signal GSM",         "dumpsys telephony.registry | grep Strength | head -3", C["yellow"]),
                ("🔗 Interfaces",         "ip link show",                                     C["green"]),
            ]),
        ]
        for gi, (gtitle, actions) in enumerate(groups):
            c = self._card(p, 1, gi, gtitle)
            c.grid_columnconfigure(0, weight=1)
            for j, (lbl, cmd, col) in enumerate(actions):
                self._btn(c, lbl, lambda cc=cmd: self._shell_log(cc, self.net_out),
                          j+1, 0, col)

        # Commande ping custom
        ping_c = self._card(p, 2, 0, "🌍 PING CUSTOM", cspan=3)
        ping_c.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(ping_c, text="Hôte:",
            font=ctk.CTkFont(size=10), text_color=C["dim"]
        ).grid(row=1, column=0, padx=14, pady=8)
        self.ping_entry = ctk.CTkEntry(ping_c, placeholder_text="8.8.8.8  ou  google.com",
            fg_color=C["bg"], border_color=C["border"],
            font=ctk.CTkFont(family="Courier New", size=11), height=34)
        self.ping_entry.grid(row=1, column=1, padx=4, pady=8, sticky="ew")
        self._btn(ping_c, "🌍 Ping", self._do_ping, 1, 2, C["green"])

    def _do_ping(self):
        host = self.ping_entry.get().strip() or "8.8.8.8"
        self._shell_log(f"ping -c 4 {host}", self.net_out)

    # =========================================================================
    #  PAGE: APPLICATIONS
    # =========================================================================
    def _pg_apps(self):
        p = self._make_page("apps", "GESTIONNAIRE D'APPLICATIONS", "📦")
        p.grid_columnconfigure((0, 1), weight=1)

        # ── Barre de recherche / filtres ──────────────────────────────────
        sb = ctk.CTkFrame(p, fg_color=C["panel"], corner_radius=10)
        sb.grid(row=1, column=0, columnspan=2, padx=8, pady=6, sticky="ew")
        sb.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(sb, text="🔍",
            font=ctk.CTkFont(size=16)
        ).grid(row=0, column=0, padx=(14, 4), pady=10)

        self.app_search = ctk.CTkEntry(sb,
            placeholder_text="Filtrer les packages...",
            fg_color=C["bg"], border_color=C["border"],
            font=ctk.CTkFont(size=12), height=36)
        self.app_search.grid(row=0, column=1, padx=4, pady=10, sticky="ew")

        for i, (lbl, fn, col) in enumerate([
            ("📋 Toutes",        self._list_all_apps,      C["blue"]),
            ("👤 Utilisateur",   self._list_user_apps,     C["green"]),
            ("⚙️ Système",       self._list_sys_apps,      C["purple"]),
            ("🔴 Désactivées",   self._list_disabled_apps, C["red"]),
        ]):
            ctk.CTkButton(sb, text=lbl, command=fn, width=110,
                fg_color=col, hover_color=self._darken(col),
                font=ctk.CTkFont(size=10), height=32
            ).grid(row=0, column=2+i, padx=3, pady=10)

        # ── Liste packages ────────────────────────────────────────────────
        lc = self._card(p, 2, 0, "📋 LISTE DES PACKAGES")
        lc.grid_columnconfigure(0, weight=1)
        lc.grid_rowconfigure(1, weight=1)
        p.grid_rowconfigure(2, weight=1)
        self.app_list = self._textbox(lc, 340)
        self.app_list.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # ── Actions ───────────────────────────────────────────────────────
        ac = self._card(p, 2, 1, "⚡ ACTIONS SUR PACKAGE")
        ac.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(ac, text="Package cible:",
            font=ctk.CTkFont(size=10), text_color=C["dim"]
        ).grid(row=1, column=0, padx=14, pady=(8, 2), sticky="w")

        self.pkg_entry = ctk.CTkEntry(ac,
            placeholder_text="com.example.package",
            fg_color=C["bg"], border_color=C["border"],
            font=ctk.CTkFont(family="Courier New", size=11), height=34)
        self.pkg_entry.grid(row=2, column=0, padx=10, pady=4, sticky="ew")

        pkg_actions = [
            ("🚫 Désinstaller (user 0)",  self._app_uninstall,    C["red"]),
            ("🔕 Désactiver Package",     self._app_disable,      C["yellow"]),
            ("✅ Activer Package",         self._app_enable,       C["green"]),
            ("⏹️ Forcer Arrêt",           self._app_force_stop,   C["yellow"]),
            ("🗑️ Vider Cache & Données",  self._app_clear,        C["orange"]),
            ("📋 Infos Détaillées",       self._app_info,         C["purple"]),
            ("🚀 Lancer App",             self._app_launch,       C["green"]),
            ("🔑 Voir Permissions",       self._app_perms,        C["blue"]),
            ("📥 Extraire APK (pull)",    self._app_extract_apk,  C["cyan"]),
        ]
        for i, (lbl, fn, col) in enumerate(pkg_actions):
            self._btn(ac, lbl, fn, i+3, 0, col, height=34)

        # ── Bloatware ─────────────────────────────────────────────────────
        blc = self._card(p, 3, 0, "🗑️ SUPPRESSION BLOATWARE", cspan=2)
        blc.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        bloat = [
            ("Facebook",    "com.facebook.katana"),
            ("FB Services", "com.facebook.services"),
            ("Instagram",   "com.instagram.android"),
            ("TikTok",      "com.zhiliaoapp.musically"),
            ("Twitter/X",   "com.twitter.android"),
            ("LinkedIn",    "com.linkedin.android"),
            ("Netflix",     "com.netflix.mediaclient"),
            ("🗑️ TOUS",     None),
        ]
        for i, (name, pkg) in enumerate(bloat):
            col = C["red"] if name == "🗑️ TOUS" else C["yellow"]
            fn = (self._remove_all_bloat
                  if pkg is None
                  else (lambda pp=pkg: self._bloat_pkg(pp)))
            ctk.CTkButton(blc, text=name, command=fn,
                fg_color=col, hover_color=self._darken(col),
                font=ctk.CTkFont(size=10), height=30
            ).grid(row=1, column=i, padx=3, pady=(0, 12), sticky="ew")

    def _pkg(self) -> str:
        return self.pkg_entry.get().strip()

    def _list_all_apps(self):
        def _run():
            apps = sorted(self.adb.list_packages())
            q = self.app_search.get().strip().lower()
            if q:
                apps = [a for a in apps if q in a.lower()]
            self.app_list.configure(state="normal")
            self.app_list.delete("1.0", "end")
            self.app_list.insert("end",
                f"  Total: {len(apps)} packages\n{'─'*42}\n")
            for a in apps:
                self.app_list.insert("end", f"  {a}\n")
            self.app_list.configure(state="disabled")
        self._thread(_run)

    def _list_user_apps(self):
        def _run():
            apps = sorted(self.adb.list_packages("-3"))
            self.app_list.configure(state="normal")
            self.app_list.delete("1.0", "end")
            self.app_list.insert("end",
                f"  Apps utilisateur: {len(apps)}\n{'─'*42}\n")
            for a in apps:
                self.app_list.insert("end", f"  📱 {a}\n")
            self.app_list.configure(state="disabled")
        self._thread(_run)

    def _list_sys_apps(self):
        def _run():
            all_a = set(self.adb.list_packages())
            usr_a = set(self.adb.list_packages("-3"))
            sys_a = sorted(all_a - usr_a)
            self.app_list.configure(state="normal")
            self.app_list.delete("1.0", "end")
            self.app_list.insert("end",
                f"  Apps système: {len(sys_a)}\n{'─'*42}\n")
            for a in sys_a:
                self.app_list.insert("end", f"  ⚙️ {a}\n")
            self.app_list.configure(state="disabled")
        self._thread(_run)

    def _list_disabled_apps(self):
        def _run():
            apps = sorted(self.adb.list_packages("-d"))
            self.app_list.configure(state="normal")
            self.app_list.delete("1.0", "end")
            self.app_list.insert("end",
                f"  Apps désactivées: {len(apps)}\n{'─'*42}\n")
            for a in apps:
                self.app_list.insert("end", f"  🔕 {a}\n")
            self.app_list.configure(state="disabled")
        self._thread(_run)

    def _app_uninstall(self):
        pkg = self._pkg()
        if not pkg:
            return
        def _run():
            r = self.adb.run(f"uninstall {pkg}")
            out = r.stdout.strip() if r else "Erreur"
            self._log(self.app_list, f"UNINSTALL {pkg} → {out}")
        self._thread(_run)

    def _app_disable(self):
        pkg = self._pkg()
        if pkg:
            self._shell_log(f"pm disable-user --user 0 {pkg}", self.app_list)

    def _app_enable(self):
        pkg = self._pkg()
        if pkg:
            self._shell_log(f"pm enable {pkg}", self.app_list)

    def _app_force_stop(self):
        pkg = self._pkg()
        if pkg:
            self._shell_log(f"am force-stop {pkg}", self.app_list)

    def _app_clear(self):
        pkg = self._pkg()
        if pkg:
            self._shell_log(f"pm clear {pkg}", self.app_list)

    def _app_info(self):
        pkg = self._pkg()
        if not pkg:
            return
        def _run():
            r = self.adb.shell(f"dumpsys package {pkg}")
            out = r.stdout[:1500] if r and r.stdout else "Package introuvable"
            self._log(self.app_list, f"─── {pkg} ───\n{out}")
        self._thread(_run)

    def _app_launch(self):
        pkg = self._pkg()
        if pkg:
            self._shell_log(f"monkey -p {pkg} 1", self.app_list)

    def _app_perms(self):
        pkg = self._pkg()
        if not pkg:
            return
        def _run():
            r = self.adb.shell(f"dumpsys package {pkg}")
            if r and r.stdout:
                lines = [l for l in r.stdout.split("\n")
                         if "permission" in l.lower() or "granted" in l.lower()]
                self._log(self.app_list,
                    f"Permissions {pkg}:\n" + "\n".join(lines[:40]))
        self._thread(_run)

    def _app_extract_apk(self):
        pkg = self._pkg()
        if not pkg:
            return
        def _run():
            r = self.adb.shell(f"pm path {pkg}")
            if r and r.stdout:
                path = r.stdout.strip().replace("package:", "")
                self._log(self.app_list, f"APK path: {path}")
                self.adb.run(f"pull {path} ./{pkg}.apk")
                self._log(self.app_list, f"📥 Extrait → ./{pkg}.apk")
        self._thread(_run)

    def _bloat_pkg(self, pkg: str):
        self._shell_log(f"pm uninstall --user 0 {pkg}", self.app_list)

    def _remove_all_bloat(self):
        pkgs = [
            "com.facebook.katana", "com.facebook.services",
            "com.instagram.android", "com.zhiliaoapp.musically",
            "com.twitter.android", "com.linkedin.android",
            "com.netflix.mediaclient",
        ]
        def _run():
            for pkg in pkgs:
                self.adb.shell(f"pm uninstall --user 0 {pkg}")
                self._log(self.app_list, f"  🗑️ {pkg}")
                time.sleep(0.3)
            self._log(self.app_list, "✅ Bloatwares supprimés")
        self._thread(_run)

    # =========================================================================
    #  PAGE: GOOGLE PLAY SERVICES
    # =========================================================================
    def _pg_googleplay(self):
        p = self._make_page("googleplay", "GOOGLE PLAY SERVICES", "🛡️")
        p.grid_columnconfigure((0, 1), weight=1)

        # ── Status ────────────────────────────────────────────────────────
        sc = ctk.CTkFrame(p, fg_color=C["panel"], corner_radius=10)
        sc.grid(row=1, column=0, columnspan=2, padx=8, pady=6, sticky="ew")
        sc.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(sc, text=f"📦  {GPS_PKG}",
            font=ctk.CTkFont(family="Courier New", size=12),
            text_color=C["dim"]
        ).grid(row=0, column=0, padx=14, pady=12)

        self.gp_status_lbl = ctk.CTkLabel(sc,
            text="●  ÉTAT INCONNU",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=C["yellow"])
        self.gp_status_lbl.grid(row=0, column=1, padx=14, pady=12)

        ctk.CTkButton(sc, text="🔄 Vérifier", width=120,
            command=self._gp_check,
            fg_color=C["blue"], hover_color=self._darken(C["blue"])
        ).grid(row=0, column=2, padx=(4, 14), pady=12)

        # ── Boutons principaux ─────────────────────────────────────────────
        toggle = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=10)
        toggle.grid(row=2, column=0, columnspan=2, padx=8, pady=6, sticky="ew")
        toggle.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(toggle,
            text="🔴   DÉSACTIVER   Google Play Services",
            command=self._gp_disable,
            fg_color=C["red"], hover_color=self._darken(C["red"]),
            font=ctk.CTkFont(size=14, weight="bold"), height=56
        ).grid(row=0, column=0, padx=14, pady=16, sticky="ew")

        ctk.CTkButton(toggle,
            text="🟢   ACTIVER   Google Play Services",
            command=self._gp_enable,
            fg_color=C["green"], hover_color=self._darken(C["green"]),
            font=ctk.CTkFont(size=14, weight="bold"), height=56,
            text_color="#000"
        ).grid(row=0, column=1, padx=14, pady=16, sticky="ew")

        # ── Opérations avancées ────────────────────────────────────────────
        adv = self._card(p, 3, 0, "⚙️ OPÉRATIONS AVANCÉES")
        adv.grid_columnconfigure(0, weight=1)
        adv_items = [
            ("⏹️ Forcer Arrêt GPS",         f"am force-stop {GPS_PKG}",                                  C["yellow"]),
            ("🗑️ Vider Cache GPS",           f"pm clear {GPS_PKG}",                                      C["yellow"]),
            ("🔐 Restaurer Permissions",     None,                                                        C["blue"]),
            ("📊 Version Installée",         f"dumpsys package {GPS_PKG} | grep versionName",            C["purple"]),
            ("📁 Chemin APK",                f"pm path {GPS_PKG}",                                       C["cyan"]),
            ("🔄 Restart SurfaceFlinger",    "setprop ctl.restart surfaceflinger",                       C["orange"]),
            ("🌐 Sync Accounts",             "am broadcast -a android.intent.action.SYNC_STATE_CHANGED", C["green"]),
        ]
        for i, (lbl, cmd, col) in enumerate(adv_items):
            fn = (lambda cc=cmd: self._shell_log(cc, self.gp_out)) if cmd else self._gp_restore_perms
            self._btn(adv, lbl, fn, i+1, 0, col)

        # ── Conséquences ──────────────────────────────────────────────────
        wc = self._card(p, 3, 1, "⚠️ CONSÉQUENCES DE LA DÉSACTIVATION")
        wc.grid_columnconfigure(0, weight=1)

        for i, (txt, col) in enumerate([
            ("❌  Google Play Store inaccessible",         C["red"]),
            ("❌  Gmail / Maps / Drive cassés",            C["red"]),
            ("❌  Synchronisation désactivée",             C["red"]),
            ("❌  Notifications push stoppées",            C["red"]),
            ("❌  Authentification Google cassée",         C["red"]),
            ("❌  Google Assistant inutilisable",          C["red"]),
            ("─" * 36,                                     C["border"]),
            ("✅  Économie batterie significative",        C["green"]),
            ("✅  Réduction du tracking Google",           C["green"]),
            ("✅  Gain d'espace stockage",                 C["green"]),
            ("✅  Meilleures performances générales",      C["green"]),
            ("✅  Moins de connectivité en arrière-plan", C["green"]),
        ]):
            ctk.CTkLabel(wc, text=txt,
                font=ctk.CTkFont(size=10), text_color=col
            ).grid(row=i+1, column=0, padx=14, pady=2, sticky="w")

        # ── Journal ───────────────────────────────────────────────────────
        gout_f = ctk.CTkFrame(p, fg_color=C["panel"], corner_radius=10)
        gout_f.grid(row=4, column=0, columnspan=2, padx=8, pady=8, sticky="ew")
        gout_f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(gout_f, text="📤  JOURNAL GPS",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["dim"]
        ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")
        self.gp_out = self._textbox(gout_f, 130)
        self.gp_out.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

    def _gp_check(self):
        def _run():
            status = self.adb.gps_status()
            if status == "DISABLED":
                self.gp_status_lbl.configure(text="●  DÉSACTIVÉ", text_color=C["red"])
                self._log(self.gp_out, "État GPS: DÉSACTIVÉ ⛔")
            elif status == "ENABLED":
                self.gp_status_lbl.configure(text="●  ACTIF", text_color=C["green"])
                self._log(self.gp_out, "État GPS: ACTIF ✅")
            else:
                self.gp_status_lbl.configure(text="●  INTROUVABLE", text_color=C["yellow"])
                self._log(self.gp_out, "GPS package introuvable sur cet appareil ⚠️")
        self._thread(_run)

    def _gp_disable(self):
        def _run():
            self._log(self.gp_out, "⏳ Désactivation de Google Play Services...")
            methods = [
                f"pm disable-user --user 0 {GPS_PKG}",
                f"pm disable {GPS_PKG}",
                f"cmd package disable-user --user 0 {GPS_PKG}",
            ]
            for m in methods:
                r = self.adb.shell(m)
                if r and any(k in r.stdout.lower()
                             for k in ("disabled", "success")):
                    self.adb.shell(f"am force-stop {GPS_PKG}")
                    self.adb.shell(f"pm clear {GPS_PKG}")
                    self.gp_status_lbl.configure(text="●  DÉSACTIVÉ", text_color=C["red"])
                    self._log(self.gp_out,
                        f"✅ Désactivé via: {m}\n"
                        "📝 Redémarrez le téléphone pour finaliser.")
                    self.adb.log("GPS désactivé")
                    return
            self._log(self.gp_out, "❌ Toutes les méthodes ont échoué\n"
                "Vérifiez les droits root ou utilisez la méthode --user 0.")
        self._thread(_run)

    def _gp_enable(self):
        def _run():
            self._log(self.gp_out, "⏳ Activation de Google Play Services...")
            methods = [
                f"pm enable {GPS_PKG}",
                f"cmd package enable {GPS_PKG}",
                f"pm enable-user --user 0 {GPS_PKG}",
                f"pm install-existing {GPS_PKG}",
            ]
            for m in methods:
                r = self.adb.shell(m)
                if r and any(k in r.stdout.lower()
                             for k in ("enabled", "success", "package")):
                    self.gp_status_lbl.configure(text="●  ACTIF", text_color=C["green"])
                    self._log(self.gp_out,
                        f"✅ Activé via: {m}\n"
                        "📝 Redémarrez le téléphone pour finaliser.")
                    self.adb.log("GPS activé")
                    return
            self._log(self.gp_out,
                "❌ Échec — redémarrez le téléphone et réessayez.")
        self._thread(_run)

    def _gp_restore_perms(self):
        perms = [
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.ACCESS_COARSE_LOCATION",
            "android.permission.INTERNET",
            "android.permission.ACCESS_NETWORK_STATE",
            "android.permission.ACCESS_WIFI_STATE",
            "android.permission.GET_ACCOUNTS",
            "android.permission.READ_CONTACTS",
            "android.permission.WRITE_CONTACTS",
            "android.permission.READ_PHONE_STATE",
            "android.permission.RECEIVE_BOOT_COMPLETED",
            "android.permission.WAKE_LOCK",
            "android.permission.FOREGROUND_SERVICE",
        ]
        def _run():
            self._log(self.gp_out, f"🔐 Restauration de {len(perms)} permissions...")
            for perm in perms:
                self.adb.shell(f"pm grant {GPS_PKG} {perm}")
                time.sleep(0.08)
            self._log(self.gp_out, "✅ Permissions restaurées")
        self._thread(_run)

    # =========================================================================
    #  PAGE: SÉCURITÉ
    # =========================================================================
    def _pg_security(self):
        p = self._make_page("security", "SÉCURITÉ & VERROUILLAGE", "🔒")
        p.grid_columnconfigure((0, 1), weight=1)

        out_f = ctk.CTkFrame(p, fg_color=C["panel"], corner_radius=10)
        out_f.grid(row=4, column=0, columnspan=2, padx=8, pady=8, sticky="ew")
        out_f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(out_f, text="📤  SORTIE SÉCURITÉ",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["dim"]
        ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")
        self.sec_out = self._textbox(out_f, 150)
        self.sec_out.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        groups = [
            ("🔐 VERROUILLAGE ÉCRAN", [
                ("🔓 Désactiver Verrou",        "locksettings clear --old 1234",        C["red"]),
                ("✅ Activer Verrou",            "locksettings enable",                  C["green"]),
                ("🔢 PIN → 0000",               "locksettings set-pin 0000",            C["yellow"]),
                ("🛡️ Politique Sécurité",       "dumpsys device_policy",               C["blue"]),
                ("⚙️ Paramètres Sécurité",      "am start -a android.settings.SECURITY_SETTINGS", C["blue"]),
                ("📋 Admin Appareils",           "dumpsys device_policy | grep admin",  C["purple"]),
            ]),
            ("📍 LOCALISATION & PERMISSIONS", [
                ("📍 Localisation OFF",         "settings put secure location_mode 0",  C["red"]),
                ("📍 GPS+Réseau ON",            "settings put secure location_mode 3",  C["green"]),
                ("📍 GPS Seulement",            "settings put secure location_mode 1",  C["yellow"]),
                ("🔑 Perms App Cible",          self._sec_analyze_pkg,                  C["purple"]),
                ("🚫 Révoquer Localisation",    self._sec_revoke_loc,                   C["red"]),
                ("🛑 Supprimer Admin Device",   "dpm remove-active-admin",             C["orange"]),
            ]),
        ]
        for gi, (gtitle, actions) in enumerate(groups):
            c = self._card(p, 1, gi, gtitle)
            c.grid_columnconfigure(0, weight=1)
            for j, item in enumerate(actions):
                lbl, act, col = item
                fn = act if callable(act) else (lambda cc=act: self._shell_log(cc, self.sec_out))
                self._btn(c, lbl, fn, j+1, 0, col)

        # Package cible pour permissions
        pc = self._card(p, 2, 0, "🔍 ANALYSE PERMISSIONS", cspan=2)
        pc.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(pc, text="Package:",
            font=ctk.CTkFont(size=10), text_color=C["dim"]
        ).grid(row=1, column=0, padx=14, pady=8)

        self.sec_pkg_entry = ctk.CTkEntry(pc,
            placeholder_text="com.example.app",
            fg_color=C["bg"], border_color=C["border"],
            font=ctk.CTkFont(family="Courier New", size=11), height=34)
        self.sec_pkg_entry.grid(row=1, column=1, padx=4, pady=8, sticky="ew")
        self._btn(pc, "🔍 Analyser",     self._sec_analyze_pkg, 1, 2, C["blue"])
        self._btn(pc, "🚫 Révoquer Loc", self._sec_revoke_loc,  1, 3, C["red"])

        # Audit rapide
        audit_c = self._card(p, 3, 0, "🔬 AUDIT RAPIDE", cspan=2)
        audit_c.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        audits = [
            ("🌐 Ports Ouverts",       "netstat -tulnp",                                C["cyan"]),
            ("👁️ Apps avec GPS",       "dumpsys package | grep ACCESS_FINE_LOCATION",   C["yellow"]),
            ("📡 Services Actifs",     "dumpsys activity services | head -30",           C["blue"]),
            ("🔑 Certificats CA",      "security list-ca-certs | head -20",             C["purple"]),
            ("📋 Admins Appareils",    "dumpsys device_policy | grep -A2 admin",        C["orange"]),
        ]
        for i, (lbl, cmd, col) in enumerate(audits):
            self._btn(audit_c, lbl, lambda cc=cmd: self._shell_log(cc, self.sec_out),
                      1, i, col)

    def _sec_analyze_pkg(self):
        pkg = self.sec_pkg_entry.get().strip()
        if not pkg:
            return
        def _run():
            r = self.adb.shell(f"dumpsys package {pkg}")
            if r and r.stdout:
                lines = [l for l in r.stdout.split("\n")
                         if "permission" in l.lower() or "granted" in l.lower()]
                self._log(self.sec_out,
                    f"Permissions {pkg}:\n" + "\n".join(lines[:50]))
        self._thread(_run)

    def _sec_revoke_loc(self):
        pkg = self.sec_pkg_entry.get().strip()
        if pkg:
            self._shell_log(
                f"pm revoke {pkg} android.permission.ACCESS_FINE_LOCATION",
                self.sec_out)

    # =========================================================================
    #  PAGE: DÉVELOPPEUR
    # =========================================================================
    def _pg_developer(self):
        p = self._make_page("developer", "OPTIONS DÉVELOPPEUR", "⚙️")
        p.grid_columnconfigure((0, 1, 2), weight=1)

        out_f = ctk.CTkFrame(p, fg_color=C["panel"], corner_radius=10)
        out_f.grid(row=4, column=0, columnspan=3, padx=8, pady=8, sticky="ew")
        out_f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(out_f, text="📤  SORTIE DÉVELOPPEUR",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["dim"]
        ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")
        self.dev_out = self._textbox(out_f, 100)
        self.dev_out.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        groups = [
            ("🐛 USB DEBUGGING", [
                ("✅ USB Debug ON",          "settings put global adb_enabled 1",                     C["green"]),
                ("❌ USB Debug OFF",         "settings put global adb_enabled 0",                     C["red"]),
                ("☕ Stay Awake ON",         "settings put global stay_on_while_plugged_in 3",        C["blue"]),
                ("☕ Stay Awake OFF",        "settings put global stay_on_while_plugged_in 0",        C["yellow"]),
                ("⚡ Dev Settings ON",       "settings put global development_settings_enabled 1",    C["purple"]),
                ("🔍 Mock Location ON",      "settings put secure mock_location 1",                   C["orange"]),
            ]),
            ("🎨 ANIMATIONS UI", [
                ("⚡ Animations ZERO",       "settings put global window_animation_scale 0 ; "
                                            "settings put global transition_animation_scale 0 ; "
                                            "settings put global animator_duration_scale 0",          C["green"]),
                ("0.5x  Animations",         "settings put global window_animation_scale 0.5",       C["blue"]),
                ("1x    Animations",         "settings put global window_animation_scale 1",         C["yellow"]),
                ("2x    Animations",         "settings put global window_animation_scale 2",         C["red"]),
                ("GPU Rendering",            "settings put global debug.hwui.renderer skiavk",       C["purple"]),
                ("4x MSAA ON",               "settings put global debug.egl.force_msaa 1",           C["cyan"]),
            ]),
            ("📸 CAPTURE & ENREGISTREMENT", [
                ("📸 Screenshot",            None,                                                     C["blue"]),
                ("🎥 Record 30s",            "screenrecord --time-limit 30 /sdcard/rec_adb.mp4",     C["purple"]),
                ("📥 Pull Screenshot",        None,                                                     C["green"]),
                ("📥 Pull Recording",         None,                                                     C["green"]),
                ("🐛 Bug Report",            "bugreport /sdcard/bugreport.zip",                       C["orange"]),
                ("📊 GPU Profiling ON",      "setprop debug.hwui.profile true",                      C["yellow"]),
            ]),
        ]
        for gi, (gtitle, actions) in enumerate(groups):
            c = self._card(p, 1, gi, gtitle)
            c.grid_columnconfigure(0, weight=1)
            for j, (lbl, cmd, col) in enumerate(actions):
                if cmd:
                    fn = lambda cc=cmd: self._shell_log(cc, self.dev_out)
                elif lbl == "📸 Screenshot":
                    fn = self._quick_screenshot
                elif lbl == "📥 Pull Screenshot":
                    fn = lambda: self._thread(
                        lambda: self.adb.run("pull /sdcard/_adb_ss.png ./screenshot_adb.png"))
                elif lbl == "📥 Pull Recording":
                    fn = lambda: self._thread(
                        lambda: self.adb.run("pull /sdcard/rec_adb.mp4 ./recording_adb.mp4"))
                else:
                    fn = lambda: None
                self._btn(c, lbl, fn, j+1, 0, col)

        # ── Logcat ───────────────────────────────────────────────────────
        lc_f = ctk.CTkFrame(p, fg_color=C["panel"], corner_radius=10)
        lc_f.grid(row=2, column=0, columnspan=3, padx=8, pady=6, sticky="ew")
        lc_f.grid_columnconfigure(0, weight=1)

        lc_hdr = ctk.CTkFrame(lc_f, fg_color="transparent")
        lc_hdr.grid(row=0, column=0, sticky="ew", padx=14)
        lc_hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(lc_hdr, text="📋  LOGCAT EN TEMPS RÉEL",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["dim"]
        ).grid(row=0, column=0, pady=(10, 4), sticky="w")

        lc_tag_f = ctk.CTkFrame(lc_hdr, fg_color="transparent")
        lc_tag_f.grid(row=0, column=1, pady=(10, 4), sticky="e")

        ctk.CTkLabel(lc_tag_f, text="Niveau:",
            font=ctk.CTkFont(size=10), text_color=C["dim"]
        ).grid(row=0, column=0, padx=4)

        self.logcat_level = ctk.CTkOptionMenu(
            lc_tag_f, values=["*:V", "*:D", "*:I", "*:W", "*:E"], width=80)
        self.logcat_level.set("*:W")
        self.logcat_level.grid(row=0, column=1, padx=4)

        for i, (lbl, fn, col) in enumerate([
            ("▶ Démarrer", self._logcat_start, C["green"]),
            ("⏹ Stopper",  self._logcat_stop,  C["red"]),
            ("🗑️ Effacer", lambda: self._clear_tb(self.logcat_box), C["yellow"]),
        ]):
            ctk.CTkButton(lc_tag_f, text=lbl, command=fn, width=100,
                fg_color=col, hover_color=self._darken(col),
                font=ctk.CTkFont(size=10)
            ).grid(row=0, column=2+i, padx=3)

        self.logcat_box = self._textbox(lc_f, 190)
        self.logcat_box.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # ── Propriétés système avancées ───────────────────────────────────
        adv_c = self._card(p, 3, 0, "🔧 SETPROP AVANCÉ", cspan=3)
        adv_c.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(adv_c, text="Propriété:",
            font=ctk.CTkFont(size=10), text_color=C["dim"]
        ).grid(row=1, column=0, padx=14, pady=8)
        self.setprop_key = ctk.CTkEntry(adv_c, placeholder_text="debug.hwui.profile",
            fg_color=C["bg"], border_color=C["border"],
            font=ctk.CTkFont(family="Courier New", size=11), height=34, width=200)
        self.setprop_key.grid(row=1, column=1, padx=4, pady=8, sticky="ew")
        self.setprop_val = ctk.CTkEntry(adv_c, placeholder_text="true",
            fg_color=C["bg"], border_color=C["border"],
            font=ctk.CTkFont(family="Courier New", size=11), height=34, width=100)
        self.setprop_val.grid(row=1, column=2, padx=4, pady=8)
        self._btn(adv_c, "setprop", self._do_setprop, 1, 3, C["orange"])
        self._btn(adv_c, "getprop", self._do_getprop, 1, 4, C["blue"])

    def _logcat_start(self):
        self.logcat_running = True
        level = self.logcat_level.get()
        def _run():
            proc = subprocess.Popen(
                ["adb", "logcat", "-v", "brief", level],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, bufsize=1
            )
            while self.logcat_running:
                line = proc.stdout.readline()
                if line:
                    self._log(self.logcat_box, line.rstrip())
            proc.terminate()
        self._thread(_run)

    def _logcat_stop(self):
        self.logcat_running = False

    def _do_setprop(self):
        key = self.setprop_key.get().strip()
        val = self.setprop_val.get().strip()
        if key and val:
            self._shell_log(f"setprop {key} {val}", self.dev_out)

    def _do_getprop(self):
        key = self.setprop_key.get().strip()
        if key:
            self._shell_log(f"getprop {key}", self.dev_out)

    # =========================================================================
    #  PAGE: DONNÉES
    # =========================================================================
    def _pg_data(self):
        p = self._make_page("data", "DONNÉES & STOCKAGE", "💾")
        p.grid_columnconfigure((0, 1), weight=1)

        out_f = ctk.CTkFrame(p, fg_color=C["panel"], corner_radius=10)
        out_f.grid(row=3, column=0, columnspan=2, padx=8, pady=8, sticky="ew")
        out_f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(out_f, text="📤  SORTIE DONNÉES",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["dim"]
        ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")
        self.data_out = self._textbox(out_f, 160)
        self.data_out.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # ── Transfert fichiers ─────────────────────────────────────────────
        ft = self._card(p, 1, 0, "📁 TRANSFERT FICHIERS PC ↔ TÉLÉPHONE")
        ft.grid_columnconfigure(0, weight=1)

        for label, attr, placeholder in [
            ("📱 Chemin sur Téléphone:", "remote_path_e", "/sdcard/fichier.txt"),
            ("💻 Chemin Local PC:",      "local_path_e",  "./"),
        ]:
            ctk.CTkLabel(ft, text=label, font=ctk.CTkFont(size=10), text_color=C["dim"]
            ).grid(padx=14, pady=(8, 2), sticky="w")
            entry = ctk.CTkEntry(ft, placeholder_text=placeholder,
                fg_color=C["bg"], border_color=C["border"],
                font=ctk.CTkFont(family="Courier New", size=11), height=34)
            entry.grid(padx=10, pady=2, sticky="ew")
            setattr(self, attr, entry)

        self._btn(ft, "📂 Parcourir (PC)",   self._browse_local, 5, 0, C["purple"])
        self._btn(ft, "📥  PULL  (Tél → PC)", self._pull_file,    6, 0, C["blue"],  height=40)
        self._btn(ft, "📤  PUSH  (PC → Tél)", self._push_file,    7, 0, C["green"], height=40)

        # ── Stockage ──────────────────────────────────────────────────────
        si = self._card(p, 1, 1, "💾 STOCKAGE & EXPLORATEUR")
        si.grid_columnconfigure(0, weight=1)
        stor = [
            ("📊 Espace /data",           "df /data",                                    C["blue"]),
            ("📊 Espace /sdcard",         "df /sdcard",                                  C["blue"]),
            ("📁 Contenu /sdcard/",       "ls -la /sdcard/",                             C["green"]),
            ("📸 Photos DCIM",            "ls -la /sdcard/DCIM/Camera/ | tail -20",     C["cyan"]),
            ("📥 Downloads",              "ls -la /sdcard/Download/",                   C["yellow"]),
            ("📋 DiskStats Détaillés",    "dumpsys diskstats",                           C["purple"]),
            ("🧹 Vider Cache Système",    "pm trim-caches 999g",                        C["orange"]),
            ("📇 Exporter Contacts",      "content query --uri content://contacts/phones", C["green"]),
        ]
        for i, (lbl, cmd, col) in enumerate(stor):
            self._btn(si, lbl, lambda cc=cmd: self._shell_log(cc, self.data_out),
                      i+1, 0, col)

        # ── Explorateur de chemin ──────────────────────────────────────────
        exp = self._card(p, 2, 0, "🗂️ EXPLORATEUR DE CHEMIN", cspan=2)
        exp.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(exp, text="Chemin:",
            font=ctk.CTkFont(size=10), text_color=C["dim"]
        ).grid(row=1, column=0, padx=14, pady=8)
        self.explorer_entry = ctk.CTkEntry(exp,
            placeholder_text="/sdcard/",
            fg_color=C["bg"], border_color=C["border"],
            font=ctk.CTkFont(family="Courier New", size=11), height=34)
        self.explorer_entry.grid(row=1, column=1, padx=4, pady=8, sticky="ew")
        self._btn(exp, "📁 Lister",    self._explore_path,   1, 2, C["blue"])
        self._btn(exp, "🗑️ Supprimer", self._delete_remote,  1, 3, C["red"])

    def _pull_file(self):
        remote = self.remote_path_e.get().strip()
        local  = self.local_path_e.get().strip() or "."
        if remote:
            def _run():
                r = self.adb.run(f'pull "{remote}" "{local}"')
                self._log(self.data_out,
                    f"PULL {remote} → {local}\n{r.stdout.strip() if r else 'Erreur'}")
            self._thread(_run)

    def _push_file(self):
        local  = self.local_path_e.get().strip()
        remote = self.remote_path_e.get().strip() or "/sdcard/"
        if local:
            def _run():
                r = self.adb.run(f'push "{local}" "{remote}"')
                self._log(self.data_out,
                    f"PUSH {local} → {remote}\n{r.stdout.strip() if r else 'Erreur'}")
            self._thread(_run)

    def _browse_local(self):
        path = filedialog.askopenfilename()
        if path:
            self.local_path_e.delete(0, "end")
            self.local_path_e.insert(0, path)

    def _explore_path(self):
        path = self.explorer_entry.get().strip() or "/sdcard/"
        self._shell_log(f"ls -la {path}", self.data_out)

    def _delete_remote(self):
        path = self.explorer_entry.get().strip()
        if path:
            self._shell_log(f"rm -rf {path}", self.data_out)

    # =========================================================================
    #  PAGE: PERSONNALISATION
    # =========================================================================
    def _pg_custom(self):
        p = self._make_page("custom", "PERSONNALISATION", "🎨")
        p.grid_columnconfigure((0, 1, 2), weight=1)

        out_f = ctk.CTkFrame(p, fg_color=C["panel"], corner_radius=10)
        out_f.grid(row=4, column=0, columnspan=3, padx=8, pady=8, sticky="ew")
        out_f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(out_f, text="📤  SORTIE",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["dim"]
        ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")
        self.cust_out = self._textbox(out_f, 90)
        self.cust_out.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        groups = [
            ("🌙 THÈME & APPARENCE", [
                ("🌙 Mode Sombre",         "settings put secure ui_night_mode 2",         C["purple"]),
                ("☀️ Mode Clair",          "settings put secure ui_night_mode 1",         C["yellow"]),
                ("🔄 Mode Auto",           "settings put secure ui_night_mode 0",         C["blue"]),
                ("🎨 Fond d'Écran",        "am start -a android.intent.action.SET_WALLPAPER", C["blue"]),
                ("🖥️ Paramètres Affichage","am start -a android.settings.DISPLAY_SETTINGS", C["blue"]),
                ("🌈 Paramètres Couleurs", "am start -a android.settings.DISPLAY_SETTINGS", C["purple"]),
            ]),
            ("🔤 TEXTE & TAILLE", [
                ("🔡 Texte Petit (0.85)",  "settings put system font_scale 0.85",        C["red"]),
                ("🔤 Texte Normal (1.0)",  "settings put system font_scale 1.0",         C["green"]),
                ("🔠 Texte Grand (1.15)",  "settings put system font_scale 1.15",        C["blue"]),
                ("🔠 Texte Plus Grand (1.3)","settings put system font_scale 1.3",       C["yellow"]),
                ("🔠 Texte Max (1.6)",     "settings put system font_scale 1.6",         C["orange"]),
                ("📐 Densité Actuelle",    "wm density",                                  C["dim"]),
            ]),
            ("🎮 INTERFACE AVANCÉE", [
                ("⬛ Plein Écran ON",      "settings put global policy_control immersive.full=*", C["purple"]),
                ("🔲 Plein Écran OFF",     "settings put global policy_control null",            C["blue"]),
                ("🎮 Mode Jeu ON",         "settings put global game_driver_all_apps 1",         C["green"]),
                ("🎮 Mode Jeu OFF",        "settings put global game_driver_all_apps 0",         C["red"]),
                ("🌐 Langue",             "am start -a android.settings.LOCALE_SETTINGS",       C["blue"]),
                ("🔔 Sons",               "am start -a android.settings.SOUND_SETTINGS",        C["blue"]),
            ]),
        ]
        for gi, (gtitle, actions) in enumerate(groups):
            c = self._card(p, 1, gi, gtitle)
            c.grid_columnconfigure(0, weight=1)
            for j, (lbl, cmd, col) in enumerate(actions):
                self._btn(c, lbl, lambda cc=cmd: self._shell_log(cc, self.cust_out),
                          j+1, 0, col)

        # ── Presets rapides ───────────────────────────────────────────────
        pc = ctk.CTkFrame(p, fg_color=C["panel"], corner_radius=10)
        pc.grid(row=2, column=0, columnspan=3, padx=8, pady=6, sticky="ew")
        pc.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        ctk.CTkLabel(pc, text="⚡  PRESETS RAPIDES",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["dim"]
        ).grid(row=0, column=0, columnspan=6, padx=14, pady=(10, 4), sticky="w")

        presets = [
            ("🌙 Night Mode", C["purple"], [
                "settings put secure ui_night_mode 2",
                "settings put system screen_brightness 50",
                "settings put system mode_ringer 1",
            ]),
            ("☀️ Day Mode", C["yellow"], [
                "settings put secure ui_night_mode 1",
                "settings put system screen_brightness 200",
                "settings put system accelerometer_rotation 1",
            ]),
            ("🎮 Gaming Mode", C["green"], [
                "settings put global game_driver_all_apps 1",
                "settings put system peak_refresh_rate 120",
                "settings put global window_animation_scale 0",
                "settings put global transition_animation_scale 0",
                "settings put global animator_duration_scale 0",
            ]),
            ("📸 Photo Mode", C["blue"], [
                "settings put system screen_brightness 255",
                "settings put system accelerometer_rotation 0",
                "settings put system mode_ringer 0",
            ]),
            ("🔋 Eco Mode", C["orange"], [
                "settings put global low_power 1",
                "settings put system screen_brightness 80",
                "settings put secure ui_night_mode 2",
                "settings put global window_animation_scale 0.5",
            ]),
            ("🕵️ Privacy Mode", C["red"], [
                "settings put secure location_mode 0",
                "svc wifi disable",
                "svc data disable",
                f"am force-stop {GPS_PKG}",
            ]),
        ]
        for i, (lbl, col, cmds) in enumerate(presets):
            def make_fn(cc_list, name):
                def fn():
                    def _run():
                        for cc in cc_list:
                            self.adb.shell(cc)
                            time.sleep(0.2)
                        self._log(self.cust_out, f"✅ Preset '{name}' appliqué")
                    self._thread(_run)
                return fn
            ctk.CTkButton(pc, text=lbl, command=make_fn(cmds, lbl),
                fg_color=col, hover_color=self._darken(col),
                font=ctk.CTkFont(size=11), height=46, corner_radius=8
            ).grid(row=1, column=i, padx=6, pady=(4, 14), sticky="ew")

        # ── Réglages custom densité ─────────────────────────────────────
        dens_c = self._card(p, 3, 0, "📐 DENSITÉ PERSONNALISÉE", cspan=3)
        dens_c.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(dens_c, text="DPI:",
            font=ctk.CTkFont(size=10), text_color=C["dim"]
        ).grid(row=1, column=0, padx=14, pady=8)
        self.dpi_entry = ctk.CTkEntry(dens_c, placeholder_text="420",
            fg_color=C["bg"], border_color=C["border"],
            font=ctk.CTkFont(family="Courier New", size=11), height=34)
        self.dpi_entry.grid(row=1, column=1, padx=4, pady=8, sticky="ew")
        self._btn(dens_c, "✅ Appliquer DPI", self._apply_dpi,  1, 2, C["green"])
        self._btn(dens_c, "🔄 Reset DPI",     self._reset_dpi,  1, 3, C["yellow"])

    def _apply_dpi(self):
        dpi = self.dpi_entry.get().strip()
        if dpi and dpi.isdigit():
            self._shell_log(f"wm density {dpi}", self.cust_out)

    def _reset_dpi(self):
        self._shell_log("wm density reset", self.cust_out)

    # =========================================================================
    #  PAGE: AUTOMATISATION
    # =========================================================================
    def _pg_automation(self):
        p = self._make_page("automation", "AUTOMATISATION & SCRIPTS", "🔄")
        p.grid_columnconfigure((0, 1), weight=1)

        out_f = ctk.CTkFrame(p, fg_color=C["panel"], corner_radius=10)
        out_f.grid(row=3, column=0, columnspan=2, padx=8, pady=8, sticky="ew")
        out_f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(out_f, text="📤  SORTIE AUTOMATISATION",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["dim"]
        ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")
        self.auto_out = self._textbox(out_f, 150)
        self.auto_out.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # ── Scripts prédéfinis ────────────────────────────────────────────
        sc = self._card(p, 1, 0, "🚀 SCRIPTS PRÉDÉFINIS")
        sc.grid_columnconfigure(0, weight=1)
        scripts = [
            ("🧹 Nettoyage Complet",       self._sc_cleanup,   C["green"]),
            ("🎮 Optimisation Gaming",      self._sc_gaming,    C["purple"]),
            ("🔋 Économie Batterie",        self._sc_battery,   C["yellow"]),
            ("🕵️ Confidentialité Maximum",  self._sc_privacy,   C["red"]),
            ("⚡ Boost Performances",       self._sc_boost,     C["blue"]),
            ("📸 Mode Photo/Vidéo",         self._sc_photo,     C["orange"]),
            ("🌐 Reset Réseau Complet",     self._sc_netreset,  C["cyan"]),
            ("🔓 Déverrouiller Développeur",self._sc_devmode,   C["yellow"]),
        ]
        for i, (lbl, fn, col) in enumerate(scripts):
            self._btn(sc, lbl, fn, i+1, 0, col, height=42)

        # ── Macro Builder ─────────────────────────────────────────────────
        mc = self._card(p, 1, 1, "⚡ MACRO BUILDER")
        mc.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(mc, text="Commande rapide (Enter pour exécuter):",
            font=ctk.CTkFont(size=10), text_color=C["dim"]
        ).grid(row=1, column=0, padx=14, pady=(8, 2), sticky="w")

        self.quick_cmd_entry = ctk.CTkEntry(mc,
            placeholder_text="shell <cmd>  ou  <adb cmd>",
            fg_color=C["bg"], border_color=C["border"],
            font=ctk.CTkFont(family="Courier New", size=11), height=34)
        self.quick_cmd_entry.grid(row=2, column=0, padx=10, pady=4, sticky="ew")
        self.quick_cmd_entry.bind("<Return>", lambda e: self._run_quick_cmd())
        self._btn(mc, "▶ Exécuter", self._run_quick_cmd, 3, 0, C["green"], height=36)

        ctk.CTkLabel(mc,
            text="Séquence de commandes (1 commande ADB shell par ligne):\n"
                 "# Les lignes commençant par # sont des commentaires",
            font=ctk.CTkFont(size=10), text_color=C["dim"]
        ).grid(row=4, column=0, padx=14, pady=(12, 2), sticky="w")

        self.macro_box = ctk.CTkTextbox(mc, fg_color=C["bg"],
            text_color=C["text"],
            font=ctk.CTkFont(family="Courier New", size=10), height=170)
        self.macro_box.grid(row=5, column=0, padx=10, pady=4, sticky="ew")
        self.macro_box.insert("1.0",
            "# Exemple de séquence\n"
            "pm trim-caches 999g\n"
            "settings put global window_animation_scale 0.5\n"
        )

        self._btn(mc, "▶▶ Exécuter Séquence Complète",
                  self._run_macro, 6, 0, C["purple"], height=40)

        btns_row = ctk.CTkFrame(mc, fg_color="transparent")
        btns_row.grid(row=7, column=0, padx=10, pady=(0, 12), sticky="ew")
        btns_row.grid_columnconfigure((0, 1, 2), weight=1)
        self._btn(btns_row, "💾 Sauvegarder", self._save_macro, 0, 0, C["blue"])
        self._btn(btns_row, "📂 Charger",     self._load_macro, 0, 1, C["yellow"])
        self._btn(btns_row, "🗑️ Effacer",     self._clear_macro, 0, 2, C["red"])

        # ── Barre de progression ──────────────────────────────────────────
        self.auto_progress = ctk.CTkProgressBar(p, progress_color=C["green"], height=10)
        self.auto_progress.grid(row=2, column=0, columnspan=2,
                                padx=8, pady=(0, 4), sticky="ew")
        self.auto_progress.set(0)

        self.auto_status_lbl = ctk.CTkLabel(p, text="",
            font=ctk.CTkFont(family="Courier New", size=10),
            text_color=C["dim"])
        self.auto_status_lbl.grid(row=2, column=0, columnspan=2,
                                   padx=18, pady=0, sticky="w")

    def _run_quick_cmd(self):
        cmd = self.quick_cmd_entry.get().strip()
        if not cmd:
            return
        if cmd.startswith("shell "):
            self._shell_log(cmd[6:], self.auto_out)
        else:
            def _run():
                r = self.adb.run(cmd)
                self._log(self.auto_out,
                    f"adb {cmd}\n{r.stdout.strip() if r else 'Erreur'}")
            self._thread(_run)

    def _run_macro(self):
        cmds = [l.strip() for l in self.macro_box.get("1.0", "end").strip().split("\n")
                if l.strip() and not l.strip().startswith("#")]
        if not cmds:
            return
        def _run():
            for i, cmd in enumerate(cmds):
                self.auto_status_lbl.configure(text=f"  ▶ {cmd[:60]}...")
                self.auto_progress.set((i + 1) / len(cmds))
                self.adb.shell(cmd)
                self._log(self.auto_out, f"✓ {cmd}")
                time.sleep(0.3)
            self.auto_progress.set(0)
            self.auto_status_lbl.configure(text="  ✅ Séquence terminée")
            self._log(self.auto_out, f"✅ {len(cmds)} commandes exécutées")
        self._thread(_run)

    def _save_macro(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texte", "*.txt"), ("Tous", "*.*")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.macro_box.get("1.0", "end"))
            self._log(self.auto_out, f"💾 Macro sauvegardée → {path}")

    def _load_macro(self):
        path = filedialog.askopenfilename(
            filetypes=[("Texte", "*.txt"), ("Tous", "*.*")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.macro_box.delete("1.0", "end")
                self.macro_box.insert("1.0", f.read())

    def _clear_macro(self):
        self.macro_box.delete("1.0", "end")

    def _run_script(self, name: str, cmds: list):
        def _run():
            self._log(self.auto_out, f"{'═'*42}\n▶▶ SCRIPT: {name}")
            for i, cmd in enumerate(cmds):
                self.auto_status_lbl.configure(text=f"  ▶ {cmd[:60]}")
                self.auto_progress.set((i + 1) / len(cmds))
                r = self.adb.shell(cmd)
                out = r.stdout.strip()[:50] if r and r.stdout.strip() else ""
                self._log(self.auto_out, f"  ✓ {cmd}  {out}")
                time.sleep(0.4)
            self.auto_progress.set(0)
            self.auto_status_lbl.configure(text=f"  ✅ '{name}' terminé")
            self._log(self.auto_out, f"✅ Script '{name}' terminé!")
            self.adb.log(f"Script: {name}")
        self._thread(_run)

    def _sc_cleanup(self):
        self._run_script("Nettoyage Complet", [
            "pm trim-caches 999g",
            "rm -rf /sdcard/.thumbnails",
            "rm -rf /sdcard/Download/*.tmp 2>/dev/null",
            "am kill-all",
            "sync",
        ])

    def _sc_gaming(self):
        self._run_script("Optimisation Gaming", [
            "settings put global game_driver_all_apps 1",
            "settings put system peak_refresh_rate 120",
            "settings put global window_animation_scale 0",
            "settings put global transition_animation_scale 0",
            "settings put global animator_duration_scale 0",
            "settings put global always_finish_activities 0",
        ])

    def _sc_battery(self):
        self._run_script("Économie Batterie", [
            "settings put global low_power 1",
            "settings put global wifi_sleep_policy 2",
            "settings put global sync_disabled 1",
            "settings put system screen_brightness 80",
            "settings put secure ui_night_mode 2",
        ])

    def _sc_privacy(self):
        self._run_script("Confidentialité Maximale", [
            "settings put secure location_mode 0",
            "svc wifi disable",
            "svc data disable",
            f"am force-stop {GPS_PKG}",
            "settings put global bluetooth_on 0",
        ])

    def _sc_boost(self):
        self._run_script("Boost Performances", [
            "settings put global window_animation_scale 0.5",
            "settings put global transition_animation_scale 0.5",
            "settings put global animator_duration_scale 0.5",
            "am kill-all",
            "pm trim-caches 999g",
        ])

    def _sc_photo(self):
        self._run_script("Mode Photo/Vidéo", [
            "settings put system screen_brightness 255",
            "settings put system accelerometer_rotation 0",
            "settings put system mode_ringer 0",
            "settings put secure ui_night_mode 1",
        ])

    def _sc_netreset(self):
        self._run_script("Reset Réseau", [
            "svc wifi disable",
            "svc data disable",
            "settings put global airplane_mode_on 1",
            "settings put global airplane_mode_on 0",
            "svc wifi enable",
            "svc data enable",
        ])

    def _sc_devmode(self):
        self._run_script("Mode Développeur", [
            "settings put global development_settings_enabled 1",
            "settings put global adb_enabled 1",
            "settings put global stay_on_while_plugged_in 3",
            "settings put global window_animation_scale 0.5",
        ])

    # =========================================================================
    #  PAGE: MONITEUR (MATPLOTLIB)
    # =========================================================================
    def _pg_monitor(self):
        p = self._make_page("monitor", "MONITEUR EN TEMPS RÉEL", "📊")
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        p.grid_rowconfigure(2, weight=1)

        # ── 4 cartes stats live ───────────────────────────────────────────
        self._mon_lbls: dict = {}
        for i, (key, title, col) in enumerate([
            ("batt",   "🔋 Batterie",   C["green"]),
            ("temp",   "🌡️  Temp CPU",  C["yellow"]),
            ("status", "⚡ Statut",     C["blue"]),
            ("uptime", "⏱️  Uptime",    C["purple"]),
        ]):
            sc = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=10)
            sc.grid(row=1, column=i, padx=8, pady=6, sticky="nsew")
            ctk.CTkLabel(sc, text=title,
                font=ctk.CTkFont(size=10), text_color=C["dim"]
            ).grid(row=0, column=0, padx=12, pady=(8, 2))
            lbl = ctk.CTkLabel(sc, text="---",
                font=ctk.CTkFont(family="Courier New", size=24, weight="bold"),
                text_color=col)
            lbl.grid(row=1, column=0, padx=12, pady=(2, 10))
            self._mon_lbls[key] = lbl

        # ── Graphique Matplotlib ──────────────────────────────────────────
        chart_c = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=10)
        chart_c.grid(row=2, column=0, columnspan=4, padx=8, pady=6, sticky="nsew")
        chart_c.grid_columnconfigure(0, weight=1)
        chart_c.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(chart_c,
            text="📈   HISTORIQUE BATTERIE — TEMPS RÉEL",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["dim"]
        ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")

        # Figure Matplotlib
        self._fig = Figure(figsize=(9, 3.4), dpi=96, facecolor="#161b22")
        self._ax  = self._fig.add_subplot(111)
        self._ax.set_facecolor("#0d1117")
        self._ax.tick_params(colors="#7d8590", labelsize=8)
        for spine in self._ax.spines.values():
            spine.set_edgecolor("#30363d")
        self._ax.set_xlabel("Temps (s)", color="#7d8590", fontsize=8)
        self._ax.set_ylabel("Batterie (%)", color="#7d8590", fontsize=8)
        self._ax.set_ylim(0, 105)
        self._ax.set_xlim(0, 60)
        self._ax.grid(True, color="#30363d", alpha=0.5)
        self._ax.axhline(y=20, color=C["red"],    linestyle="--", alpha=0.5, lw=1, label="Critique 20%")
        self._ax.axhline(y=50, color=C["yellow"], linestyle="--", alpha=0.4, lw=1, label="Normal 50%")
        self._ax.legend(loc="upper right",
                        facecolor="#161b22", edgecolor="#30363d",
                        labelcolor="#7d8590", fontsize=8)
        self._line, = self._ax.plot([], [], color=C["green"], linewidth=2,
                                    marker="o", markersize=3, label="Batterie")
        self._fill = None
        self._fig.tight_layout(pad=1.5)

        self._canvas = FigureCanvasTkAgg(self._fig, master=chart_c)
        self._canvas.get_tk_widget().configure(bg="#161b22", highlightthickness=0)
        self._canvas.get_tk_widget().grid(row=1, column=0, padx=8, pady=(0, 8), sticky="nsew")

        # ── Contrôles moniteur ────────────────────────────────────────────
        ctrl = ctk.CTkFrame(p, fg_color="transparent")
        ctrl.grid(row=3, column=0, columnspan=4, padx=8, pady=(0, 8), sticky="ew")
        ctrl.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        for i, (lbl, fn, col) in enumerate([
            ("▶ Démarrer",  self._start_monitor, C["green"]),
            ("⏹ Arrêter",   self._stop_monitor,  C["red"]),
            ("🗑️ Effacer",  self._clear_monitor, C["yellow"]),
            ("📊 Exporter CSV", self._export_data, C["blue"]),
        ]):
            ctk.CTkButton(ctrl, text=lbl, command=fn,
                fg_color=col, hover_color=self._darken(col),
                font=ctk.CTkFont(weight="bold"), height=38
            ).grid(row=0, column=i, padx=6, sticky="ew")

        ctk.CTkLabel(ctrl, text="Intervalle:",
            font=ctk.CTkFont(size=10), text_color=C["dim"]
        ).grid(row=0, column=4, padx=(16, 4))

        self.interval_var = ctk.StringVar(value="30s")
        ctk.CTkOptionMenu(ctrl,
            values=["5s", "10s", "30s", "60s", "2min"],
            variable=self.interval_var, width=90
        ).grid(row=0, column=5, padx=4)

    def _start_monitor(self):
        if self.monitor_running:
            return
        self.monitor_running = True
        self._monitor_t0 = time.time()
        self._thread(self._monitor_loop)

    def _stop_monitor(self):
        self.monitor_running = False

    def _clear_monitor(self):
        self._time_pts.clear()
        self._batt_pts.clear()
        self._line.set_data([], [])
        self._ax.set_xlim(0, 60)
        if self._fill:
            try:
                self._fill.remove()
            except Exception:
                pass
            self._fill = None
        self._canvas.draw()

    def _export_data(self):
        if not self._batt_pts:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write("time_s,battery_pct\n")
                for t, b in zip(self._time_pts, self._batt_pts):
                    f.write(f"{t:.1f},{b}\n")

    def _monitor_loop(self):
        interval_map = {"5s": 5, "10s": 10, "30s": 30, "60s": 60, "2min": 120}
        while self.monitor_running:
            try:
                batt   = self.adb.battery_level()
                temp   = self.adb.battery_temp()
                status = self.adb.battery_status()
                elapsed = time.time() - self._monitor_t0

                if batt is not None:
                    self._batt_pts.append(batt)
                    self._time_pts.append(elapsed)
                    col = C["green"] if batt > 50 else (C["yellow"] if batt > 20 else C["red"])
                    self._mon_lbls["batt"].configure(text=f"{batt}%", text_color=col)

                    # Mise à jour graphique
                    self._line.set_data(self._time_pts, self._batt_pts)
                    self._line.set_color(col)
                    if self._fill:
                        try:
                            self._fill.remove()
                        except Exception:
                            pass
                    self._fill = self._ax.fill_between(
                        self._time_pts, self._batt_pts, alpha=0.12, color=col)
                    xmax = max(self._time_pts) + 20 if self._time_pts else 60
                    self._ax.set_xlim(0, xmax)
                    self._canvas.draw()

                if temp is not None:
                    col_t = C["green"] if temp < 40 else (C["yellow"] if temp < 50 else C["red"])
                    self._mon_lbls["temp"].configure(text=f"{temp}°C", text_color=col_t)

                if status:
                    self._mon_lbls["status"].configure(text=status)

                r = self.adb.shell("cat /proc/uptime")
                if r and r.stdout:
                    try:
                        secs = int(float(r.stdout.split()[0]))
                        h, rem = divmod(secs, 3600)
                        m = rem // 60
                        self._mon_lbls["uptime"].configure(text=f"{h}h{m:02d}m")
                    except Exception:
                        pass

            except Exception:
                pass

            interval = interval_map.get(self.interval_var.get(), 30)
            time.sleep(interval)

    # =========================================================================
    #  PAGE: TERMINAL ADB
    # =========================================================================
    def _pg_terminal(self):
        p = self._make_page("terminal", "TERMINAL ADB", "⚡")
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(1, weight=1)

        # ── Écran terminal ────────────────────────────────────────────────
        tc = ctk.CTkFrame(p, fg_color="#000000", corner_radius=8,
                          border_width=1, border_color=C["green"])
        tc.grid(row=1, column=0, padx=12, pady=(0, 4), sticky="nsew")
        tc.grid_columnconfigure(0, weight=1)
        tc.grid_rowconfigure(0, weight=1)

        self.term_box = ctk.CTkTextbox(tc,
            fg_color="#000000",
            text_color=C["terminal"],
            font=ctk.CTkFont(family="Courier New", size=12),
            state="disabled", wrap="word")
        self.term_box.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        # Message de bienvenue
        welcome = (
            "╔══════════════════════════════════════════════════════════╗\n"
            "║         ADB MASTER CONTROL  v2.0 ELITE                  ║\n"
            "║         ML | github.com/exploit4040                     ║\n"
            "╠══════════════════════════════════════════════════════════╣\n"
            "║  COMMANDES DISPONIBLES:                                  ║\n"
            "║  shell <cmd>        →  commande sur l'appareil           ║\n"
            "║  <adb cmd>          →  commande ADB directe              ║\n"
            "║  help               →  afficher l'aide                   ║\n"
            "║  clear  /  cls      →  effacer le terminal               ║\n"
            "║  Flèches ↑↓         →  naviguer dans l'historique        ║\n"
            "╚══════════════════════════════════════════════════════════╝\n"
            "\nadb> "
        )
        self.term_box.configure(state="normal")
        self.term_box.insert("end", welcome)
        self.term_box.configure(state="disabled")

        # ── Barre de saisie ───────────────────────────────────────────────
        ib = ctk.CTkFrame(p, fg_color=C["panel"], corner_radius=8)
        ib.grid(row=2, column=0, padx=12, pady=(0, 4), sticky="ew")
        ib.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(ib, text="adb>",
            font=ctk.CTkFont(family="Courier New", size=14, weight="bold"),
            text_color=C["green"]
        ).grid(row=0, column=0, padx=(12, 6), pady=8)

        self.term_input = ctk.CTkEntry(ib,
            placeholder_text="Entrez une commande ADB...",
            fg_color="#000000",
            border_color=C["green"],
            text_color=C["terminal"],
            font=ctk.CTkFont(family="Courier New", size=12), height=38)
        self.term_input.grid(row=0, column=1, padx=4, pady=8, sticky="ew")
        self.term_input.bind("<Return>", lambda e: self._term_exec())
        self.term_input.bind("<Up>",     self._term_hist_up)
        self.term_input.bind("<Down>",   self._term_hist_down)

        ctk.CTkButton(ib, text="▶ EXEC", width=86,
            command=self._term_exec,
            fg_color=C["green"], hover_color=self._darken(C["green"]),
            text_color="#000", font=ctk.CTkFont(weight="bold", size=12)
        ).grid(row=0, column=2, padx=4, pady=8)

        ctk.CTkButton(ib, text="CLR", width=50,
            command=lambda: self._term_clear(),
            fg_color=C["yellow"], hover_color=self._darken(C["yellow"]),
            text_color="#000", font=ctk.CTkFont(size=10)
        ).grid(row=0, column=3, padx=(0, 8), pady=8)

        # ── Raccourcis rapides ────────────────────────────────────────────
        qb = ctk.CTkScrollableFrame(p, fg_color=C["panel"],
                                     height=42, corner_radius=6, orientation="horizontal")
        qb.grid(row=3, column=0, padx=12, pady=(0, 10), sticky="ew")

        quick_cmds = [
            ("devices",       "devices"),
            ("model",         "shell getprop ro.product.model"),
            ("android ver",   "shell getprop ro.build.version.release"),
            ("battery",       "shell dumpsys battery | head -12"),
            ("ps",            "shell ps -A | head -30"),
            ("netstat",       "shell netstat"),
            ("df",            "shell df /data"),
            ("wifi",          "shell dumpsys wifi | grep SSID | head -5"),
            ("logcat(W)",     "logcat -d *:W | head -30"),
            ("packages",      "shell pm list packages -3"),
            ("wm size",       "shell wm size"),
            ("uptime",        "shell uptime"),
            ("cpu info",      "shell cat /proc/cpuinfo | head -20"),
            ("mem info",      "shell cat /proc/meminfo | head -10"),
            ("running apps",  "shell am stack list"),
        ]
        for lbl, cmd in quick_cmds:
            ctk.CTkButton(qb, text=lbl, width=100,
                command=lambda c=cmd: self._term_run_cmd(c),
                fg_color=C["card2"], hover_color=C["card"],
                text_color=C["green"],
                font=ctk.CTkFont(family="Courier New", size=9), height=28,
                corner_radius=4
            ).pack(side="left", padx=3, pady=3)

    def _term_exec(self):
        cmd = self.term_input.get().strip()
        if not cmd:
            return
        self.term_history.append(cmd)
        self.term_hist_idx = len(self.term_history)
        self.term_input.delete(0, "end")
        self._term_run_cmd(cmd)

    def _term_run_cmd(self, cmd: str):
        def _run():
            self.term_box.configure(state="normal")
            self.term_box.insert("end", f"\nadb> {cmd}\n")

            if cmd.lower() in ("clear", "cls"):
                self.term_box.delete("1.0", "end")
                self.term_box.insert("end", "adb> ")
                self.term_box.configure(state="disabled")
                return

            if cmd.lower() == "help":
                self.term_box.insert("end",
                    "  shell <cmd>     → Commande sur l'appareil Android\n"
                    "  devices          → Appareils ADB connectés\n"
                    "  pull <src> <dst> → Copier du téléphone vers le PC\n"
                    "  push <src> <dst> → Copier du PC vers le téléphone\n"
                    "  install <apk>    → Installer un APK\n"
                    "  logcat           → Voir les logs Android\n"
                    "  <toute cmd ADB>  → Exécutée directement\n"
                    "  clear / cls      → Effacer le terminal\n"
                    "  ↑↓               → Naviguer dans l'historique\n"
                )
            else:
                r = self.adb.run(cmd)
                if r:
                    if r.stdout.strip():
                        self.term_box.insert("end", r.stdout)
                    if r.stderr.strip():
                        self.term_box.insert("end", f"[stderr] {r.stderr}\n")
                else:
                    self.term_box.insert("end", "❌ Erreur d'exécution ADB\n")

            self.term_box.insert("end", "\nadb> ")
            self.term_box.see("end")
            self.term_box.configure(state="disabled")
        self._thread(_run)

    def _term_clear(self):
        self.term_box.configure(state="normal")
        self.term_box.delete("1.0", "end")
        self.term_box.insert("end", "adb> ")
        self.term_box.configure(state="disabled")

    def _term_hist_up(self, event):
        if self.term_history and self.term_hist_idx > 0:
            self.term_hist_idx -= 1
            self.term_input.delete(0, "end")
            self.term_input.insert(0, self.term_history[self.term_hist_idx])

    def _term_hist_down(self, event):
        if self.term_hist_idx < len(self.term_history) - 1:
            self.term_hist_idx += 1
            self.term_input.delete(0, "end")
            self.term_input.insert(0, self.term_history[self.term_hist_idx])
        else:
            self.term_hist_idx = len(self.term_history)
            self.term_input.delete(0, "end")

    # =========================================================================
    #  CONNEXION ADB
    # =========================================================================
    def _auto_connect(self):
        if not self.adb.check_adb_installed():
            self.conn_badge.configure(text="● ADB NON TROUVÉ", text_color=C["red"])
            self.dev_lbl.configure(
                text="ADB introuvable!\nInstallez Android Platform Tools\n"
                     "puis ajoutez-le au PATH")
            return
        self._thread(self._connect_thread)

    def _connect_thread(self):
        self.conn_badge.configure(text="● CONNEXION...", text_color=C["yellow"])
        ok = self.adb.connect()
        if ok:
            d = self.adb.device_info
            self.conn_badge.configure(text="● CONNECTÉ", text_color=C["green"])
            self.dev_lbl.configure(
                text=f"{d.get('brand','')} {d.get('model','')}\n"
                     f"Android {d.get('android','?')} • SDK {d.get('sdk','?')}\n"
                     f"{d.get('cpu','?')}")
            self.after(0, self._refresh_dashboard)
        else:
            self.conn_badge.configure(text="● DÉCONNECTÉ", text_color=C["red"])
            self.dev_lbl.configure(
                text="Aucun appareil connecté\n\n"
                     "1. Active Options Développeur\n"
                     "    (7× sur Numéro de build)\n"
                     "2. Active Débogage USB\n"
                     "3. Branche le câble USB\n"
                     "4. Autorise ce PC")


# =============================================================================
#  ENTRY POINT
# =============================================================================
def main():
    # Vérification ADB avant lancement
    try:
        subprocess.run(["adb", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "ADB non trouvé",
            "ADB n'est pas installé ou pas dans le PATH.\n\n"
            "Installation:\n"
            "  Windows : Android Platform Tools\n"
            "            developer.android.com/studio/releases/platform-tools\n"
            "  Linux   : sudo apt install adb\n"
            "  macOS   : brew install android-platform-tools"
        )
        sys.exit(1)

    app = ADBMasterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
