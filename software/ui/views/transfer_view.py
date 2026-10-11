"""
PC Link - File Transfer Screen
"""
import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
from ...config import THEME
from ..theme import CardFrame, SectionHeader
from ...transfer.engine import TransferState

class TransferView(ctk.CTkFrame):
    def __init__(self, master, bridge, transfer_engine, app_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.bridge = bridge
        self.transfer_engine = transfer_engine
        self.app_controller = app_controller
        self.selected_file_path: str = ""

        # Hook engine callbacks
        self.transfer_engine.on_progress = self._on_engine_progress
        self.transfer_engine.on_complete = self._on_engine_complete
        self.transfer_engine.on_offer_received = self._on_offer_received

        self._build_ui()

    def _build_ui(self):
        header = SectionHeader(
            self,
            title="FILE TRANSFER",
            subtitle="Bidirectional, high-speed chunked transfer with SHA-256 verification"
        )
        header.pack(fill="x", padx=24, pady=(20, 15))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Top Card: File Selection
        self.card_select = CardFrame(content)
        self.card_select.pack(fill="x", pady=(0, 15))

        lbl_sec1 = ctk.CTkLabel(
            self.card_select, text="SELECT FILE TO SEND",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME["TEXT_MUTED"]
        )
        lbl_sec1.pack(anchor="w", padx=16, pady=(14, 8))

        row_pick = ctk.CTkFrame(self.card_select, fg_color="transparent")
        row_pick.pack(fill="x", padx=16, pady=(0, 14))

        self.btn_browse = ctk.CTkButton(
            row_pick, text="Browse Files...",
            fg_color=THEME["PRIMARY"], hover_color=THEME["PRIMARY_HOVER"],
            text_color="#000000", font=ctk.CTkFont(size=12, weight="bold"),
            command=self._on_browse_file, height=34
        )
        self.btn_browse.pack(side="left", padx=(0, 12))

        self.lbl_selected_file = ctk.CTkLabel(
            row_pick, text="No file selected. Click Browse to choose a file.",
            font=ctk.CTkFont(size=12), text_color=THEME["TEXT_SECONDARY"]
        )
        self.lbl_selected_file.pack(side="left", fill="x", expand=True)

        # Middle Card: Active Transfer Monitor
        self.card_progress = CardFrame(content)
        self.card_progress.pack(fill="both", expand=True, pady=(0, 15))

        lbl_sec2 = ctk.CTkLabel(
            self.card_progress, text="TRANSFER PROGRESS & VERIFICATION",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME["TEXT_MUTED"]
        )
        lbl_sec2.pack(anchor="w", padx=16, pady=(14, 8))

        # File and Status Info
        self.lbl_transfer_name = ctk.CTkLabel(
            self.card_progress, text="Status: IDLE",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=THEME["TEXT_MAIN"]
        )
        self.lbl_transfer_name.pack(anchor="w", padx=16, pady=(0, 4))

        self.lbl_transfer_details = ctk.CTkLabel(
            self.card_progress, text="Ready to initiate high-speed transfer.",
            font=ctk.CTkFont(size=12), text_color=THEME["TEXT_MUTED"]
        )
        self.lbl_transfer_details.pack(anchor="w", padx=16, pady=(0, 12))

        # Progress Bar
        self.prog_bar = ctk.CTkProgressBar(
            self.card_progress,
            progress_color=THEME["PRIMARY"],
            fg_color=THEME["SECONDARY"],
            height=12, corner_radius=6
        )
        self.prog_bar.pack(fill="x", padx=16, pady=(0, 12))
        self.prog_bar.set(0.0)

        # Speed, Size, ETA metrics row
        metrics_row = ctk.CTkFrame(self.card_progress, fg_color="transparent")
        metrics_row.pack(fill="x", padx=16, pady=(0, 16))

        self.lbl_metric_transferred = ctk.CTkLabel(
            metrics_row, text="Transferred: 0 B / 0 B (0%)",
            font=ctk.CTkFont(size=12), text_color=THEME["TEXT_SECONDARY"]
        )
        self.lbl_metric_transferred.pack(side="left")

        self.lbl_metric_speed = ctk.CTkLabel(
            metrics_row, text="Speed: 0.0 KB/s",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME["PRIMARY"]
        )
        self.lbl_metric_speed.pack(side="left", padx=20)

        self.lbl_metric_eta = ctk.CTkLabel(
            metrics_row, text="ETA: --",
            font=ctk.CTkFont(size=12), text_color=THEME["TEXT_MUTED"]
        )
        self.lbl_metric_eta.pack(side="right")

        # Action Buttons Row
        btn_row = ctk.CTkFrame(self.card_progress, fg_color="transparent")
        btn_row.pack(anchor="w", padx=16, pady=(0, 16))

        self.btn_start = ctk.CTkButton(
            btn_row, text="Send to Remote PC",
            fg_color=THEME["PRIMARY"], hover_color=THEME["PRIMARY_HOVER"],
            text_color="#000000", font=ctk.CTkFont(size=12, weight="bold"),
            command=self._on_start_transfer, height=34
        )
        self.btn_start.pack(side="left", padx=(0, 10))

        self.btn_pause = ctk.CTkButton(
            btn_row, text="Pause",
            fg_color=THEME["SECONDARY"], hover_color=THEME["SECONDARY_BORDER"],
            text_color=THEME["TEXT_MAIN"], font=ctk.CTkFont(size=12),
            command=self._on_pause_resume, height=34, state="disabled"
        )
        self.btn_pause.pack(side="left", padx=(0, 10))

        self.btn_cancel = ctk.CTkButton(
            btn_row, text="Cancel",
            fg_color="#3B1C1C", hover_color="#522424",
            text_color=THEME["DANGER_RED"], font=ctk.CTkFont(size=12),
            command=self._on_cancel, height=34, state="disabled"
        )
        self.btn_cancel.pack(side="left")

    def _on_browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select File to Send over PC Link"
        )
        if file_path:
            self.selected_file_path = file_path
            p = Path(file_path)
            size_mb = p.stat().st_size / (1024 * 1024)
            self.lbl_selected_file.configure(
                text=f"{p.name} ({size_mb:.2f} MB) — {p.parent}"
            )
            self.lbl_transfer_name.configure(text=f"Ready to send: {p.name}")
            self.lbl_transfer_details.configure(text=f"Total file size: {self._format_bytes(p.stat().st_size)}")

    def _on_start_transfer(self):
        if not self.selected_file_path:
            return
        if not self.bridge.is_connected():
            self.lbl_transfer_details.configure(
                text="Error: Hardware bridge disconnected. Cannot send file.",
                text_color=THEME["DANGER_RED"]
            )
            return

        self.btn_start.configure(state="disabled")
        self.btn_pause.configure(state="normal", text="Pause")
        self.btn_cancel.configure(state="normal")
        self.prog_bar.set(0.0)

        success = self.transfer_engine.send_file(self.selected_file_path)
        if success:
            self.app_controller.log(f"Initiated file transfer: {Path(self.selected_file_path).name}")
        else:
            self.lbl_transfer_details.configure(
                text="Error starting transfer. Busy or connection dropped.",
                text_color=THEME["DANGER_RED"]
            )
            self.btn_start.configure(state="normal")

    def _on_pause_resume(self):
        if self.transfer_engine.state == TransferState.PAUSED:
            self.transfer_engine.resume_transfer()
            self.btn_pause.configure(text="Pause")
            self.app_controller.log("Transfer resumed.")
        elif self.transfer_engine.state in (TransferState.SENDING, TransferState.RECEIVING):
            self.transfer_engine.pause_transfer()
            self.btn_pause.configure(text="Resume")
            self.app_controller.log("Transfer paused.")

    def _on_cancel(self):
        self.transfer_engine.cancel_transfer()
        self.btn_start.configure(state="normal")
        self.btn_pause.configure(state="disabled")
        self.btn_cancel.configure(state="disabled")
        self.app_controller.log("Transfer canceled by user.", "WARN")

    def _on_engine_progress(self, data: dict):
        # Update progress widgets thread-safely via root timer
        pct = data["percent"] / 100.0
        self.prog_bar.set(pct)

        direction = "Sending" if data["is_sender"] else "Receiving"
        self.lbl_transfer_name.configure(
            text=f"{direction}: {data['filename']} [{data['state']}]",
            text_color=THEME["PRIMARY"] if data["state"] != TransferState.PAUSED else THEME["WARNING_AMBER"]
        )

        tr_str = self._format_bytes(data["transferred"])
        tot_str = self._format_bytes(data["total"])
        self.lbl_metric_transferred.configure(
            text=f"Transferred: {tr_str} / {tot_str} ({data['percent']:.1f}%)"
        )

        speed_str = self._format_speed(data["speed_bps"])
        self.lbl_metric_speed.configure(text=f"Speed: {speed_str}")

        eta = data["eta_s"]
        eta_str = f"{int(eta)}s remaining" if eta > 0 else "--"
        self.lbl_metric_eta.configure(text=f"ETA: {eta_str}")

    def _on_engine_complete(self, filename: str, success: bool, message: str):
        self.btn_start.configure(state="normal")
        self.btn_pause.configure(state="disabled", text="Pause")
        self.btn_cancel.configure(state="disabled")

        if success:
            self.prog_bar.set(1.0)
            self.lbl_transfer_name.configure(
                text=f"Transfer Completed: {filename}",
                text_color=THEME["PRIMARY"]
            )
            self.lbl_transfer_details.configure(
                text=f"SUCCESS: {message} (SHA-256 Verified)",
                text_color=THEME["PRIMARY"]
            )
            self.app_controller.log(f"Completed {filename}: {message}")
        else:
            self.lbl_transfer_name.configure(
                text=f"Transfer Failed: {filename}",
                text_color=THEME["DANGER_RED"]
            )
            self.lbl_transfer_details.configure(
                text=f"FAILED: {message}",
                text_color=THEME["DANGER_RED"]
            )
            self.app_controller.log(f"Failed {filename}: {message}", "ERROR")

    def _on_offer_received(self, filename: str, size: int):
        self.btn_start.configure(state="disabled")
        self.btn_pause.configure(state="normal", text="Pause")
        self.btn_cancel.configure(state="normal")
        self.lbl_transfer_name.configure(
            text=f"Receiving: {filename}",
            text_color=THEME["PRIMARY"]
        )
        self.lbl_transfer_details.configure(
            text=f"Incoming transfer ({self._format_bytes(size)}) accepted automatically."
        )
        self.app_controller.log(f"Receiving file {filename} ({self._format_bytes(size)})")

    def _format_bytes(self, b: int) -> str:
        if b < 1024:
            return f"{b} B"
        elif b < 1024 * 1024:
            return f"{b / 1024:.1f} KB"
        elif b < 1024 * 1024 * 1024:
            return f"{b / (1024 * 1024):.2f} MB"
        else:
            return f"{b / (1024 * 1024 * 1024):.2f} GB"

    def _format_speed(self, bps: float) -> str:
        if bps < 1024:
            return f"{bps:.0f} B/s"
        elif bps < 1024 * 1024:
            return f"{bps / 1024:.1f} KB/s"
        else:
            return f"{bps / (1024 * 1024):.2f} MB/s"
