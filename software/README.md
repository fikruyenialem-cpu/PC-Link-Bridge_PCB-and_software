# PC Link — Windows Desktop Application Guide

**Project**: Dual USB-A PC-to-PC High-Speed Data Bridge & Power Management  
**Application Name**: **PC Link**  
**Version**: 1.0.0  
**Tagline**: **DATA • POWER • TOGETHER.**  
**Status**: COMPLETE, VERIFIED & PRODUCTION READY

---

## 1. Overview & Visual Identity

**PC Link** is a specialized, professional Windows desktop application engineered to coordinate two personal computers (PC A and PC B) connected via the custom Dual USB-A High-Speed Data Bridge hardware.

### Visual Styling
* **Primary Accent**: Vivid Electric Green (`#00E676`) for active connections, successful data transfer states, and verified indicators.
* **Secondary Elements**: Dark Forest Green (`#0E2A1B`, `#1B4D31`) container cards and obsidian surfaces (`#0A0D0B`, `#131A15`).
* **Text Contrast**: Crisp pure white (`#FFFFFF`) and cool gray (`#B0BEC5`).
* **Alert States**: Amber (`#FFB300`) for warnings; Red (`#FF5252`) for hardware faults.
* **Cover Branding Artwork**: A realistic, metallic computer CPU processor centered on dark PCB traces glowing with electric green circuitry and engraved with **“PC LINK — DATA • POWER • TOGETHER.”** (located in `software/assets/cover.jpg`).

---

## 2. Main Screens & Features

### 2.1 Home / Dashboard
* Displays local host identity ("PC A" or "PC B") and remote host link status in real time.
* Real-time hardware telemetry display from the dual on-board Texas Instruments INA219 sensors:
  * Port A VBUS Voltage (e.g. 5.04 V) and Current Draw (e.g. 95 mA).
  * Port B VBUS Voltage (e.g. 4.98 V) and Current Draw (e.g. 90 mA).
  * Enforced Power Domain Isolation status: `ENFORCED (ISOLATED)`.
* Live event log detailing packet handshake timestamps and transfer milestones.

### 2.2 File Transfer
* Select files and folders with native Windows dialogs.
* Chunked high-speed file transfer engine (4 KB packets) over the binary protocol.
* Live real-time statistics: transferred bytes, total size, percentage progress bar, transfer rate (KB/s and MB/s), and estimated time remaining (ETA).
* Pause, Resume, and Cancel support with zero resource leakage.
* End-to-end SHA-256 cryptographic verification: computes digest before transmission and verifies digest after reception before atomically committing the received file.
* Collision handling: automatically appends unique suffixes (`(1)`, `(2)`) to prevent overwriting existing destination files.

### 2.3 Power Control
* Displays three states:
  1. **Power Transfer Disabled (Safely Isolated)** — Active verified default.
  2. **PC A Supplies Power to PC B** — Marked `HARDWARE LOCKED / UNSUPPORTED`.
  3. **PC B Supplies Power to PC A** — Marked `HARDWARE LOCKED / UNSUPPORTED`.
* Clear technical explanation:
  * Standard PC USB Type-A ports are strictly power sources (DFP). Attempting to sink current into a PC's USB-A port causes destructive back-feeding.
  * The hardware diode-OR network and hardwired pull-downs strictly isolate VBUS_A and VBUS_B.
  * Any live attempt to command host charging triggers a confirmation warning modal and is rejected by the hardware bridge with error code `RESP_ERR_UNSUPPORTED` (`0x81`).

### 2.4 Settings
* Local computer role selection (`PC A` vs `PC B`).
* Connection mode toggle:
  * `Virtual Bridge`: Local loopback relay daemon enabling full dual-instance desktop testing on a single PC.
  * `Serial / Hardware`: Real FTDI USB High-Speed COM port communication.
* Configurable download directory with automatic folder creation.
* Persistent JSON configuration stored in `software/settings.json`.

### 2.5 About & Help
* Full-resolution CPU processor branding artwork display.
* Application version, tagline, and project description.
* Hardware compatibility notes and detailed technical FAQ.

---

## 3. How to Run PC Link

### Prerequisites
* Python 3.10+ (Python 3.12 verified)
* Required packages: `customtkinter`, `pillow`, `pyserial`

```powershell
pip install customtkinter pillow pyserial
```

### Running a Single Instance
```powershell
cd C:\pc-usb-bridge\software
python main.py
```

### Running Dual Coordinated Instances (Simulating PC A & PC B)
Open two separate terminal windows:

**Terminal 1 (PC A Instance):**
```powershell
cd C:\pc-usb-bridge\software
python main.py --role "PC A" --mode "virtual"
```

**Terminal 2 (PC B Instance):**
```powershell
cd C:\pc-usb-bridge\software
python main.py --role "PC B" --mode "virtual"
```

Both instances automatically connect over the internal virtual bridge relay:
1. PC A's dashboard will show `PC B (Remote): Connected`.
2. PC B's dashboard will show `PC A (Remote): Connected`.
3. Select any file in PC A, click **Send to Remote PC**, and observe real-time transfer, speed metrics, and SHA-256 integrity verification on PC B!

---

## 4. Running the Automated Test Suite

```powershell
cd C:\pc-usb-bridge
python software/test_pc_link.py
```

The automated test suite verifies:
* CRC16-CCITT packet framing and unframing.
* Virtual hardware bridge command dispatching and telemetry.
* Safety interlock enforcement (rejection of unsupported charging commands).
* End-to-end 256 KB file transfer with bit-for-bit SHA-256 verification.
