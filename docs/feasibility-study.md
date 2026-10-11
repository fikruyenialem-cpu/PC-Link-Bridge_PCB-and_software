# Feasibility Study: Dual USB-A Host-to-Host Data Bridge and Power Analysis

**Project**: Dual USB-A PC-to-PC High-Speed Data Bridge  
**Author**: Hardware Systems Engineering Team  
**Date**: October 2026  
**Status**: APPROVED / ARCHITECTURE FROZEN

---

## 1. Executive Summary

This feasibility study investigates the engineering requirements, physical constraints, and safety implications of connecting two personal computers via their USB Type-A ports to achieve high-speed data transfer and managed power distribution.

Key engineering determinations:
1. **Host-to-Host Data Transfer**: Two standard USB hosts cannot be connected directly via passive copper cabling without causing physical damage and enumeration failure. An active dual-device bridge architecture is required.
2. **Bandwidth Feasibility**: USB 2.0 High-Speed (480 Mbps raw signaling) is selected. Realistic achievable application-level bulk transfer rates are between 32 MB/s and 42 MB/s (~256 Mbps to ~336 Mbps) after USB protocol overhead, packet framing, and operating system scheduling.
3. **USB-A Power/Charging Reality**: Standard USB Type-A ports on PCs are strictly Downstream Facing Ports (DFP), meaning they are power *sources*, never power *sinks*. Neither connected PC can safely accept charging power via USB-A. Attempting to back-feed power into a host's USB-A port bypasses motherboard power distribution switches and risks destroying the Southbridge/PCH or power management circuitry.
4. **Architecture Selection**: **Option 1** is selected and enforced in hardware: complete electrical isolation between the power domains of the two computers, safe diode-OR board powering, dual High-Speed USB bridge ICs (FTDI FT232HL), and an intermediate high-performance microcontroller (Raspberry Pi RP2040) with dedicated hardware interlocks.

---

## 2. USB-A Host-to-Host Data Transfer Investigation

### 2.1 The Passive Connection Hazard
In the USB architecture (USB 2.0 Specification §4.1):
* The bus topology is strictly tiered-star with a single Host at the root.
* All peripheral ports are Devices.
* USB Type-A receptacles on computers supply +5V nominal on pin 1 (`VBUS`) and act as master controllers driving bus arbitration, Start-of-Frame (SOF) tokens, and transaction scheduling.

If a passive cable with two USB Type-A male connectors is plugged between two computers:
1. **Power Contention**: Two unregulated or slightly differing 5V supplies (e.g., PC A at 5.12V, PC B at 4.95V) are placed directly in parallel with near-zero loop resistance. Severe circulating currents flow into the lower-voltage supply, tripping motherboard polyfuses or burning out power switches.
2. **Signaling Collision**: Both host controllers assert pull-down resistors (15 kΩ nominal) on `D+` and `D-`. Neither host detects the standard device pull-up resistor (1.5 kΩ on `D+` for Full/High Speed), so neither host initiates enumeration. If either host attempts packet transmission, driver contention on the transceiver stages will occur.

**Conclusion**: A passive USB-A to USB-A connection is strictly forbidden and non-functional.

### 2.2 Active Bridge Architectural Options

To enable safe communication, the bridge hardware must present itself as a standard **USB Device** (Upstream Facing Port / UFP) to both computers simultaneously.

| Architecture Option | Description | High-Speed (480 Mbps) Feasibility | Driver / OS Complexity | Component Availability | Feasibility Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Option A: Legacy Single-Chip Bridge (e.g., Prolific PL25A1)** | Obsolete ASIC used in Windows Easy Transfer cables. | Theoretical 480 Mbps. | Requires legacy Prolific proprietary drivers. | End-of-Life (EOL), obsolete at distributors, unorderable. | **REJECTED**: Not manufacturable with modern, verifiable supply chains. |
| **Option B: Dual-PHY Microcontroller (Single MCU)** | High-end MCU (e.g., STM32H7, NXP LPC55S69) with two USB peripherals. | Most MCUs feature 1 HS + 1 FS, or require two external ULPI PHYs (e.g., USB3300) with 24 high-speed parallel lines. | Complex dual USB stack in firmware; high CPU load. | High complexity (QFP-144/BGA packages, multi-rail PMICs, 6-layer PCB). | **REJECTED**: Excessive BOM cost and routing complexity. |
| **Option C: Back-to-Back High-Speed Bridges with Intermediate Controller** | Two FTDI FT232HL High-Speed USB to FIFO ICs connected via a Raspberry Pi RP2040 dual-core processor. | Full 480 Mbps physical signaling per port; sustained ~35 MB/s data relay via hardware PIO state machines. | Uses standard, WHQL-certified FTDI D2XX / WinUSB drivers. Zero kernel driver development. | 100% active, orderable from Mouser, DigiKey, Farnell, LCSC. | **SELECTED**: Robust, fully verifiable, standard packages, modular firmware. |

