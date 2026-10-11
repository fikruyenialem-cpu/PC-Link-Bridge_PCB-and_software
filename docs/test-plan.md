# Comprehensive Hardware Test and Validation Plan

**Project**: Dual USB-A PC-to-PC High-Speed Data Bridge  
**Document**: Staged Hardware Test Plan  
**Status**: APPROVED

---

## 1. Overview and Staging Methodology

This test plan defines the formal verification sequence required to validate the Dual USB-A PC-to-PC Data Bridge hardware from design review through production bench testing and final host integration.

**Safety Rule**: Testing proceeds in strict chronological order across Stages A through F. Under no circumstances may a personal computer be connected to the device until Stages A through E have passed successfully on bench test equipment.

---

## 2. Validation Stages

### Stage A: Design and Pre-Fabrication Validation
*Objective: Verify that all schematic nets, component footprints, electrical ratings, and design rules are valid prior to fabrication.*

| Test ID | Test Item | Procedure | Pass Criteria | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-A1** | **Datasheet & Pinout Audit** | Cross-verify every symbol pin number in KiCad against manufacturer datasheets for U1 (RP2040), U2/U3 (FT232HL), U4/U5 (93LC56B), U6 (W25Q128), U7 (AP2112K), U8/U9 (INA219), D1/D2 (PMEG3020EP). | 100% pin matching; zero unverified or swapped pins. | **PASSED** (In Design) |
| **TC-A2** | **Power Net Isolation Review** | Perform programmatic and visual netlist audit to verify that `VBUS_A` and `VBUS_B` have zero common copper connections or sneak paths. | Complete electrical separation between VBUS domains. | **PASSED** (In Design) |
| **TC-A3** | **Differential Impedance Review** | Verify stack-up dielectric constant ($Er=4.3$), trace width ($0.35\text{ mm}$), and spacing ($0.20\text{ mm}$) using 2D field solver. | Differential impedance within $90\ \Omega \pm 10\%$. | **PASSED** (In Design) |
| **TC-A4** | **KiCad ERC & DRC Execution** | Run Electrical Rules Check (ERC) and Design Rules Check (DRC) on the schematic and layout files. | 0 Errors, 0 Unconnected Nets. | **PASSED** (In Design) |

---

### Stage B: Bare Board & Assembled PCB Manufacturing Checks
*Objective: Verify manufacturing quality and ensure no short circuits exist before applying power.*

| Test ID | Test Item | Required Equipment | Procedure | Pass Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **TC-B1** | **Visual Inspection** | Stereo Microscope (10x–40x) | Inspect all solder joints under magnification. Check QFN-56 and LQFP-48 pins for solder bridging, insufficient wetting, or tombstoning. Check polarity of diodes D1, D2 and electrolytic/tantalum caps. | Clean fillets, zero solder shorts, correct component orientations. |
| **TC-B2** | **Cold Resistance / Short-Circuit Test** | Digital Multimeter (DMM) | With the board completely unpowered, measure resistance to GND on: `VBUS_A`, `VBUS_B`, `VBUS_OR`, `+3V3`, `+1V1_CORE`, `+1V8_CORE_A`, `+1V8_CORE_B`. | All power rails show $> 10\text{ k}\Omega$ resistance to GND. Zero shorts. |
| **TC-B3** | **Port-to-Port Isolation Resistance** | DMM (Hi-Z mode) | Measure DC resistance between `VBUS_A` pad and `VBUS_B` pad. | Resistance $> 10\text{ M}\Omega$ (open circuit). Zero DC leakage. |
| **TC-B4** | **Power Rail Bring-Up Test** | Current-limited DC bench power supply (set to 5.0V, 50 mA limit) | Connect bench supply to `VBUS_A` (with Port B disconnected). Measure: 1. `VBUS_OR` voltage (~4.65V). 2. Output of U7 (`+3V3` rail: 3.30V ± 0.05V). 3. Output of U1 internal LDO (`+1V1_CORE`: 1.10V ± 0.05V). 4. Output of U2 internal LDO (`+1V8_CORE_A`: 1.80V ± 0.05V). Repeat for `VBUS_B`. | All voltage rails within ±2% of nominal; quiescent supply current $< 25\text{ mA}$. |

---

### Stage C: Microcontroller & Controller Bring-Up
*Objective: Verify RP2040 and FTDI startup, clock oscillation, and programming interfaces.*

