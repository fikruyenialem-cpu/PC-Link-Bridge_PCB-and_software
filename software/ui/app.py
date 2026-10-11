"""
PC Link - Main Application Window and Navigation Controller
"""
import customtkinter as ctk
from typing import Dict, Any
from ..config import THEME, APP_NAME, TAGLINE, VERSION, load_settings, save_settings
from .theme import setup_app_theme
from .views import DashboardView, TransferView, PowerView, SettingsView, AboutView
from ..hardware import VirtualHardwareBridge, SerialHardwareBridge
from ..transfer.engine import FileTransferEngine

class PCLinkApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        setup_app_theme()

        self.title(f"{APP_NAME} v{VERSION} — Dual USB-A PC-to-PC Bridge")
        self.geometry("1100x720")
        self.minsize(960, 600)
        self.configure(fg_color=THEME["BG_DARK"])

        # Load settings
        self.settings = load_settings()

        # Initialize hardware bridge
        self._init_bridge()

        # Initialize file transfer engine
        self.transfer_engine = FileTransferEngine(self.bridge, self.settings["download_dir"])

        # Navigation state
        self.views = {}
        self.active_view_name = "dashboard"

        # Build UI layout
        self._build_sidebar()
        self._build_content_area()

        # Select initial view
        self.show_view("dashboard")

        # Start periodic telemetry timer (1 Hz)
        self.after(1000, self._on_telemetry_tick)

        # Handle clean exit
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_bridge(self):
        mode = self.settings.get("connection_mode", "virtual")
        role = self.settings.get("local_role", "PC A")
        if mode == "serial":
            port = self.settings.get("serial_port", "AUTO")
            baud = self.settings.get("baud_rate", 115200)
            self.bridge = SerialHardwareBridge(port, baud)
        else:
            self.bridge = VirtualHardwareBridge(role)

        if self.settings.get("auto_connect", True):
            self.bridge.connect()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self, width=220, corner_radius=0,
            fg_color=THEME["CARD_BG"], border_color=THEME["CARD_BORDER"], border_width=1
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # App Logo & Branding Title
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(20, 20))

        logo_row = ctk.CTkFrame(brand_frame, fg_color="transparent")
        logo_row.pack(fill="x", anchor="w")

        dot = ctk.CTkFrame(logo_row, width=10, height=10, corner_radius=5, fg_color=THEME["PRIMARY"])
        dot.pack(side="left", padx=(0, 8))

        lbl_logo = ctk.CTkLabel(
            logo_row, text=APP_NAME.upper(),
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=THEME["TEXT_MAIN"]
        )
        lbl_logo.pack(side="left")

        lbl_sub = ctk.CTkLabel(
            brand_frame, text=TAGLINE,
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=THEME["PRIMARY"]
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # Navigation Buttons
        self.nav_btns = {}
        nav_items = [
            ("dashboard", "Dashboard / Home"),
            ("transfer", "File Transfer"),
            ("power", "Power Control"),
            ("settings", "Settings"),
            ("about", "About & Help"),
        ]

        for key, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=label,
                anchor="w", height=40, corner_radius=6,
                fg_color="transparent",
                hover_color=THEME["SECONDARY"],
                text_color=THEME["TEXT_MUTED"],
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda k=key: self.show_view(k)
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.nav_btns[key] = btn

        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)

        # Bottom Connection & Role Pill Card
        bot_card = ctk.CTkFrame(self.sidebar, fg_color=THEME["SECONDARY"], corner_radius=6)
        bot_card.pack(fill="x", padx=12, pady=16)

        self.lbl_side_role = ctk.CTkLabel(
            bot_card, text=f"Role: {self.settings['local_role']}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME["TEXT_MAIN"]
        )
        self.lbl_side_role.pack(anchor="w", padx=12, pady=(10, 2))

        status_row = ctk.CTkFrame(bot_card, fg_color="transparent")
        status_row.pack(anchor="w", padx=12, pady=(0, 10))

        self.side_dot = ctk.CTkFrame(status_row, width=8, height=8, corner_radius=4, fg_color=THEME["PRIMARY"])
        self.side_dot.pack(side="left", padx=(0, 6))

        self.lbl_side_status = ctk.CTkLabel(
            status_row, text="Bridge Online",
            font=ctk.CTkFont(size=11), text_color=THEME["TEXT_SECONDARY"]
        )
        self.lbl_side_status.pack(side="left")

    def _build_content_area(self):
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.pack(side="right", fill="both", expand=True)

        # Instantiate all views
        self.views["dashboard"] = DashboardView(self.content_container, self.bridge, self.transfer_engine, self)
        self.views["transfer"] = TransferView(self.content_container, self.bridge, self.transfer_engine, self)
        self.views["power"] = PowerView(self.content_container, self.bridge, self)
        self.views["settings"] = SettingsView(self.content_container, self.bridge, self)
        self.views["about"] = AboutView(self.content_container, self)

    def show_view(self, view_name: str):
        if view_name not in self.views:
            return

        self.active_view_name = view_name

        # Highlight active button
        for key, btn in self.nav_btns.items():
            if key == view_name:
                btn.configure(
                    fg_color=THEME["SECONDARY"],
                    text_color=THEME["PRIMARY"]
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=THEME["TEXT_MUTED"]
                )

        # Show selected view
        for name, view in self.views.items():
            if name == view_name:
                view.pack(fill="both", expand=True)
            else:
                view.pack_forget()

    def get_setting(self, key: str, default=None):
        return self.settings.get(key, default)

    def set_setting(self, key: str, val: Any):
        self.settings[key] = val
        if key == "local_role":
            self.lbl_side_role.configure(text=f"Role: {val}")
            if isinstance(self.bridge, VirtualHardwareBridge):
                self.bridge.role = val
        elif key == "download_dir":
            self.transfer_engine.set_download_dir(val)
        save_settings(self.settings)

    def log(self, message: str, level: str = "INFO"):
        if "dashboard" in self.views:
            self.views["dashboard"].add_log_entry(message, level)

    def _on_telemetry_tick(self):
        # Update dashboard metrics
        if "dashboard" in self.views:
            self.views["dashboard"].update_telemetry()

        # Update sidebar connection indicator
        if self.bridge.is_connected():
            self.side_dot.configure(fg_color=THEME["PRIMARY"])
            self.lbl_side_status.configure(text="Bridge Active")
        else:
            self.side_dot.configure(fg_color=THEME["DANGER_RED"])
            self.lbl_side_status.configure(text="Disconnected")

        self.after(1000, self._on_telemetry_tick)

    def _on_close(self):
        if self.bridge:
            self.bridge.disconnect()
        self.destroy()
