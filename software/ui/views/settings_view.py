"""
PC Link - Settings View
"""
import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
import serial.tools.list_ports
from ...config import THEME, save_settings
from ..theme import CardFrame, SectionHeader

class SettingsView(ctk.CTkFrame):
    def __init__(self, master, bridge, app_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.bridge = bridge
        self.app_controller = app_controller

        self._build_ui()

    def _build_ui(self):
        header = SectionHeader(
            self,
            title="SETTINGS & PREFERENCES",
            subtitle="Configure local instance identity, bridge connections, and storage"
        )
        header.pack(fill="x", padx=24, pady=(20, 15))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Card 1: Instance Identity
        card_id = CardFrame(content)
        card_id.pack(fill="x", pady=(0, 15))

        lbl_id = ctk.CTkLabel(card_id, text="LOCAL COMPUTER IDENTITY", font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME["TEXT_MUTED"])
        lbl_id.pack(anchor="w", padx=16, pady=(14, 8))

        row_id = ctk.CTkFrame(card_id, fg_color="transparent")
        row_id.pack(fill="x", padx=16, pady=(0, 14))

        lbl_role = ctk.CTkLabel(row_id, text="Operating Role:", font=ctk.CTkFont(size=12), text_color=THEME["TEXT_MAIN"])
        lbl_role.pack(side="left", padx=(0, 10))

        curr_role = self.app_controller.get_setting("local_role")
        self.combo_role = ctk.CTkComboBox(
            row_id, values=["PC A", "PC B"],
            fg_color=THEME["SECONDARY"], border_color=THEME["SECONDARY_BORDER"],
            text_color=THEME["TEXT_MAIN"], font=ctk.CTkFont(size=12),
            command=self._on_role_changed
        )
        self.combo_role.set(curr_role)
        self.combo_role.pack(side="left", padx=(0, 20))

        lbl_note = ctk.CTkLabel(
            row_id, text="(Instance automatically identifies as PC A or PC B on the bridge)",
            font=ctk.CTkFont(size=11), text_color=THEME["TEXT_MUTED"]
        )
        lbl_note.pack(side="left")

        # Card 2: Bridge Connection Mode
        card_conn = CardFrame(content)
        card_conn.pack(fill="x", pady=(0, 15))

        lbl_conn = ctk.CTkLabel(card_conn, text="HARDWARE BRIDGE INTERFACE", font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME["TEXT_MUTED"])
        lbl_conn.pack(anchor="w", padx=16, pady=(14, 8))

        row_mode = ctk.CTkFrame(card_conn, fg_color="transparent")
        row_mode.pack(fill="x", padx=16, pady=(0, 10))

        lbl_m = ctk.CTkLabel(row_mode, text="Connection Mode:", font=ctk.CTkFont(size=12), text_color=THEME["TEXT_MAIN"])
        lbl_m.pack(side="left", padx=(0, 10))

        curr_mode = self.app_controller.get_setting("connection_mode")
        self.combo_mode = ctk.CTkComboBox(
            row_mode, values=["virtual", "serial"],
            fg_color=THEME["SECONDARY"], border_color=THEME["SECONDARY_BORDER"],
            text_color=THEME["TEXT_MAIN"], font=ctk.CTkFont(size=12)
        )
        self.combo_mode.set(curr_mode)
        self.combo_mode.pack(side="left", padx=(0, 20))

        # Port Selection Row
        row_port = ctk.CTkFrame(card_conn, fg_color="transparent")
        row_port.pack(fill="x", padx=16, pady=(0, 14))

        lbl_p = ctk.CTkLabel(row_port, text="COM Port (if Serial):", font=ctk.CTkFont(size=12), text_color=THEME["TEXT_MAIN"])
        lbl_p.pack(side="left", padx=(0, 10))

        ports = [p.device for p in serial.tools.list_ports.comports()]
        if not ports:
            ports = ["AUTO"]
        else:
            ports.insert(0, "AUTO")

        self.combo_port = ctk.CTkComboBox(
            row_port, values=ports,
            fg_color=THEME["SECONDARY"], border_color=THEME["SECONDARY_BORDER"],
            text_color=THEME["TEXT_MAIN"], font=ctk.CTkFont(size=12)
        )
        self.combo_port.set(self.app_controller.get_setting("serial_port"))
        self.combo_port.pack(side="left", padx=(0, 10))

        # Card 3: Storage & Destination
        card_storage = CardFrame(content)
        card_storage.pack(fill="x", pady=(0, 15))

        lbl_st = ctk.CTkLabel(card_storage, text="FILE STORAGE DESTINATION", font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME["TEXT_MUTED"])
        lbl_st.pack(anchor="w", padx=16, pady=(14, 8))

        row_dest = ctk.CTkFrame(card_storage, fg_color="transparent")
        row_dest.pack(fill="x", padx=16, pady=(0, 14))

        self.entry_dest = ctk.CTkEntry(
            row_dest,
            fg_color=THEME["BG_DARK"], border_color=THEME["CARD_BORDER"],
            text_color=THEME["TEXT_MAIN"], font=ctk.CTkFont(size=12)
        )
        self.entry_dest.insert(0, self.app_controller.get_setting("download_dir"))
        self.entry_dest.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_browse_dest = ctk.CTkButton(
            row_dest, text="Browse...", width=80,
            fg_color=THEME["SECONDARY"], hover_color=THEME["SECONDARY_BORDER"],
            text_color=THEME["TEXT_MAIN"], font=ctk.CTkFont(size=12),
            command=self._on_browse_dest
        )
        btn_browse_dest.pack(side="left")

        # Save Button & Status
        bottom_row = ctk.CTkFrame(content, fg_color="transparent")
        bottom_row.pack(fill="x", pady=(10, 0))

        btn_save = ctk.CTkButton(
            bottom_row, text="Save Settings",
            fg_color=THEME["PRIMARY"], hover_color=THEME["PRIMARY_HOVER"],
            text_color="#000000", font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_save_settings, height=36
        )
        btn_save.pack(side="left", padx=(0, 15))

        self.lbl_save_status = ctk.CTkLabel(
            bottom_row, text="",
            font=ctk.CTkFont(size=12), text_color=THEME["PRIMARY"]
        )
        self.lbl_save_status.pack(side="left")

    def _on_browse_dest(self):
        new_dir = filedialog.askdirectory(title="Select Download Folder for PC Link")
        if new_dir:
            self.entry_dest.delete(0, "end")
            self.entry_dest.insert(0, new_dir)

    def _on_role_changed(self, new_role: str):
        self.app_controller.set_setting("local_role", new_role)
        self.app_controller.log(f"Switched role to {new_role}")

    def _on_save_settings(self):
        settings = {
            "local_role": self.combo_role.get(),
            "connection_mode": self.combo_mode.get(),
            "serial_port": self.combo_port.get(),
            "download_dir": self.entry_dest.get()
        }
        for k, v in settings.items():
            self.app_controller.set_setting(k, v)
        save_settings(self.app_controller.settings)
        self.lbl_save_status.configure(text="Settings saved successfully!")
        self.after(3000, lambda: self.lbl_save_status.configure(text=""))
        self.app_controller.log("Settings saved.")
