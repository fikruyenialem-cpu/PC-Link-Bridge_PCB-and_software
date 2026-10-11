# Complete Pin Mapping and Netlist Specification

**Project**: Dual USB-A PC-to-PC High-Speed Data Bridge  
**Document**: Pin Mapping Specification  
**Status**: APPROVED

---

## 1. Overview

This document specifies the exact pin-to-net mapping for all integrated circuits, connectors, and control interfaces on the board.

---

## 2. Microcontroller Pin Mapping (`U1`: Raspberry Pi RP2040, QFN-56)

| Pin Number | Pin Name | Net Name | Direction | Function / Description |
| :---: | :---: | :---: | :---: | :--- |
| **2** | GPIO0 | `FIFO_A_D0` | Bidirectional | Port A FT245 Data bit 0 |
| **3** | GPIO1 | `FIFO_A_D1` | Bidirectional | Port A FT245 Data bit 1 |
| **4** | GPIO2 | `FIFO_A_D2` | Bidirectional | Port A FT245 Data bit 2 |
| **5** | GPIO3 | `FIFO_A_D3` | Bidirectional | Port A FT245 Data bit 3 |
| **6** | GPIO4 | `FIFO_A_D4` | Bidirectional | Port A FT245 Data bit 4 |
| **7** | GPIO5 | `FIFO_A_D5` | Bidirectional | Port A FT245 Data bit 5 |
| **8** | GPIO6 | `FIFO_A_D6` | Bidirectional | Port A FT245 Data bit 6 |
| **9** | GPIO7 | `FIFO_A_D7` | Bidirectional | Port A FT245 Data bit 7 |
| **11** | GPIO8 | `FIFO_A_RXF_N` | Input to MCU | Port A Receive FIFO has data (active LOW) |
| **12** | GPIO9 | `FIFO_A_TXE_N` | Input to MCU | Port A Transmit FIFO has space (active LOW) |
| **13** | GPIO10 | `FIFO_A_RD_N` | Output from MCU | Port A Read Strobe (active LOW) |
| **14** | GPIO11 | `FIFO_A_WR_N` | Output from MCU | Port A Write Strobe (active LOW) |
| **15** | GPIO12 | `FIFO_B_D0` | Bidirectional | Port B FT245 Data bit 0 |
| **16** | GPIO13 | `FIFO_B_D1` | Bidirectional | Port B FT245 Data bit 1 |
| **17** | GPIO14 | `FIFO_B_D2` | Bidirectional | Port B FT245 Data bit 2 |
| **18** | GPIO15 | `FIFO_B_D3` | Bidirectional | Port B FT245 Data bit 3 |
| **27** | GPIO16 | `FIFO_B_D4` | Bidirectional | Port B FT245 Data bit 4 |
| **28** | GPIO17 | `FIFO_B_D5` | Bidirectional | Port B FT245 Data bit 5 |
| **29** | GPIO18 | `FIFO_B_D6` | Bidirectional | Port B FT245 Data bit 6 |
| **30** | GPIO19 | `FIFO_B_D7` | Bidirectional | Port B FT245 Data bit 7 |
| **31** | GPIO20 | `FIFO_B_RXF_N` | Input to MCU | Port B Receive FIFO has data (active LOW) |
| **32** | GPIO21 | `FIFO_B_TXE_N` | Input to MCU | Port B Transmit FIFO has space (active LOW) |
| **34** | GPIO22 | `FIFO_B_RD_N` | Output from MCU | Port B Read Strobe (active LOW) |
| **35** | GPIO23 | `FIFO_B_WR_N` | Output from MCU | Port B Write Strobe (active LOW) |
| **36** | GPIO24 | `PWR_ISO_EN_A` | Output from MCU | Port A power interlock gate control (pulled LOW) |
| **37** | GPIO25 | `PWR_ISO_EN_B` | Output from MCU | Port B power interlock gate control (pulled LOW) |
| **38** | GPIO26 | `I2C1_SDA` | Bidirectional | I2C Data to INA219 sensors U8 and U9 |
| **39** | GPIO27 | `I2C1_SCL` | Output from MCU | I2C Clock to INA219 sensors U8 and U9 |
| **40** | GPIO28 | `LED_ACTIVITY` | Output from MCU | High-speed data activity LED (Amber) |
| **41** | GPIO29 | `LED_FAULT` | Output from MCU | Fault / overcurrent alarm LED (Red) |
| **51** | QSPI_SD3 | `FLASH_IO3` | Bidirectional | QSPI NOR Flash Data 3 |
| **52** | QSPI_SCLK | `FLASH_CLK` | Output from MCU | QSPI NOR Flash Clock |
| **53** | QSPI_SD0 | `FLASH_IO0` | Bidirectional | QSPI NOR Flash Data 0 |
| **54** | QSPI_SD2 | `FLASH_IO2` | Bidirectional | QSPI NOR Flash Data 2 |
| **55** | QSPI_SD1 | `FLASH_IO1` | Bidirectional | QSPI NOR Flash Data 1 |
| **56** | QSPI_SS_N | `FLASH_CS_N` | Output from MCU | QSPI NOR Flash Chip Select |
| **24** | SWCLK | `SWD_CLK` | Input to MCU | SWD Clock debug interface |
| **25** | SWDIO | `SWD_DIO` | Bidirectional | SWD Data debug interface |
| **26** | RUN | `MCU_RESET_N` | Input to MCU | MCU Hardware Reset (Active LOW, pulled HIGH) |
| **20** | XIN | `OSC_IN` | Input to MCU | 12.000 MHz Crystal input |
| **21** | XOUT | `OSC_OUT` | Output from MCU | 12.000 MHz Crystal output |
| **44** | VREG_VIN | `+3V3` | Power Input | Input to internal 1.1V Core LDO |
| **45** | VREG_VOUT | `+1V1_CORE` | Power Output | Output from internal 1.1V Core LDO (Decoupled) |
| **1, 10, 22, 33, 42, 49** | IOVDD | `+3V3` | Power Input | I/O Ring Power Supplies (+3.3V) |
| **23, 50** | DVDD | `+1V1_CORE` | Power Input | Digital Core Power Supplies (+1.1V) |
| **57 (EP)** | GND | `GND` | Ground | Thermal and Electrical Ground Pad |

