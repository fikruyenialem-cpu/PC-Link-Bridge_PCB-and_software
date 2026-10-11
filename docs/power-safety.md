# Power Safety, Isolation, and Protection Specification

**Project**: Dual USB-A PC-to-PC High-Speed Data Bridge  
**Document**: Power Safety Specification  
**Status**: APPROVED

---

## 1. Safety Principles and Threat Analysis

Connecting two distinct personal computer systems over a physical link introduces electrical hazards that do not exist with ordinary peripheral connections. Standard PC power supplies operate from independent AC mains phases or wall outlets, potentially creating ground potential differences, voltage offsets, and cross-conduction paths.

### 1.1 Threat Matrix & Hardware Mitigations

| Threat ID | Threat Description | Consequence Without Hardware Protection | Hardware Mitigation Implemented |
| :--- | :--- | :--- | :--- |
| **TH-01** | **Host VBUS Direct Cross-feed** | Voltage delta between PC A (e.g. 5.15V) and PC B (e.g. 4.85V) drives high circulating current into PC B, damaging motherboard power switches or causing power supply latch-up. | **Physical Power Domain Isolation**: `VBUS_A` and `VBUS_B` traces are separated. Diode-OR Schottky network (`D1`, `D2`) provides independent unidirectional feeds into the board LDO with zero cross-conduction. |
| **TH-02** | **Phantom Powering of Unpowered Host** | When PC A is active and PC B is turned OFF, current could flow from A into B, partially energizing B's motherboard rails and damaging PCH/EC chips. | **Reverse Voltage Blocking**: Schottky diodes `D1` and `D2` block reverse leakage (<5 µA at 25°C). Isolation MOSFET switches `Q1/Q2` are hardwired in the OFF state. |
| **TH-03** | **Electrostatic Discharge (ESD)** | Static discharge when plugging USB cables damages sensitive high-speed PHY transceivers or power rails. | **IEC 61000-4-2 Level 4 Clamping**: Low-capacitance (3.5 pF) TVS diode arrays (`D3`, `D4`) positioned at the connector pins clamp ±15 kV air and ±8 kV contact discharges. |
| **TH-04** | **Inrush Current During Hot-Plug** | Large uncharged decoupling capacitors on the board draw excessive peak current (>100 mA·µs) from the host, tripping host port overcurrent protection. | **Inrush Limiting & Decoupling Sizing**: Total input capacitance directly on each host VBUS line is restricted to 4.7 µF (well below the USB 2.0 limit of 10 µF maximum). Ferrite beads (`FB1`, `FB2`) dampen high-frequency current spikes. |
| **TH-05** | **Firmware Crash / Watchdog Timeout** | If firmware hangs, power states could become ambiguous or unmonitored. | **Hardware Fail-Safe Interlock**: The physical isolation of the power domains does not rely on firmware. Hardwired pull-down resistors (`R_PD1`, 100 kΩ) force the power interlock switch permanently OPEN. Firmware cannot override this without physical hardware modification. |
| **TH-06** | **Ground Potential Differences** | PCs connected to different building mains circuits may have slight AC ground potential deltas. | **Low-Impedance Solid Ground Plane**: Continuous Layer 2 copper ground plane provides an equipotential bonding path across the PCB, preventing ground shift between the two bridge transceivers. |

---

## 2. Power Architecture: Option 1 (Preserve USB-A, Safe Isolation)

Option 1 is implemented on the physical PCB design:

```text
PC A [VBUS_A (5V)] ---> [FB1] ---> [D1: PMEG3020EP] ---+
                                                       |---> [VBUS_OR (4.7V)] ---> [U7: AP2112K-3.3] ---> [+3.3V System]
PC B [VBUS_B (5V)] ---> [FB2] ---> [D2: PMEG3020EP] ---+
```

### 2.1 Diode-OR Power Distribution Analysis
1. **Host A Connected, Host B Disconnected**:
   * `VBUS_A` provides ~5.0V. Current flows through `D1` (forward voltage drop ~0.35V).
   * `VBUS_OR` sits at ~4.65V. `U7` regulates this down to clean +3.3V.
   * `D2` has 0V on its anode and 4.65V on its cathode: `D2` is strongly reverse-biased. Zero current reaches `VBUS_B`.
2. **Host B Connected, Host A Disconnected**:
   * Identical behavior: `D2` conducts; `D1` is reverse-biased; zero current reaches `VBUS_A`.
3. **Both Hosts Connected**:
   * If `VBUS_A` (5.10V) > `VBUS_B` (4.90V): `D1` conducts, raising `VBUS_OR` to ~4.75V.
   * `D2` cathode is at 4.75V, anode is at 4.90V: `D2` is either lightly conducting or cut off. Current flows only from the supply with higher potential. Under no circumstances can current flow backwards from `VBUS_OR` into `VBUS_B`, because Schottky diodes only conduct in the forward direction.

### 2.2 Board Power Budget
* **U1 (RP2040 MCU)**: 35 mA @ 3.3V (115 mW)
* **U2 (FT232HL Port A)**: 70 mA @ 3.3V (231 mW)
* **U3 (FT232HL Port B)**: 70 mA @ 3.3V (231 mW)
* **U4, U5, U6 (EEPROMs & Flash)**: 5 mA @ 3.3V (16 mW)
* **U8, U9 (INA219 Monitors)**: 2 mA @ 3.3V (7 mW)
* **Status LEDs**: 8 mA @ 3.3V (26 mW)
* **Total Maximum Board Load**: **190 mA @ 3.3V (627 mW)**.
* Translated to 5V input through LDO: **~195 mA @ 5V**, well below the 500 mA maximum continuous limit for a standard USB 2.0 port.

---

## 3. Evaluation of Option 2 (Revised USB-C Architecture for Approval)

If the user requires genuine host-to-host laptop battery charging, a redesign to USB Type-C is required.

### 3.1 USB-C Power Delivery Architecture Requirements
To safely negotiate and deliver 45W–100W of charging power between two laptops, the design would require:
1. **Connectors**: Replace both USB-A receptacles with 24-pin USB Type-C receptacles (e.g., Amphenol 12401610E4#2A).
2. **USB-PD Controllers**: Two standalone USB-PD 3.0 controllers (e.g., TI TPS25750 or Cypress CCG3).
   * Communicates over CC1/CC2 lines with each laptop's Embedded Controller (EC).
   * Dynamically negotiates Power Data Objects (PDOs): 5V/3A, 9V/3A, 15V/3A, 20V/5A.
3. **Bidirectional Buck-Boost Converter**: Synchronous 4-switch buck-boost controller (e.g., TI BQ25713 or MPS MP2808) with external power MOSFETs.
   * Can step up 5V/20V from Host A to 20V for Host B, or reverse direction dynamically based on user selection.
4. **Thermal & PCB Layer Impact**:
   * Continuous 5A @ 20V (100W) requires minimum 2 oz copper thickness on inner power layers.
   * Requires 6-layer PCB stack-up with dedicated thermal vias and aluminum heatsink enclosure.
   * Estimated BOM cost increase: **+$28.50 per unit**.

**Summary**: While technically feasible, Option 2 represents an entirely different class of product (a high-power USB-PD bridge/charger) rather than a compact USB-A data link. Option 1 remains the approved, robust architecture for the requested USB-A specification.
