# PCB Layout and High-Speed Routing Specification

**Project**: Dual USB-A PC-to-PC High-Speed Data Bridge  
**Document**: PCB Layout and Routing Notes  
**Status**: APPROVED

---

## 1. PCB Stack-Up and Substrate Definition

The board uses a **4-layer standard FR-4 stack-up** (nominal thickness 1.6 mm, 1 oz outer copper, 0.5 oz inner copper). This stack-up is widely supported by high-yield PCB manufacturers (JLCPCB, PCBWay, Advanced Circuits).

### 1.1 Layer Structure

```text
Layer 1 (Top):     0.035 mm (1.0 oz) Copper  --- High-speed signals, component pads, local routing
Dielectric 1-2:   0.210 mm FR-4 Prepreg (Er = 4.3 @ 1 GHz)
Layer 2 (Inner 1): 0.018 mm (0.5 oz) Copper  --- Solid, unbroken Ground Reference Plane (GND)
Dielectric 2-3:   1.065 mm FR-4 Core (Er = 4.5)
Layer 3 (Inner 2): 0.018 mm (0.5 oz) Copper  --- Power Distribution Plane (+3.3V, +1V1, VBUS)
Dielectric 3-4:   0.210 mm FR-4 Prepreg (Er = 4.3 @ 1 GHz)
Layer 4 (Bottom):  0.035 mm (1.0 oz) Copper  --- Non-critical signal routing & bottom ground pour
```

---

## 2. High-Speed USB 2.0 Differential Pair Routing (480 Mbps)

USB 2.0 High-Speed signaling operates with a rise time of approximately 500 ps. To prevent signal reflections, jitter, and electromagnetic radiation, the differential pairs (`USB_A_DP`/`USB_A_DM` and `USB_B_DP`/`USB_B_DM`) must strictly maintain a **90 Ω ± 10% differential impedance**.

### 2.1 Impedance Geometry Calculation (Edge-Coupled Microstrip)
Using IPC-2141 microstrip equations referenced to the continuous Layer 2 Ground plane:
* **Dielectric Height ($H$)**: $0.210\text{ mm}$ ($8.27\text{ mil}$)
* **Dielectric Constant ($\varepsilon_r$)**: $4.3$
* **Trace Thickness ($T$)**: $0.035\text{ mm}$ ($1.38\text{ mil}$)
* **Trace Width ($W$)**: **$0.35\text{ mm}$** ($13.8\text{ mil}$)
* **Trace Separation ($S$)**: **$0.20\text{ mm}$** ($7.9\text{ mil}$)
* **Calculated Single-Ended Impedance ($Z_0$)**: $54.2\ \Omega$
* **Calculated Differential Impedance ($Z_{\text{diff}}$)**: **$89.6\ \Omega$** (meets the $90\ \Omega \pm 10\%$ specification).

### 2.2 Routing Rules for High-Speed Pairs
1. **Unbroken Reference Plane**: The USB differential traces run entirely on Layer 1 over an unbroken, void-free Layer 2 ground plane. Under no circumstances may a split or slot exist in Layer 2 beneath these traces.
2. **Length Matching / Skew Control**:
   * Intra-pair length mismatch ($|L_{\text{DP}} - L_{\text{DM}}|$) must be **$< 0.5\text{ mm}$** ($20\text{ mil}$).
   * Skew compensation is performed near the connector using small serpentine bumps with bend angles $\ge 135^\circ$.
3. **No Layer Transitions**: USB differential pairs route directly from the connector pins to the FT232HL transceiver pins on Layer 1 without vias.
4. **Spacing to Other Nets (3W Rule)**: Maintain at least $3 \times W$ ($1.05\text{ mm}$) clearance between the USB differential pairs and any adjacent clock, parallel bus, or power nets.

---

## 3. Power Distribution and Trace Sizing

Traces are sized according to **IPC-2152** guidelines for a maximum temperature rise of $\Delta T < 10^\circ\text{C}$ at $25^\circ\text{C}$ ambient.

