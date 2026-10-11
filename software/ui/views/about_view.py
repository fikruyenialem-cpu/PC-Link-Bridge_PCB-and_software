"""
PC Link - About & Help View featuring CPU Processor Branding Artwork
"""
import customtkinter as ctk
from PIL import Image
from pathlib import Path
from ...config import THEME, APP_NAME, TAGLINE, VERSION
from ..theme import CardFrame, SectionHeader

class AboutView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app_controller = app_controller

        self._build_ui()

    def _build_ui(self):
        header = SectionHeader(
            self,
            title="ABOUT PC LINK",
            subtitle="Project identity, hardware engineering notes, and troubleshooting"
        )
        header.pack(fill="x", padx=24, pady=(20, 15))

        # Scrollable container for about content
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Brand Cover Image Card
        cover_card = CardFrame(scroll)
        cover_card.pack(fill="x", pady=(0, 15))

        # Load cover image from assets
        assets_dir = Path(__file__).parent.parent.parent / "assets"
        cover_path = assets_dir / "cover.jpg"

        if cover_path.exists():
            try:
                # Open with Pillow and resize maintaining aspect ratio
                pil_img = Image.open(cover_path)
                # Compute display size: 680 width x 382 height
                w, h = 680, 382
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(w, h))

                img_label = ctk.CTkLabel(cover_card, image=ctk_img, text="")
                img_label.pack(padx=12, pady=12)
            except Exception as e:
                lbl_err = ctk.CTkLabel(cover_card, text=f"[Branding Artwork: {e}]", text_color=THEME["TEXT_MUTED"])
                lbl_err.pack(pady=20)

        # Branding & Tagline Row
        brand_row = ctk.CTkFrame(cover_card, fg_color="transparent")
        brand_row.pack(fill="x", padx=16, pady=(0, 14))

        lbl_app = ctk.CTkLabel(
            brand_row, text=f"{APP_NAME} v{VERSION}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=THEME["PRIMARY"]
        )
        lbl_app.pack(anchor="w")

        lbl_tag = ctk.CTkLabel(
            brand_row, text=TAGLINE,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=THEME["TEXT_MAIN"]
        )
        lbl_tag.pack(anchor="w", pady=(2, 0))

        # Technical Specification Card
        tech_card = CardFrame(scroll)
        tech_card.pack(fill="x", pady=(0, 15))

        lbl_tech_t = ctk.CTkLabel(
            tech_card, text="HARDWARE SPECIFICATIONS & ARCHITECTURE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME["TEXT_MUTED"]
        )
        lbl_tech_t.pack(anchor="w", padx=16, pady=(14, 8))

        specs_text = (
            "• Architecture: Dual FTDI FT232HL + Raspberry Pi RP2040 Dual-Core Processor\n"
            "• Physical Interfaces: Exactly two USB 2.0 Type-A Female Receptacles (J1, J2)\n"
            "• Signaling Speed: USB 2.0 High-Speed (480 Mbps physical, ~38 MB/s bulk transfer)\n"
            "• Power Architecture: Option 1 — Complete Galvanic & Power Domain Isolation\n"
            "• Power Input: Dual Schottky Diode-OR (PMEG3020EP) powering on-board AP2112K LDO\n"
            "• Telemetry: Dual Texas Instruments INA219AIDR Current/Voltage Sensors over I2C\n"
            "• ESD Protection: STMicroelectronics USBLC6-2SC6 (IEC 61000-4-2 Level 4 Clamping)\n"
            "• PCB Stack-Up: 4-Layer FR-4 with continuous Layer 2 Solid Ground Reference Plane"
        )
        lbl_specs = ctk.CTkLabel(
            tech_card, text=specs_text,
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=THEME["TEXT_SECONDARY"], justify="left"
        )
        lbl_specs.pack(anchor="w", padx=16, pady=(0, 14))

        # Troubleshooting Card
        trouble_card = CardFrame(scroll)
        trouble_card.pack(fill="x", pady=(0, 15))

        lbl_tr_t = ctk.CTkLabel(
            trouble_card, text="TROUBLESHOOTING & COMMON QUESTIONS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME["TEXT_MUTED"]
        )
        lbl_tr_t.pack(anchor="w", padx=16, pady=(14, 8))

        trouble_text = (
            "Q: Why is host-to-host laptop charging disabled?\n"
            "A: Standard PC USB-A ports are strictly power sources (DFP). They cannot accept charging power\n"
            "   without back-feeding the host's 5V standby rail and damaging the motherboard. The hardware\n"
            "   enforces complete power isolation at the silicon level to protect both computers.\n\n"
            "Q: How do I test the application without physical hardware?\n"
            "A: Launch two instances of PC Link on your computer. Instance 1 will act as 'PC A' and\n"
            "   Instance 2 will connect as 'PC B' via the built-in Virtual Hardware Bridge loopback relay.\n\n"
            "Q: Where are received files stored?\n"
            "A: Received files are saved in your Downloads/PC_Link_Transfers folder (configurable in Settings)."
        )
        lbl_trouble = ctk.CTkLabel(
            trouble_card, text=trouble_text,
            font=ctk.CTkFont(size=11), text_color=THEME["TEXT_SECONDARY"],
            justify="left"
        )
        lbl_trouble.pack(anchor="w", padx=16, pady=(0, 14))
