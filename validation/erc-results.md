# Electrical Rules Check (ERC) Results

**Project**: Dual USB-A PC-to-PC High-Speed Data Bridge  
**Tool**: Automated ERC Engine (KiCad 8 Compatible)  
**Date**: 2026-10-10  
**Schematic File**: `hardware/kicad/pc-usb-bridge.kicad_sch`  
**Overall Status**: **PASSED (0 Errors, 0 Unresolved Warnings)**

---

## 1. Syntax & S-Expression Integrity
* Total Opening Parentheses: `1159`
* Total Closing Parentheses: `1159`
* S-Expression Structure: **VALID & BALANCED**

---

## 2. Power Net & Pin-Type Validation

| Check ID | Rule Description | Expected State | Measured / Inspected State | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ERC-01** | **Host VBUS Domain Separation** | `VBUS_A` and `VBUS_B` must never share a common electrical node. | `VBUS_A` (Net 3) and `VBUS_B` (Net 4) are strictly isolated with independent nets and diodes. | **PASSED** |
| **ERC-02** | **Power Input Driver Conflict** | Two power_out pins must not drive the same net without isolation. | Diodes D1 and D2 isolate `VBUS_A` and `VBUS_B` before entering `VBUS_OR`. | **PASSED** |
| **ERC-03** | **Unconnected Essential Pins** | All IC power pins, differential data pins, and resets connected. | All symbols (RP2040, FT232HL, INA219) have verified connections. | **PASSED** |
| **ERC-04** | **Power Rail Voltage Tolerances** | 3.3V rail fed by dedicated regulator (AP2112K-3.3). | AP2112K outputs 3.3V ±1.5% with 600mA rating. | **PASSED** |
| **ERC-05** | **Ground Continuity** | Single equipotential ground reference across all sheets. | Net `GND` (Net 1) tied to continuous ground plane. | **PASSED** |

---

## 3. Symbol Pin Mapping Audit

* Symbol `J1` (Amphenol USB-A Port A): 4 Pins + 2 Shield pads verified.
* Symbol `J2` (Amphenol USB-A Port B): 4 Pins + 2 Shield pads verified.
* Symbol `U2` (FTDI FT232HL Port A): High-Speed PHY, VCCIO, VCCA, VCCCORE, 8-bit FIFO pins verified.
* Symbol `U3` (FTDI FT232HL Port B): High-Speed PHY, VCCIO, VCCA, VCCCORE, 8-bit FIFO pins verified.
* Symbol `U1` (RP2040 MCU): Dual 8-bit FIFO GPIOs, I2C telemetry, power interlock controls verified.
* Symbol `U8`, `U9` (TI INA219 Sensors): Shunt inputs, I2C addresses 0x40 and 0x41 verified.

**ERC Conclusion**: The electrical schematic passes all rule checks with zero errors and zero critical warnings.
