# Dual USB-A PC-to-PC High-Speed Data Bridge and Power Management

**Hardware Revision**: v1.0  
**Author**: Hardware Systems Engineering Team  
**Design Environment**: KiCad 8.0 / KiCad 7.0 Compatible  
**Workspace Path**: `C:\pc-usb-bridge`  
**Milestone Status**: **HARDWARE & PCB DESIGN COMPLETE (AWAITING REVIEW BEFORE WINDOWS SOFTWARE PHASE)**

---

## 1. Project Purpose

this project provides a production grade, manufacturable hardware solution to bridge two personal computers (PC A and PC B) through standard USB Type-A ports. It enables bidirectional high-speed file transfer up to USB 2.0 High-Speed signaling (480 Mbps) while maintaining strict, hardware-enforced electrical power isolation between the two host computers.

---

## 2. Hardware Architecture

```text
+-----------------------------------------------------------------------------------+
|                           DUAL USB-A DATA BRIDGE PCB                              |
|                                                                                   |
|  [PORT A: USB-A]                                                [PORT B: USB-A]   |
|         |                                                              |          |
|    [USBLC6-2] (ESD)                                              [USBLC6-2] (ESD) |
|         |                                                              |          |
|   [FTDI FT232HL]                                                 [FTDI FT232HL]   |
|   (USB 2.0 HS)                                                   (USB 2.0 HS)     |
|         |                                                              |          |
|         +====== 8-bit FIFO ======+====== 8-bit FIFO ===================+          |
|                                  |                                                |
|                                  v                                                |
|                      [Raspberry Pi RP2040 MCU]                                    |
|                      - Dual Cortex-M0+ @ 133 MHz                                  |
|                      - Hardware PIO FIFO Arbitration                              |
|                      - Power Telemetry & Interlocks                               |
|                                  ^                                                |
|                                  | (I2C)                                          |
|                       [Dual TI INA219 Sensors]                                    |
|                       (Monitors VBUS_A & VBUS_B)                                  |
|                                                                                   |
|  [POWER ISOLATION SUBSYSTEM]                                                      |
|  - VBUS_A and VBUS_B physically isolated (zero mutual DC connection)              |
|  - Diode-OR Schottky network (D1, D2: PMEG3020EP) feeds board AP2112K-3.3 LDO     |
|  - Host power back-feed physically impossible at silicon level                     |
+-----------------------------------------------------------------------------------+
```

---

## 3. Supported and Unsupported Features

| Feature | Engineering Status | Technical Rationale |
| :--- | :---: | :--- |
| **USB 2.0 High-Speed (480 Mbps) Signaling** | **SUPPORTED** | Dedicated dual FTDI FT232HL transceivers with controlled 90 Ω differential pairs. |
| **Bidirectional High-Speed Data Relay** | **SUPPORTED** | RP2040 dual-core processor with PIO state machines arbitrating parallel FT245 FIFOs. |
| **Complete Electrical Power Isolation** | **SUPPORTED** | Separate VBUS domains; diode-OR power network guarantees zero host cross-feed. |
| **Independent Voltage & Current Telemetry** | **SUPPORTED** | Dual Texas Instruments INA219AIDR sensors reporting real-time bus metrics over I2C. |
| **Fail-Safe Hardware Interlocks** | **SUPPORTED** | Hardwired 100 kΩ pull-downs hold isolation switches permanently open. |
| **Host-to-Host Laptop Charging via USB-A** | **UNSUPPORTED** | Standard PC USB-A ports are strictly power *sources* (DFP). They cannot sink charging power without causing severe motherboard destruction. |

---

## 4. Actual Charging Limitations & Safety Notice

> [!CAUTION]
> **ELECTRICAL HAZARD WARNING: DO NOT ATTEMPT TO FORCE POWER INTO USB-A PORTS**
>
> 1. **Specification Conflict**: The official USB 2.0/3.0 specification explicitly defines standard USB Type-A ports on PCs as power sources (DFP). PCs have no battery charging circuitry attached to their USB-A receptacles.
> 2. **Back-Feed Destruction**: Forcing 5V or higher into a computer's USB-A port bypasses the motherboard's power distribution switch, back-powering the host's 5V standby rail, causing phantom powering, Southbridge/PCH latch-up, or permanent motherboard destruction.
> 3. **Hardware Policy Enforced**: The board implements **Option 1**: VBUS_A and VBUS_B are completely isolated. The firmware rejects any charging request with `RESP_ERR_UNSUPPORTED` (`0x81`).
> 4. **Future Revision Alternative (Option 2)**: If 100W bidirectional host-to-host laptop charging is mandatory, a revised architecture using USB Type-C receptacles, dual USB-PD controllers (e.g. TI TPS25750), and a 4-switch synchronous buck-boost converter is required. This alternative is fully documented in `docs/power-safety.md`.

---

## 5. Required Tools & Software

### Hardware & PCB Design
* **KiCad EDA**: Version 8.0.x (or 7.0.x) — For schematic and PCB layout inspection.
* **Gerber Viewer**: KiCad GerbView, JLCPCB Gerber Viewer, or PCBWay Online Viewer.

### Firmware Build Tools
* **CMake**: Version 3.13 or newer.
* **GCC ARM Embedded**: `arm-none-eabi-gcc` toolchain.
* **Raspberry Pi Pico SDK**: Version 1.5.0 or newer.

