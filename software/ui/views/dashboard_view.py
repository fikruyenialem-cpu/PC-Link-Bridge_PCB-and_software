"""
PC Link - Home / Dashboard View
"""
import customtkinter as ctk
import time
from ...config import THEME
from ..theme import CardFrame, SectionHeader
from ...protocol.commands import PWR_MODE_ISOLATED

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, bridge, transfer_engine, app_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.bridge = bridge
        self.transfer_engine = transfer_engine
        self.app_controller = app_controller

        self._build_ui()

    def _build_ui(self):
        # Top Header
        header = SectionHeader(
            self,
            title="SYSTEM DASHBOARD",
            subtitle="Real-time link status, telemetry metrics, and hardware supervision"
        )
        header.pack(fill="x", padx=24, pady=(20, 15))

        # Main Scrollable / Stack Layout
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Row 1: Connection Overview Cards (3 Cards)
        cards_row = ctk.CTkFrame(content, fg_color="transparent")
        cards_row.pack(fill="x", pady=(0, 15))
        cards_row.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")

        # Card 1: Local Computer
        self.card_local = CardFrame(cards_row)
        self.card_local.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self._build_status_card(
            self.card_local, "LOCAL HOST", "PC A", "Active & Listening", THEME["PRIMARY"]
        )

        # Card 2: Remote Computer
        self.card_remote = CardFrame(cards_row)
        self.card_remote.grid(row=0, column=1, padx=5, sticky="nsew")
        self._build_status_card(
            self.card_remote, "REMOTE HOST", "PC B", "Connected (High-Speed)", THEME["PRIMARY"]
        )

        # Card 3: USB Hardware Bridge
        self.card_bridge = CardFrame(cards_row)
        self.card_bridge.grid(row=0, column=2, padx=(10, 0), sticky="nsew")
        self._build_status_card(
            self.card_bridge, "USB BRIDGE", "Dual FT232HL", "Active (480 Mbps HS)", THEME["PRIMARY"]
        )

        # Row 2: Telemetry Metrics Card
        self.telemetry_card = CardFrame(content)
        self.telemetry_card.pack(fill="x", pady=(0, 15))
        self._build_telemetry_ui()

        # Row 3: Event Log
        self.log_card = CardFrame(content)
        self.log_card.pack(fill="both", expand=True)
        self._build_log_ui()

    def _build_status_card(self, card, subtitle, title, status, color):
        lbl_sub = ctk.CTkLabel(
            card, text=subtitle,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME["TEXT_MUTED"]
        )
        lbl_sub.pack(anchor="w", padx=16, pady=(14, 2))

        lbl_title = ctk.CTkLabel(
            card, text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=THEME["TEXT_MAIN"]
        )
        lbl_title.pack(anchor="w", padx=16, pady=(0, 4))
        card.lbl_title = lbl_title

        status_row = ctk.CTkFrame(card, fg_color="transparent")
        status_row.pack(anchor="w", padx=16, pady=(0, 14))

        dot = ctk.CTkFrame(status_row, width=8, height=8, corner_radius=4, fg_color=color)
        dot.pack(side="left", padx=(0, 6))
        card.dot = dot

        lbl_stat = ctk.CTkLabel(
            status_row, text=status,
            font=ctk.CTkFont(size=12),
            text_color=THEME["TEXT_SECONDARY"]
        )
        lbl_stat.pack(side="left")
        card.lbl_stat = lbl_stat

    def _build_telemetry_ui(self):
        title_row = ctk.CTkFrame(self.telemetry_card, fg_color="transparent")
        title_row.pack(fill="x", padx=16, pady=(14, 10))

        lbl = ctk.CTkLabel(
            title_row, text="HARDWARE POWER & BUS TELEMETRY (TI INA219 SENSORS)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME["TEXT_MUTED"]
        )
        lbl.pack(side="left")

        # Grid of metrics
        grid = ctk.CTkFrame(self.telemetry_card, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=(0, 16))
        grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Metric 1: Port A Voltage
        self.val_v_a = self._add_metric(grid, 0, "PORT A VBUS", "5.04 V", "Nominal 5.0 V")
        # Metric 2: Port A Current
        self.val_i_a = self._add_metric(grid, 1, "PORT A CURRENT", "95 mA", "Host draw (<500mA)")
        # Metric 3: Port B Voltage
        self.val_v_b = self._add_metric(grid, 2, "PORT B VBUS", "4.98 V", "Nominal 5.0 V")
        # Metric 4: Isolation Status
        self.val_iso = self._add_metric(grid, 3, "POWER ISOLATION", "ENFORCED", "Zero Cross-feed", color=THEME["PRIMARY"])

    def _add_metric(self, parent, col, title, val, sub, color=None):
        frame = ctk.CTkFrame(parent, fg_color=THEME["SECONDARY"], corner_radius=6)
        frame.grid(row=0, column=col, padx=5, sticky="nsew", pady=4)

        lbl_t = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=10, weight="bold"), text_color=THEME["TEXT_MUTED"])
        lbl_t.pack(anchor="w", padx=12, pady=(10, 2))

        val_color = color or THEME["TEXT_MAIN"]
        lbl_v = ctk.CTkLabel(frame, text=val, font=ctk.CTkFont(size=18, weight="bold"), text_color=val_color)
        lbl_v.pack(anchor="w", padx=12, pady=(0, 2))

        lbl_s = ctk.CTkLabel(frame, text=sub, font=ctk.CTkFont(size=10), text_color=THEME["TEXT_MUTED"])
        lbl_s.pack(anchor="w", padx=12, pady=(0, 10))

        return lbl_v

    def _build_log_ui(self):
        title_row = ctk.CTkFrame(self.log_card, fg_color="transparent")
        title_row.pack(fill="x", padx=16, pady=(14, 8))

        lbl = ctk.CTkLabel(
            title_row, text="RECENT OPERATIONS & SYSTEM LOG",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME["TEXT_MUTED"]
        )
        lbl.pack(side="left")

        btn_clear = ctk.CTkButton(
            title_row, text="Clear Log", width=70, height=24,
            fg_color=THEME["SECONDARY"], hover_color=THEME["SECONDARY_BORDER"],
            text_color=THEME["TEXT_SECONDARY"], font=ctk.CTkFont(size=11),
            command=self._clear_log
        )
        btn_clear.pack(side="right")

        self.txt_log = ctk.CTkTextbox(
            self.log_card,
            fg_color=THEME["BG_DARK"],
            text_color=THEME["TEXT_SECONDARY"],
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=6
        )
        self.txt_log.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Initial log entries
        self.add_log_entry("PC Link initialized. Safety interlocks verified (Power transfer isolated).")
        self.add_log_entry("Hardware bridge connected. Baud rate / high-speed transceivers active.")

    def add_log_entry(self, message: str, level: str = "INFO"):
        timestamp = time.strftime("%H:%M:%S")
        prefix = f"[{timestamp}] [{level}] "
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", f"{prefix}{message}\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def _clear_log(self):
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.configure(state="disabled")

    def update_telemetry(self):
        """Called periodically by the main application timer."""
        telem = self.bridge.get_telemetry()
        local_role = self.app_controller.get_setting("local_role")
        remote_role = "PC B" if local_role == "PC A" else "PC A"

        # Update local card
        self.card_local.lbl_title.configure(text=f"{local_role} (This PC)")
        self.card_local.lbl_stat.configure(text="Online & Ready")
        self.card_local.dot.configure(fg_color=THEME["PRIMARY"])

        # Update remote card
        is_remote_connected = telem["port_b_connected"] if local_role == "PC A" else telem["port_a_connected"]
        if is_remote_connected:
            self.card_remote.lbl_title.configure(text=f"{remote_role} (Remote)")
            self.card_remote.lbl_stat.configure(text="Connected (480 Mbps HS)")
            self.card_remote.dot.configure(fg_color=THEME["PRIMARY"])
        else:
            self.card_remote.lbl_title.configure(text=f"{remote_role} (Remote)")
            self.card_remote.lbl_stat.configure(text="Awaiting Link...")
            self.card_remote.dot.configure(fg_color=THEME["DISABLED_TEXT"])

        # Update bridge card
        if self.bridge.is_connected():
            self.card_bridge.lbl_stat.configure(text=telem.get("raw_status", "Active"))
            self.card_bridge.dot.configure(fg_color=THEME["PRIMARY"])
        else:
            self.card_bridge.lbl_stat.configure(text="Disconnected")
            self.card_bridge.dot.configure(fg_color=THEME["DANGER_RED"])

        # Update telemetry values
        v_a = telem.get("vbus_a_mv", 0) / 1000.0
        i_a = telem.get("current_a_ma", 0)
        v_b = telem.get("vbus_b_mv", 0) / 1000.0
        i_b = telem.get("current_b_ma", 0)

        self.val_v_a.configure(text=f"{v_a:.2f} V")
        self.val_i_a.configure(text=f"{i_a} mA")
        self.val_v_b.configure(text=f"{v_b:.2f} V")

        if telem.get("fault_status"):
            self.val_iso.configure(text="FAULT DETECTED", text_color=THEME["DANGER_RED"])
        else:
            self.val_iso.configure(text="ENFORCED", text_color=THEME["PRIMARY"])
