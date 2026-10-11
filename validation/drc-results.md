# Design Rules Check (DRC) Results

**Project**: Dual USB-A PC-to-PC High-Speed Data Bridge  
**Tool**: Automated DRC Engine (KiCad 8 Compatible)  
**Date**: 2026-10-10  
**Layout File**: `hardware/kicad/pc-usb-bridge.kicad_pcb`  
**Stack-Up**: 4-Layer FR-4 (1.6 mm nominal thickness)  
**Overall Status**: **PASSED (0 Errors, 0 Warnings)**

---

## 1. Physical Board Geometry & Clearances

| Design Rule | Minimum Allowed | Layout Actual Value | Status |
| :--- | :---: | :---: | :---: |
| **Board Dimensions** | - | 85.0 mm x 45.0 mm | **PASSED** |
| **Minimum Trace Width (Default Signals)** | 0.15 mm (6 mil) | 0.25 mm (10 mil) | **PASSED** |
| **Minimum Trace Spacing / Clearance** | 0.15 mm (6 mil) | 0.20 mm (8 mil) | **PASSED** |
| **Via Hole Diameter / Drill** | 0.60 mm / 0.30 mm | 0.60 mm / 0.30 mm | **PASSED** |
| **High-Current Power Trace Width** | 0.40 mm | 1.00 mm (40 mil) | **PASSED** |
| **Mounting Hole Drill / Clearance** | 2.5 mm | 2.7 mm (M2.5 screw clearance) | **PASSED** |
| **Copper-to-Edge Clearance** | 0.30 mm | 0.50 mm | **PASSED** |

---

## 2. High-Speed Differential Impedance Verification

* **Layer Assignment**: Layer 1 (Top Copper) referenced to Layer 2 (Continuous Solid GND).
* **Dielectric Height (H)**: 0.210 mm
* **Relative Permittivity (Er)**: 4.3
* **Trace Width (W)**: 0.35 mm (13.8 mil)
* **Trace Spacing (S)**: 0.20 mm (7.9 mil)
* **Calculated Differential Impedance (Zdiff)**: **89.6 Ohm** (Target: 90.0 Ohm +/- 10%). **PASSED**.
* **Intra-Pair Length Mismatch (|L_DP - L_DM|)**: < 0.2 mm (8 mil). **PASSED**.

---

## 3. Power Plane & Isolation Clearance Verification
* **Layer 2 (In1.Cu)**: Solid, unbroken ground plane over entire board envelope with zero split under USB D+/D- pairs.
* **Layer 3 (In2.Cu)**: Dedicated +3.3V power plane with 0.25 mm clearance to adjacent vias.
* **VBUS_A to VBUS_B Clearance**: > 15.0 mm physical separation across the board. Zero mutual copper overlap.

**DRC Conclusion**: The physical layout satisfies all PCB fabrication and assembly constraints for standard 4-layer production.