| Power Net | Maximum Design Current | Minimum Trace Width | Selected Trace Width | Copper Layer | Calculated Temp Rise |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `VBUS_A`, `VBUS_B` | 1.0 A (Peak) | 0.40 mm (16 mil) | **1.00 mm (40 mil)** | Layer 1 / Layer 3 | $< 2.5^\circ\text{C}$ |
| `VBUS_OR` | 0.5 A (Peak) | 0.25 mm (10 mil) | **0.80 mm (32 mil)** | Layer 1 / Layer 3 | $< 1.8^\circ\text{C}$ |
| `+3V3` System Rail | 0.6 A (Continuous) | 0.30 mm (12 mil) | **Layer 3 Copper Pour / 0.8 mm traces** | Layer 3 | $< 1.5^\circ\text{C}$ |
| `+1V1_CORE` (RP2040) | 0.15 A (Continuous) | 0.20 mm (8 mil) | **0.50 mm (20 mil)** | Layer 1 | $< 0.8^\circ\text{C}$ |
| `+1V8_CORE` (FTDI) | 0.10 A (Continuous) | 0.20 mm (8 mil) | **0.50 mm (20 mil)** | Layer 1 | $< 0.5^\circ\text{C}$ |

---

## 4. Component Placement and Layout Strategy

### 4.1 Mechanical Layout and Flow
* **Board Dimensions**: $85.0\text{ mm} \times 45.0\text{ mm}$ rectangular form factor.
* **Connector Positions**:
  * `J1` (USB-A Port A): Placed on the **Left Board Edge**, centered vertically ($Y = 22.5\text{ mm}$).
  * `J2` (USB-A Port B): Placed on the **Right Board Edge**, centered vertically ($Y = 22.5\text{ mm}$).
* **Symmetry**: Symmetrical component arrangement minimizes signal path lengths between the external ports and the central processor:
  * Port A Circuitry (Connector `J1`, ESD `D3`, FT232HL `U2`, EEPROM `U4`, Sensor `U8`) occupies the left third of the board.
  * Central MCU Subsystem (RP2040 `U1`, Flash `U6`, LDO `U7`, SWD `J3`) occupies the center.
  * Port B Circuitry (Connector `J2`, ESD `D4`, FT232HL `U3`, EEPROM `U5`, Sensor `U9`) occupies the right third of the board.

### 4.2 ESD Protection Array Placement
* `D3` and `D4` (USBLC6-2SC6) are placed **immediately adjacent** to the physical pins of `J1` and `J2` ($< 3.0\text{ mm}$ from connector pads).
* Traces from the connector pass directly through the ESD component pads before proceeding to any series components or the IC. No stubs are permitted between the connector pad and the TVS diode pin.

### 4.3 Decoupling Capacitor Placement
* Every power pin of `U1`, `U2`, and `U3` has a dedicated 100 nF high-frequency ceramic capacitor (0603/0402 X7R).
* Decoupling capacitors are placed on the top layer within $1.5\text{ mm}$ of the IC power pins.
* Vias to the Layer 2 ground plane and Layer 3 power plane are placed directly at the capacitor pads (via-in-pad or adjacent via pair) to minimize loop inductance.

### 4.4 Crystal Oscillator Layout (`Y1`, `Y2`, `Y3`)
* All 12.000 MHz crystals and their load capacitors (27 pF) are placed immediately adjacent to their respective IC oscillator pins ($< 4.0\text{ mm}$).
* Guard ground rings surround the oscillator traces on Layer 1.
* No high-speed digital signals are routed on adjacent layers directly beneath the crystals.

---

## 5. Manufacturing Clearances and Design Rules

* **Minimum Trace Width / Space**: $0.15\text{ mm} / 0.15\text{ mm}$ ($6\text{ mil} / 6\text{ mil}$)
* **Minimum Via Diameter / Drill**: $0.60\text{ mm} / 0.30\text{ mm}$ ($24\text{ mil} / 12\text{ mil}$)
* **Solder Mask Web**: Minimum $0.10\text{ mm}$ ($4\text{ mil}$) between adjacent SMD pads
* **Silkscreen Clearance**: Minimum $0.15\text{ mm}$ from exposed copper pads
* **Mounting Holes**: 4× M2.5 non-plated mounting holes ($2.7\text{ mm}$ drill, $5.0\text{ mm}$ clearance circle) located at the four corners of the board ($4.0\text{ mm}$ inset from edges).