| Test ID | Test Item | Required Equipment | Procedure | Pass Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **TC-C1** | **Clock Generation Verification** | 100 MHz+ Oscilloscope with 10x probe | Probe crystal oscillator pins for Y1, Y2, and Y3. | Stable 12.000 MHz sinusoidal oscillation with amplitude $> 0.8\text{ V}_{\text{p-p}}$. |
| **TC-C2** | **SWD Firmware Flashing** | Raspberry Pi Debug Probe / J-Link | Connect SWD header `J3`. Flash base firmware UF2 image to RP2040. | Flash write verifies successfully; MCU boots; LED1 (Heartbeat) toggles. |
| **TC-C3** | **EEPROM Configuration** | FTDI FT_PROG utility or MCU I2C writer | Program U4 and U5 EEPROMs with FT245 FIFO mode, custom descriptors ("PC Data Bridge A" / "PC Data Bridge B"). | EEPROMs programmed and verified; FTDI re-enumerates in FT245 mode. |
| **TC-C4** | **I2C Sensor Communication** | Firmware console / Logic Analyzer | Query INA219 sensors at address `0x40` and `0x41` over I2C bus. | Sensors return valid manufacturer IDs (`0x5449`) and accurate bus voltages. |

---

### Stage D: USB High-Speed Data Relay Validation
*Objective: Verify USB device enumeration, signal integrity, and sustained data throughput.*

| Test ID | Test Item | Required Equipment | Procedure | Pass Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **TC-D1** | **High-Speed Enumeration** | Test PC running USBView / Wireshark USBPcap | Plug Port A into PC. Observe device descriptor and speed negotiation. | Enumerates as USB 2.0 High-Speed (480 Mbps) Bulk Device with VID 0x0403. |
| **TC-D2** | **Signal Eye Diagram** | 1 GHz+ Digital Storage Oscilloscope | Run USB-IF High-Speed Compliance Pattern (Test_Packet). Measure eye mask on D+/D-. | Eye pattern fits comfortably within standard USB 2.0 template; jitter $< 50\text{ ps}$. |
| **TC-D3** | **Loopback & Relay Throughput** | Test Bench PC running benchmark utility | Stream 100 MB of random pseudorandom payload through Port A to RP2040 ring buffer and back. | Sustained transfer rate $\ge 30\text{ MB/s}$ with zero CRC errors or dropped packets. |
| **TC-D4** | **FIFO Handshake Timing** | 16-channel Logic Analyzer | Monitor `RXF#`, `TXE#`, `RD#`, `WR#` strobes during maximum rate burst. | No setup/hold violations; strobes respect FTDI 30 ns / 50 ns timing specs. |

---

### Stage E: Power Safety & Interlock Bench Testing
*Objective: Verify electrical safety under fault conditions using bench instruments.*

| Test ID | Test Item | Required Equipment | Procedure | Pass Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **TC-E1** | **Reverse Current Stress Test** | Dual Bench Supplies, DMM in µA mode | Apply 5.25V to Port A. Apply 0.0V (grounded) to Port B. Measure current back-fed into Port B. | Back-feed current $< 5\ \mu\text{A}$ (diode reverse leakage only). Zero dangerous cross-feed. |
| **TC-E2** | **Overcurrent Fault Interlock** | Programmable DC Electronic Load | Draw increasing current from board 3.3V rail. | INA219 trips overcurrent alarm at 500 mA; firmware asserts FAULT LED; LDO current-limits safely. |
| **TC-E3** | **Unsupported Mode Command Rejection** | Serial Terminal / Protocol Script | Send packet requesting `CMD_SET_POWER_MODE` (requesting PC A to charge PC B). | Firmware immediately returns `ERR_UNSUPPORTED_HARDWARE` (0x81); isolation switches remain hardwired OFF. |

---

### Stage F: Host Computer Integration (Dual PC Live Test)
*Objective: Validate live operation between two independent computers.*

| Test ID | Test Item | Required Equipment | Procedure | Pass Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **TC-F1** | **Independent Dual Hot-Plug** | PC A (Laptop) and PC B (Desktop) | Connect Port A to PC A. Wait 5s. Connect Port B to PC B. Disconnect PC A. Reconnect PC A. | Both hosts detect smooth, glitch-free enumeration. Board remains powered continuously. Zero system crashes. |
| **TC-F2** | **Bidirectional File Transfer** | PC A and PC B running protocol validation software | Transfer a 1 GB ISO file from PC A to PC B, then concurrently transfer a 1 GB file from PC B to PC A. | File SHA-256 hashes match identically; sustained transfer rate $> 25\text{ MB/s}$ full duplex; zero dropped bytes. |