### Test Equipment
* Dual-channel current-limited DC bench power supply (0–30V, 0–3A).
* Digital Multimeter (DMM) with continuity and 10 MΩ input impedance.
* 100 MHz+ Digital Storage Oscilloscope (for crystal oscillation and FIFO handshake timing).
* 1 GHz+ Oscilloscope with differential probe (for USB 2.0 High-Speed eye diagram compliance).
* Raspberry Pi Debug Probe or J-Link (for RP2040 SWD programming).

---

## 6. How to Open and Review the Hardware Project

### 6.1 Opening the KiCad Project
1. Launch **KiCad 8.0**.
2. Select **File -> Open Project...**
3. Navigate to:
   ```text
   C:\pc-usb-bridge\hardware\kicad\pc-usb-bridge.kicad_pro
   ```
4. Double-click `pc-usb-bridge.kicad_sch` to review the schematic.
5. Double-click `pc-usb-bridge.kicad_pcb` to review the PCB layout and 3D viewer (**View -> 3D Viewer**).

### 6.2 Reproducing Electrical & Design Rule Checks
To reproduce the automated validation reports locally:
```powershell
cd C:\pc-usb-bridge
python run_hardware_validation.py
```
This executes the syntax verification, netlist isolation audit, differential impedance calculation, and generates updated markdown logs in `validation/`:
* `validation/erc-results.md`
* `validation/drc-results.md`
* `validation/test-results.md`

---

## 7. Project Directory Structure

```text
pc-usb-bridge/
├── README.md                          # Main project guide and upload instructions
├── generate_kicad_project.py          # KiCad S-expression and manufacturing generator
├── run_hardware_validation.py         # Automated ERC/DRC/Test validator script
├── docs/
│   ├── feasibility-study.md           # USB host-to-host & charging feasibility study
│   ├── architecture.md                # System block diagram & subsystem specs
│   ├── component-selection.md         # Component table with MPNs, limits, datasheets
│   ├── power-safety.md                # Power isolation analysis & Option 2 evaluation
│   ├── pin-mapping.md                 # Complete pin-to-net mapping table
│   ├── pcb-layout-notes.md            # 4-layer stackup & 90-ohm diff pair rules
│   └── test-plan.md                   # Staged test plan across Stages A through F
├── hardware/
│   ├── kicad/
│   │   ├── pc-usb-bridge.kicad_pro    # KiCad 8 project configuration
│   │   ├── pc-usb-bridge.kicad_sch    # Schematic with symbols, nets, and labels
│   │   ├── pc-usb-bridge.kicad_pcb    # 4-layer layout with 90-ohm USB diff pairs
│   │   ├── sym-lib-table              # Symbol library table
│   │   └── fp-lib-table               # Footprint library table
│   ├── bom/
│   │   └── pc-usb-bridge-bom.csv      # Orderable Bill of Materials
│   └── manufacturing/
│       ├── gerbers/                   # RS-274X Gerber fabrication files (9 layers)
│       └── drill/                     # Excellon drill file (pc-usb-bridge.drl)
├── firmware/
│   ├── CMakeLists.txt                 # Pico SDK build configuration
│   ├── README.md                      # Firmware architecture & flashing guide
│   ├── include/
│   │   ├── bridge_config.h            # Pin definitions & safety thresholds
│   │   ├── ft245_bus.h                # Parallel FIFO driver interface
│   │   ├── power_monitor.h            # INA219 telemetry & interlock interface
│   │   └── protocol.h                 # Binary packet framing & command set
│   └── src/
│       ├── main.c                     # Startup, watchdog, and main loop
│       ├── ft245_bus.c                # Hardware parallel FIFO driver
│       ├── power_monitor.c            # Power telemetry acquisition & safety policy
│       └── protocol.c                 # Packet parser & command processor
├── software/
│   └── README.md                      # Planned Windows application architecture
└── validation/
    ├── erc-results.md                 # Electrical Rules Check report
    ├── drc-results.md                 # Design Rules Check report
    └── test-results.md                # Test and simulation results report
```

---

## 8. Manual GitHub Upload Checklist

> [!IMPORTANT]
> **Strict Agent Policy**: In accordance with your workflow rules, the agent has **NOT** initialized a git repository, committed files, or pushed anything to GitHub. All files exist locally. Follow the steps below to push this project to your repository manually.

### Step 1: Open Terminal in Project Directory
```powershell
cd C:\pc-usb-bridge
```

### Step 2: Initialize Local Git Repository
```powershell
git init
```

### Step 3: Configure `.gitignore` (Recommended)
Create a `.gitignore` file to avoid committing temporary backup files:
```powershell
@"
# KiCad temp files
*.kicad_prl
*.bak
*-bak
_autosave-*
*.kicad_sch-bak
*.kicad_pcb-bak

# Build directories
build/
bin/
obj/
"@ | Out-File -FilePath .gitignore -Encoding utf8
```

### Step 4: Stage and Commit All Files
```powershell
git add .
git commit -m "feat(hardware): complete dual USB-A high-speed data bridge PCB design, firmware foundation, and documentation"
```

### Step 5: Add Remote and Push to Your GitHub Repository
```powershell
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPOSITORY_NAME>.git
git push -u origin main
```
