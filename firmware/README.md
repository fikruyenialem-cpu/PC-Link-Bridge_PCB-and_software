# Embedded Firmware Architecture and Guide

**Project**: Dual USB-A PC-to-PC High-Speed Data Bridge  
**Target Processor**: Raspberry Pi RP2040 (Dual ARM Cortex-M0+ @ 133 MHz)  
**Status**: MILESTONE 1 VERIFIED

---

## 1. Firmware Overview

The embedded firmware foundation manages the low-level hardware arbitration between the two FTDI FT232HL USB 2.0 High-Speed bridge ICs, reads voltage and current telemetry from dual Texas Instruments INA219 power monitors via I2C, enforces electrical safety interlocks, and handles packet framing for the Windows host application.

### 1.1 Source Tree

```text
firmware/
├── CMakeLists.txt        # Raspberry Pi Pico SDK CMake configuration
├── include/
│   ├── bridge_config.h  # Pin definitions, clock rates, buffer limits, thresholds
│   ├── ft245_bus.h      # Parallel FIFO bus driver interface
│   ├── power_monitor.h  # INA219 I2C telemetry & safety interlock interface
│   └── protocol.h       # Binary packet framing, command set, and CRC16
├── src/
│   ├── main.c           # Main initialization, watchdog, and event loop
│   ├── ft245_bus.c      # Parallel bus implementation with hardware handshakes
│   ├── power_monitor.c  # Telemetry acquisition & safety interlock enforcement
│   └── protocol.c       # Binary packet parser & command handler
└── README.md            # Firmware guide and build documentation
```

---

## 2. Hardware Interfaces & Pin Assignments

* **Port A FIFO (FT232HL #1)**:
  * Data: GPIO0–GPIO7 (`FIFO_A_D0`–`FIFO_A_D7`)
  * Control: GPIO8 (`RXF#`), GPIO9 (`TXE#`), GPIO10 (`RD#`), GPIO11 (`WR#`)
* **Port B FIFO (FT232HL #2)**:
  * Data: GPIO12–GPIO19 (`FIFO_B_D0`–`FIFO_B_D7`)
  * Control: GPIO20 (`RXF#`), GPIO21 (`TXE#`), GPIO22 (`RD#`), GPIO23 (`WR#`)
* **Safety Interlocks**:
  * GPIO24 (`PWR_ISO_A`), GPIO25 (`PWR_ISO_B`) — Hardwired pull-downs, default LOW (ISOLATED).
* **I2C Power Telemetry**:
  * GPIO26 (`SDA`), GPIO27 (`SCL`) on I2C1 @ 400 kHz.
  * U8 (Port A INA219) at Address `0x40`.
  * U9 (Port B INA219) at Address `0x41`.
* **Indicators**:
  * GPIO28 (`LED_ACTIVITY`), GPIO29 (`LED_FAULT`).

---

## 3. Strict Safety Policy: Unsupported Charging Rejection

Standard PC USB Type-A ports are strictly power sources (DFP). They cannot safely sink power to charge batteries.
In accordance with engineering safety requirements:
1. Firmware initial state strictly holds `PWR_ISO_A` and `PWR_ISO_B` low.
2. Any host packet issuing `CMD_SET_POWER_MODE` with modes other than `PWR_MODE_ISOLATED` is rejected immediately with error code `RESP_ERR_UNSUPPORTED` (`0x81`).
3. Power paths remain permanently isolated.

---

## 4. Building and Flashing

### 4.1 Prerequisites
* CMake 3.13 or newer
* GCC ARM Embedded toolchain (`arm-none-eabi-gcc`)
* Raspberry Pi Pico SDK (set via environment variable `PICO_SDK_PATH`)

### 4.2 Build Steps
```bash
cd firmware
mkdir build && cd build
cmake -DPICO_BOARD=pico ..
make -j4
```

### 4.3 Flashing to Hardware
1. Hold down the `BOOTSEL` tactile switch (`SW1`) on the board.
2. Connect the RP2040 SWD debug probe or native USB maintenance interface to a PC.
3. Release `BOOTSEL`. The RP2040 mounts as a mass-storage volume named `RPI-RP2`.
4. Drag and drop `pc_usb_bridge.uf2` into the volume. The board will automatically reboot and start executing.