---

## 3. FTDI FT232HL Pin Mapping (`U2` for Port A, `U3` for Port B, LQFP-48)

| Pin Number | Pin Name | Port A Net (`U2`) | Port B Net (`U3`) | Description |
| :---: | :---: | :---: | :---: | :--- |
| **7** | DM | `USB_A_DM` | `USB_B_DM` | USB High-Speed Differential Data Minus |
| **8** | DP | `USB_A_DP` | `USB_B_DP` | USB High-Speed Differential Data Plus |
| **6** | REF | `REF_A` | `REF_B` | PHY Reference Resistor (12.0 kΩ 1% to GND) |
| **40** | VREGIN | `+3V3` | `+3V3` | +3.3V Supply input to internal 1.8V regulator |
| **37** | VCCA | `+3V3_FILT_A` | `+3V3_FILT_B` | Filtered 3.3V Supply to USB Transceiver |
| **38** | VCCCORE | `+1V8_CORE_A` | `+1V8_CORE_B` | +1.8V Internal Core LDO Output (Decoupled with 3.3µF + 100nF) |
| **13** | VCCIO | `+3V3` | `+3V3` | Digital I/O Supply (+3.3V) |
| **1** | OSCI | `XTAL_A_IN` | `XTAL_B_IN` | 12.000 MHz Crystal Oscillator Input |
| **2** | OSCO | `XTAL_A_OUT` | `XTAL_B_OUT` | 12.000 MHz Crystal Oscillator Output |
| **14** | RESET# | `FTDI_A_RST_N` | `FTDI_B_RST_N` | Hardware Reset (pulled HIGH to +3.3V) |
| **16** | ADBUS0 | `FIFO_A_D0` | `FIFO_B_D0` | FT245 Data D0 |
| **17** | ADBUS1 | `FIFO_A_D1` | `FIFO_B_D1` | FT245 Data D1 |
| **18** | ADBUS2 | `FIFO_A_D2` | `FIFO_B_D2` | FT245 Data D2 |
| **19** | ADBUS3 | `FIFO_A_D3` | `FIFO_B_D3` | FT245 Data D3 |
| **20** | ADBUS4 | `FIFO_A_D4` | `FIFO_B_D4` | FT245 Data D4 |
| **21** | ADBUS5 | `FIFO_A_D5` | `FIFO_B_D5` | FT245 Data D5 |
| **22** | ADBUS6 | `FIFO_A_D6` | `FIFO_B_D6` | FT245 Data D6 |
| **23** | ADBUS7 | `FIFO_A_D7` | `FIFO_B_D7` | FT245 Data D7 |
| **24** | ACBUS0 | `FIFO_A_RXF_N` | `FIFO_B_RXF_N` | Receive FIFO Flag (Active LOW) |
| **25** | ACBUS1 | `FIFO_A_TXE_N` | `FIFO_B_TXE_N` | Transmit FIFO Flag (Active LOW) |
| **26** | ACBUS2 | `FIFO_A_RD_N` | `FIFO_B_RD_N` | Read Strobe (Active LOW) |
| **27** | ACBUS3 | `FIFO_A_WR_N` | `FIFO_B_WR_N` | Write Strobe (Active LOW) |
| **43** | EECS | `EECS_A` | `EECS_B` | EEPROM Chip Select |
| **44** | EECLK | `EECLK_A` | `EECLK_B` | EEPROM Clock |
| **45** | EEDATA | `EEDATA_A` | `EEDATA_B` | EEPROM Data In/Out |
| **4, 9, 41** | AGND | `GND` | `GND` | Analog Ground |
| **10, 11, 15, 29, 39** | GND | `GND` | `GND` | Digital Ground |

