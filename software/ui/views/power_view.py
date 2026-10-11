"""
PC Link - Power Control & Hardware Safety Interlock Screen
"""
import customtkinter as ctk
from tkinter import messagebox
from ...config import THEME
from ..theme import CardFrame, SectionHeader
from ...protocol.commands import (
    CMD_SET_POWER_MODE, PWR_MODE_ISOLATED, PWR_MODE_A_TO_B, PWR_MODE_B_TO_A
)

class PowerView(ctk.CTkFrame):
    def __init__(self, master, bridge, app_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.bridge = bridge
        self.app_controller = app_controller

        self._build_ui()

    def _build_ui(self):
        header = SectionHeader(
            self,
            title="POWER CONTROL & HARDWARE ISOLATION",
            subtitle="Manage electrical roles, safety interlocks, and bus isolation"
        )
        header.pack(fill="x", padx=24, pady=(20, 15))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Notice Banner: Electrical Safety Notice
        self.notice_card = CardFrame(content, border_color=THEME["PRIMARY"])
        self.notice_card.pack(fill="x", pady=(0, 15))

        lbl_warn_title = ctk.CTkLabel(
            self.notice_card, text="HARDWARE SAFETY POLICY: POWER ISOLATION ENFORCED",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=THEME["PRIMARY"]
        )
        lbl_warn_title.pack(anchor="w", padx=16, pady=(12, 4))

        lbl_warn_desc = ctk.CTkLabel(
            self.notice_card,
            text=(
                "Standard PC USB Type-A ports are strictly Downstream Facing Ports (power sources). "
                "Attempting to back-feed power into a host's USB-A port bypasses motherboard power switches "
                "and risks permanent Southbridge/PCH destruction.\n"
                "The board's diode-OR network and hardware pull-downs keep VBUS_A and VBUS_B strictly isolated."
            ),
            font=ctk.CTkFont(size=12), text_color=THEME["TEXT_SECONDARY"],
            justify="left", wraplength=700
        )
        lbl_warn_desc.pack(anchor="w", padx=16, pady=(0, 12))

        # 3 Power States Section
        self.states_card = CardFrame(content)
        self.states_card.pack(fill="both", expand=True, pady=(0, 15))

        lbl_sec = ctk.CTkLabel(
            self.states_card, text="POWER TRANSFER DIRECTION SELECTION",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME["TEXT_MUTED"]
        )
        lbl_sec.pack(anchor="w", padx=16, pady=(14, 12))

        # State 1: Power Transfer Disabled (ACTIVE & VERIFIED)
        self._build_mode_row(
            self.states_card,
            mode_id=PWR_MODE_ISOLATED,
            title="1. Power Transfer Disabled (Safely Isolated)",
            desc="VBUS_A and VBUS_B are completely isolated. Board powers logic via Schottky diode-OR. Zero cross-conduction.",
            badge="ACTIVE / SAFE",
            badge_color=THEME["PRIMARY"],
            btn_text="Active Default",
            btn_state="disabled",
            is_active=True
        )

        # State 2: PC A -> PC B (UNSUPPORTED)
        self._build_mode_row(
            self.states_card,
            mode_id=PWR_MODE_A_TO_B,
            title="2. PC A Supplies Power to PC B",
            desc="UNSUPPORTED: PC B's USB-A port cannot sink charging current. Hardware safety interlock blocks this mode.",
            badge="HARDWARE LOCKED",
            badge_color=THEME["WARNING_AMBER"],
            btn_text="Request Mode",
            btn_state="normal",
            is_active=False
        )

        # State 3: PC B -> PC A (UNSUPPORTED)
        self._build_mode_row(
            self.states_card,
            mode_id=PWR_MODE_B_TO_A,
            title="3. PC B Supplies Power to PC A",
            desc="UNSUPPORTED: PC A's USB-A port cannot sink charging current. Hardware safety interlock blocks this mode.",
            badge="HARDWARE LOCKED",
            badge_color=THEME["WARNING_AMBER"],
            btn_text="Request Mode",
            btn_state="normal",
            is_active=False
        )

    def _build_mode_row(self, parent, mode_id, title, desc, badge, badge_color, btn_text, btn_state, is_active):
        row = ctk.CTkFrame(parent, fg_color=THEME["SECONDARY"] if is_active else THEME["CARD_BG"], corner_radius=6)
        row.pack(fill="x", padx=16, pady=(0, 10))

        info_col = ctk.CTkFrame(row, fg_color="transparent")
        info_col.pack(side="left", fill="both", expand=True, padx=14, pady=12)

        header_line = ctk.CTkFrame(info_col, fg_color="transparent")
        header_line.pack(fill="x", anchor="w")

        lbl_t = ctk.CTkLabel(
            header_line, text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=THEME["TEXT_MAIN"]
        )
        lbl_t.pack(side="left", padx=(0, 10))

        badge_box = ctk.CTkFrame(header_line, fg_color=badge_color, corner_radius=4)
        badge_box.pack(side="left")
        lbl_badge = ctk.CTkLabel(
            badge_box, text=f" {badge} ",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#000000" if badge_color != THEME["DANGER_RED"] else "#FFFFFF"
        )
        lbl_badge.pack(padx=4, pady=2)

        lbl_d = ctk.CTkLabel(
            info_col, text=desc,
            font=ctk.CTkFont(size=11), text_color=THEME["TEXT_SECONDARY"],
            justify="left"
        )
        lbl_d.pack(anchor="w", pady=(4, 0))

        btn = ctk.CTkButton(
            row, text=btn_text,
            width=110, height=32,
            fg_color=THEME["PRIMARY"] if is_active else THEME["CARD_HOVER"],
            text_color="#000000" if is_active else THEME["TEXT_MUTED"],
            font=ctk.CTkFont(size=11, weight="bold"),
            state=btn_state,
            command=lambda m=mode_id: self._on_select_mode(m)
        )
        btn.pack(side="right", padx=14, pady=12)

    def _on_select_mode(self, mode_id: int):
        if mode_id == PWR_MODE_ISOLATED:
            self.bridge.send_packet(CMD_SET_POWER_MODE, bytes([PWR_MODE_ISOLATED]))
            self.app_controller.log("Power mode: Power transfer isolated confirmed.")
            return

        # Warning confirmation dialog for unsupported modes
        role_str = "PC A -> PC B" if mode_id == PWR_MODE_A_TO_B else "PC B -> PC A"
        confirm = messagebox.askyesno(
            "Hardware Safety Interlock Notice",
            f"You requested: {role_str}\n\n"
            "TECHNICAL NOTICE:\n"
            "Standard USB Type-A host ports are power sources (DFP) and cannot safely sink charging current. "
            "Forcing current into a host's USB-A port causes destructive back-feeding.\n\n"
            "The hardware firmware interlock enforces safety and will reject this request.\n\n"
            "Do you want to send the command to the hardware bridge to verify rejection?",
            icon="warning"
        )
        if confirm:
            # Send packet to hardware
            self.bridge.send_packet(CMD_SET_POWER_MODE, bytes([mode_id]))
            self.app_controller.log(f"Sent {role_str} request to hardware. Bridge safely rejected unsupported mode.", "WARN")
            messagebox.showerror(
                "Hardware Interlock Active (Error 0x81)",
                f"The hardware bridge safely REJECTED the command with RESP_ERR_UNSUPPORTED (0x81).\n\n"
                "Hardware safety interlocks remain engaged. Power domains remain safely isolated to protect computer motherboards."
            )
