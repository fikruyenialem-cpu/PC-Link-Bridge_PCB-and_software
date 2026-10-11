"""
PC Link - Theme and CustomTkinter Styling Configuration
"""
import customtkinter as ctk
from ..config import THEME

def setup_app_theme():
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("green")

class CardFrame(ctk.CTkFrame):
    """A styled container card with dark forest green / obsidian styling and subtle border."""
    def __init__(self, master, **kwargs):
        config = {
            "fg_color": THEME["CARD_BG"],
            "border_color": THEME["CARD_BORDER"],
            "border_width": 1,
            "corner_radius": 8,
        }
        config.update(kwargs)
        super().__init__(master, **config)

class SectionHeader(ctk.CTkFrame):
    """Standardized section header with accent pill."""
    def __init__(self, master, title: str, subtitle: str = "", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", anchor="w")
        
        pill = ctk.CTkFrame(row, width=4, height=22, fg_color=THEME["PRIMARY"], corner_radius=2)
        pill.pack(side="left", padx=(0, 10))
        
        lbl_title = ctk.CTkLabel(
            row, text=title,
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=THEME["TEXT_MAIN"]
        )
        lbl_title.pack(side="left")

        if subtitle:
            lbl_sub = ctk.CTkLabel(
                self, text=subtitle,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=THEME["TEXT_MUTED"]
            )
            lbl_sub.pack(anchor="w", pady=(2, 0), padx=(14, 0))
