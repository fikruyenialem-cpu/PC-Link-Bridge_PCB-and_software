#!/usr/bin/env python3
"""
PC Link - Desktop Application Entry Point
Usage:
  python main.py
  python main.py --role "PC B"
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from software.ui import PCLinkApp
from software.config import save_settings, load_settings

def main():
    parser = argparse.ArgumentParser(description="PC Link - Dual USB-A PC-to-PC Data Bridge & Power Management")
    parser.add_argument("--role", choices=["PC A", "PC B"], help="Force local computer role (PC A or PC B)")
    parser.add_argument("--mode", choices=["virtual", "serial"], help="Force connection mode (virtual or serial)")
    parser.add_argument("--port", help="Serial port to connect (e.g. COM3)")
    args = parser.parse_args()

    settings = load_settings()
    if args.role:
        settings["local_role"] = args.role
    if args.mode:
        settings["connection_mode"] = args.mode
    if args.port:
        settings["serial_port"] = args.port
    save_settings(settings)

    app = PCLinkApp()
    app.mainloop()

if __name__ == "__main__":
    main()