### 2.3 Selected Data Bridge Architecture: Dual FT232HL + RP2040
* **Host A Interface**: FTDI FT232HL configured in FT245 Asynchronous/Synchronous FIFO mode. Enumerates on PC A as a High-Speed USB device.
* **Host B Interface**: FTDI FT232HL configured in identical mode. Enumerates on PC B as a High-Speed USB device.
* **Bridge Engine**: Raspberry Pi RP2040 running at 133–200 MHz. Core 0 manages Port A PIO FIFO and telemetry. Core 1 manages Port B PIO FIFO and framing.
* **Flow Control**: Hardware-level FIFO flags (`RXF#`, `TXE#`) guarantee zero data loss without requiring software polling.

---

## 3. Investigation of the Charging Requirement

### 3.1 Host Port Electrical Constraints
Standard PC USB Type-A ports conform to the following specifications:
* **USB 2.0 Host**: 5V ± 5% (4.75V to 5.25V), maximum continuous current 500 mA (2.5W total power).
* **USB 3.0/3.1 Host**: 5V ± 5% (4.45V to 5.25V), maximum continuous current 900 mA (4.5W total power).
* **BC 1.2 CDP/DCP**: Up to 1.5A at 5V (7.5W), available only on dedicated high-current charging ports.

### 3.2 Can a PC Accept Charging Power Over USB-A?
**Definitive Engineering Finding: NO.**
1. **Physical Circuitry on Host**:
   * On PC motherboards and laptops, the USB-A `VBUS` line is connected to the output of an internal power distribution switch (e.g., Texas Instruments TPS2051, Silergy SY6280, or motherboard 5V standby power rail).
   * These switches feature internal body diodes or reverse-blocking MOSFETs configured to deliver power *outward*.
   * There is **no battery charge management IC** connected to the USB-A receptacle. Laptop battery charging circuits (typically 3S/4S Lithium-ion, requiring 12.6V to 16.8V charging voltage) are connected exclusively to the DC barrel jack or dedicated USB-C Power Delivery ports.
2. **Destructive Consequences of Back-Feeding**:
   * Injecting 5V or higher into a PC's USB-A port forces current backward into the host's 5V rail.
   * If the host is powered down or in sleep mode, this can back-power the motherboard's power plane unexpectedly ("phantom powering"), causing erratic latch-up, overvoltage damage to the Southbridge/Platform Controller Hub (PCH), or tripping the host's Embedded Controller (EC) into permanent fault shutdown.

### 3.3 Power Architecture Evaluation (Options 1 vs 2 vs 3)

#### Option 1: Preserve USB-A Ports with Safe Power Isolation (SELECTED)
* **Design**: Keep exactly two USB-A female connectors.
* **Power Transfer**: Completely disabled. `VBUS_A` and `VBUS_B` are physically isolated from each other.
* **Board Powering**: Dual Schottky diode-OR network (`D1`, `D2`) routes power from either PC A or PC B to the on-board 3.3V low-dropout regulator (AP2112K-3.3). The board functions seamlessly whether one or both PCs are connected.
* **Telemetry**: Dual TI INA219 current/voltage monitors report real-time bus voltage and current draw of each port to the bridge controller.
* **Hardware Interlock**: Dedicated back-to-back isolation MOSFET switches remain hard-locked in the OFF state via hardware pull-down resistors.
* **Firmware Policy**: Firmware rejects any command requesting host-to-host power transfer with `ERR_UNSUPPORTED_HARDWARE`.

#### Option 2: Propose Revised USB-C Power Delivery Architecture (FOR FUTURE REVISION)
If bidirectional host-to-host laptop charging is mandatory, the connector architecture must be revised:
* Replace USB-A connectors with USB Type-C receptacles.
* Integrate two USB-PD Port Controllers (e.g., TI TPS25750 or Cypress CCG3).
* Integrate a high-power bidirectional buck-boost converter (e.g., TI BQ25713 or MPS MP2808) supporting 5V/9V/15V/20V at up to 5A (100W).
* **Trade-offs**: BOM cost increases by ~$25–$35; PCB area increases significantly; thermal dissipation requires heatsinking; 6-layer PCB stack-up needed for high-current copper planes.

#### Option 3: External Auxiliary Power Supply
* Retain USB-A for data and add an external 12V/24V barrel jack to power peripheral attachments.
* Does not resolve the fundamental impossibility of charging laptops through their USB-A ports.

---

## 4. Feasibility Conclusion & Next Steps

Option 1 provides a safe, standard-compliant, fully manufacturable hardware solution. The engineering team will proceed with:
1. Full architecture specification.
2. Complete component selection of orderable parts with datasheets.
3. KiCad 8 schematic capture with exact pin mapping and isolation safety.
4. 4-layer controlled-impedance PCB layout.
5. Embedded firmware foundation for the RP2040 bridge engine.