---

## 4. Power Telemetry Sensor Mapping (`U8`: Port A, `U9`: Port B, SOIC-8)

| Pin Number | Pin Name | Sensor U8 (Port A) | Sensor U9 (Port B) | Description |
| :---: | :---: | :---: | :---: | :--- |
| **1** | IN+ | `VBUS_A_RAW` | `VBUS_B_RAW` | Positive side of current sense shunt |
| **2** | IN- | `VBUS_A_PROT` | `VBUS_B_PROT` | Negative side of current sense shunt |
| **3** | GND | `GND` | `GND` | Ground reference |
| **4** | VS+ | `+3V3` | `+3V3` | Sensor supply power (+3.3V) |
| **5** | SCL | `I2C1_SCL` | `I2C1_SCL` | I2C Clock (common bus) |
| **6** | SDA | `I2C1_SDA` | `I2C1_SDA` | I2C Data (common bus) |
| **7** | A0 | `GND` (Address 0x40) | `+3V3` (Address 0x41) | I2C Address Bit 0 |
| **8** | A1 | `GND` (Address 0x40) | `GND` (Address 0x41) | I2C Address Bit 1 |

---

## 5. External Connectors & Debug Headers

### 5.1 USB-A Connectors (`J1`, `J2`: Amphenol GSB19111KEU)
* **Pin 1**: `VBUS_A` / `VBUS_B` (+5V from Host PC)
* **Pin 2**: `USB_A_DM` / `USB_B_DM` (Differential Data -)
* **Pin 3**: `USB_A_DP` / `USB_B_DP` (Differential Data +)
* **Pin 4**: `GND` (Signal & Power Ground)
* **Shell (5, 6)**: `SHIELD_GND` (Connected to system ground through parallel 1 MΩ resistor and 4.7 nF 2 kV capacitor for ESD dissipation and ground-loop breaking)

### 5.2 SWD Debug Header (`J3`: 1×4 Pin 2.54mm Header)
* **Pin 1**: `+3V3` (Target VCC sense)
* **Pin 2**: `SWD_CLK` (Clock)
* **Pin 3**: `GND` (Ground)
* **Pin 4**: `SWD_DIO` (Bidirectional Data)
