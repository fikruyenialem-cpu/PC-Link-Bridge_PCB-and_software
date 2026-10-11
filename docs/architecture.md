# System Architecture Specification

**Project**: Dual USB-A PC-to-PC High-Speed Data Bridge  
**Document**: Architecture Specification  
**Status**: APPROVED

---

## 1. System Overview

The Dual USB-A PC-to-PC Data Bridge is a hardware device designed to connect two host personal computers (PC A and PC B) via standard USB Type-A ports, enabling high-speed, bidirectional data transfer while strictly isolating their respective power domains.

### 1.1 Architecture Block Diagram

```text
+---------------------------------------------------------------------------------------------------+
|                                      DUAL USB-A DATA BRIDGE PCB                                   |
|                                                                                                   |
|  [USB-A PORT A]                                                                  [USB-A PORT B]   |
|   +-----------+                                                                  +-----------+    |
|   | VBUS_A    |---+ (Diode D1) --+                      +-- (Diode D2) <---------| VBUS_B    |    |
|   |           |   |              |                      |                        |           |    |
|   |           |   |      [Diode-OR 5V Bus]              |                        |           |    |
|   |           |   |              |                      |                        |           |    |
|   |           |   |              v                      |                        |           |    |
|   |           |   |      [3.3V LDO: AP2112K]            |                        |           |    |
|   |           |   |              |                      |                        |           |    |
|   |           |   |              +--> [+3.3V Rail]      |                        |           |    |
|   |           |   |              |    (Powers Logic)    |                        |           |    |
|   |           |   |              |                      |                        |           |    |
|   |           |   v              |                      v                        |           |    |
|   |           | [INA219 #1]      |                  [INA219 #2]                  |           |    |
|   |           | (Monitors A)     |                  (Monitors B)                 |           |    |
|   |           |   |              |                      |                        |           |    |
|   | D+ / D-   |   | (I2C)        |                      | (I2C)                  | D+ / D-   |    |
|   +-----+-----+   |              |                      |                        +-----+-----+    |
|         |         |              |                      |                              |          |
|    [USBLC6-2]     |              |                      |                         [USBLC6-2]      |
|    (ESD Array)    |              |                      |                         (ESD Array)     |
|         |         |              |                      |                              |          |
|         v         v              v                      v                              v          |
|   +-------------------+  +----------------------------------+  +-------------------+              |
|   |    FTDI FT232HL   |  |     Raspberry Pi RP2040 MCU      |  |    FTDI FT232HL   |              |
|   |     (Bridge A)    |  |       (Dual Core 133MHz)         |  |     (Bridge B)    |              |
|   |                   |  |                                  |  |                   |              |
|   |  - USB 2.0 PHY    |  |  Core 0: FIFO A / Telemetry / WDT|  |  - USB 2.0 PHY    |              |
|   |  - 480 Mbps HS    |  |  Core 1: FIFO B / Framing Engine |  |  - 480 Mbps HS    |              |
|   |  - FT245 FIFO     |  |  PIO SM0/1: Port A 8-bit bus     |  |  - FT245 FIFO     |              |
|   |  - EEPROM: 93LC56 |  |  PIO SM2/3: Port B 8-bit bus     |  |  - EEPROM: 93LC56 |              |
|   +---------+---------+  +----------------------------------+  +---------+---------+              |
|             |                            |                               |                        |
|             +==== 8-bit Parallel Bus ====^==== 8-bit Parallel Bus =======+                        |
|                   (D[7:0], RXF#, TXE#,         (D[7:0], RXF#, TXE#,                               |
|                    RD#, WR#)                    RD#, WR#)                                         |
|                                                                                                   |
|  [SAFETY SUBSYSTEM]                                                                               |
|  - VBUS_A and VBUS_B physically separated with zero DC cross-feed                                 |
|  - Hardware interlock: Back-to-back load switch held OFF by hardwired pull-downs                  |
|  - Status LEDs: PWR_GOOD (Green), LINK_A (Blue), LINK_B (Blue), ACT (Amber), FAULT (Red)          |
|  - SWD Header: SWCLK, SWDIO, GND, 3V3 for firmware programming and hardware debugging            |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Subsystem Functional Breakdown

| Subsystem Name | Primary Components | Functions & Responsibilities | Interfaces & Signal Types | Dependencies | Prototype Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **USB Physical Port A** | `J1` (Amphenol GSB19111KEU), `D3` (USBLC6-2SC6), `FB1`, `C1-C4` | USB Type-A female interface to PC A. Clamps ESD spikes; filters VBUS noise; presents standard 90Ω differential impedance. | `USB_A_DP`, `USB_A_DM`, `VBUS_A`, `GND` | External PC A connection | **Essential** |
| **USB Physical Port B** | `J2` (Amphenol GSB19111KEU), `D4` (USBLC6-2SC6), `FB2`, `C5-C8` | USB Type-A female interface to PC B. Clamps ESD spikes; filters VBUS noise; presents standard 90Ω differential impedance. | `USB_B_DP`, `USB_B_DM`, `VBUS_B`, `GND` | External PC B connection | **Essential** |
| **Bridge Controller A** | `U2` (FTDI FT232HL), `Y2` (12 MHz Crystal), `U4` (93LC56B EEPROM) | High-Speed USB 2.0 peripheral controller for PC A. Translates USB bulk endpoints into 8-bit parallel FT245 FIFO transactions. | USB High-Speed differential; 8-bit parallel data + 4 control strobes | 3.3V rail, 1.8V internal core, 12 MHz oscillator | **Essential** |
| **Bridge Controller B** | `U3` (FTDI FT232HL), `Y3` (12 MHz Crystal), `U5` (93LC56B EEPROM) | High-Speed USB 2.0 peripheral controller for PC B. Translates USB bulk endpoints into 8-bit parallel FT245 FIFO transactions. | USB High-Speed differential; 8-bit parallel data + 4 control strobes | 3.3V rail, 1.8V internal core, 12 MHz oscillator | **Essential** |
| **Intermediate MCU** | `U1` (Raspberry Pi RP2040), `U6` (Winbond W25Q128 Flash), `Y1` (12 MHz Crystal) | Arbitrates bidirectional FIFO streams using Programmable I/O (PIO) state machines. Processes host commands, monitors telemetry, controls status LEDs. | 24 GPIOs for dual FT245 buses; I2C for telemetry; SWD for debug | +3.3V rail, +1.1V internal LDO, 12 MHz oscillator | **Essential** |
| **Power Input & OR-ing** | `D1`, `D2` (Diodes Inc. PMEG3020EP Schottky diodes) | Power OR-ing network. Powers the on-board logic from either PC A or PC B while guaranteeing zero back-feed into the opposing host. | `VBUS_A`, `VBUS_B` in; `VBUS_OR` out | VBUS from either host | **Essential** |
| **Voltage Regulation** | `U7` (Diodes Inc. AP2112K-3.3), `C9-C14` | Ultra-low-dropout, low-noise linear regulator delivering clean +3.3V @ 600mA to RP2040, FT232HL I/O, EEPROMs, and sensors. | +5V nominal in; +3.3V ±1.5% out | `VBUS_OR` rail | **Essential** |
| **Power Telemetry** | `U8`, `U9` (TI INA219AIDR), `R_SH1`, `R_SH2` (0.1Ω 1% 1206) | Measures bus voltage (0–26V) and current draw (up to ±3.2A, 0.8mA resolution) on both USB ports independently. | I2C (`I2C1_SDA`, `I2C1_SCL`) to RP2040 | +3.3V logic, VBUS rails | **Essential** |
| **Safety Interlock** | `Q1`, `Q2` (Back-to-back P-MOSFETs), `R_PD1` (100kΩ pull-down) | Hardwired isolation switch. Guarantees physical disconnect between VBUS_A and VBUS_B under all operating conditions. | Gate drive from RP2040; fail-safe open | Logic power, MCU GPIO | **Essential** |
| **Indicators & Debug** | `LED1-LED5`, `SW1` (BOOTSEL), `SW2` (RESET), `J3` (SWD Header) | Provides visual health indicators and tactile debug / programming hooks. | GPIO drive, SWD lines | +3.3V rail | **Essential** |

---

## 3. Communication Protocol Architecture

### 3.1 Host-to-Device Protocol (Windows Application Interface)
Each Windows PC communicates with its respective FT232HL bridge chip using the FTDI D2XX direct-access API or standard WinUSB interface.

Data packets are framed with a robust binary header:
```text
+--------------+--------------+---------------+----------------+-------------------+---------------+
| SYNC (2 B)   | CMD (1 B)    | FLAGS (1 B)   | LENGTH (2 B)   | PAYLOAD (0..4096) | CRC16 (2 B)   |
| 0xAA 0x55    | (Opcode)     | (Stream/Ctrl) | (Payload size) | (Binary data)     | (CCITT-FALSE) |
+--------------+--------------+---------------+----------------+-------------------+---------------+
```

### 3.2 Command Set
* `CMD_PING` (0x01): Host ping / keepalive. Bridge replies with firmware version and uptime.
* `CMD_GET_TELEMETRY` (0x02): Queries voltage, current, and link status of both ports.
* `CMD_GET_CAPABILITIES` (0x03): Returns supported features (High-Speed transfer supported; Charging UNSUPPORTED).
* `CMD_SET_POWER_MODE` (0x04): Request power role change. Hardware responds with `ERR_UNSUPPORTED` (0x81).
* `CMD_DATA_PAYLOAD` (0x10): Raw streaming data block to be forwarded to opposing PC.
* `CMD_DATA_ACK` (0x11): Flow control packet acknowledgement.

---

## 4. Hardware Safety Philosophy

1. **Hardware Independence**: The protection circuitry does not rely on Windows software or microcontroller code to prevent back-feeding. The diode-OR configuration physically blocks reverse current at the silicon level.
2. **Cold Plug Immunity**: Either host can be plugged or unplugged dynamically without interrupting the bridge's internal state machine or causing voltage spikes on the remaining host.
3. **Brownout & Watchdog Protection**: The RP2040 internal brownout detector (BOD) resets the microcontroller safely if supply voltage drops below 2.8V. A hardware watchdog timer (WDT) triggers a reset within 50 ms if firmware hangs.
