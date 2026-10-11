#ifndef BRIDGE_CONFIG_H
#define BRIDGE_CONFIG_H

#include <stdint.h>
#include <stdbool.h>

/* Hardware Revision */
#define HW_REV_MAJOR            1
#define HW_REV_MINOR            0
#define FW_VERSION_MAJOR        1
#define FW_VERSION_MINOR        0

/* System Clock and Watchdog */
#define SYS_CLOCK_HZ            133000000UL
#define WATCHDOG_TIMEOUT_MS     100

/* Port A (FT232HL #1) Pin Definitions */
#define PIN_FIFO_A_D0           0
#define PIN_FIFO_A_D1           1
#define PIN_FIFO_A_D2           2
#define PIN_FIFO_A_D3           3
#define PIN_FIFO_A_D4           4
#define PIN_FIFO_A_D5           5
#define PIN_FIFO_A_D6           6
#define PIN_FIFO_A_D7           7
#define PIN_FIFO_A_RXF_N        8
#define PIN_FIFO_A_TXE_N        9
#define PIN_FIFO_A_RD_N         10
#define PIN_FIFO_A_WR_N         11

/* Port B (FT232HL #2) Pin Definitions */
#define PIN_FIFO_B_D0           12
#define PIN_FIFO_B_D1           13
#define PIN_FIFO_B_D2           14
#define PIN_FIFO_B_D3           15
#define PIN_FIFO_B_D4           16
#define PIN_FIFO_B_D5           17
#define PIN_FIFO_B_D6           18
#define PIN_FIFO_B_D7           19
#define PIN_FIFO_B_RXF_N        20
#define PIN_FIFO_B_TXE_N        21
#define PIN_FIFO_B_RD_N         22
#define PIN_FIFO_B_WR_N         23

/* Power and Safety Interlock Pin Definitions */
#define PIN_PWR_ISO_A           24
#define PIN_PWR_ISO_B           25

/* I2C Telemetry Sensor Pins */
#define PIN_I2C_SDA             26
#define PIN_I2C_SCL             27
#define I2C_PORT_ID             1
#define I2C_BAUDRATE_HZ         400000UL
#define INA219_ADDR_PORT_A      0x40
#define INA219_ADDR_PORT_B      0x41

/* Status LED Pins */
#define PIN_LED_ACTIVITY        28
#define PIN_LED_FAULT           29

/* Buffer Sizes */
#define FIFO_RING_BUFFER_SIZE   4096
#define PROTOCOL_MAX_PAYLOAD    4096

/* Safety Thresholds */
#define VBUS_MAX_VOLTAGE_MV     5500
#define VBUS_MIN_VOLTAGE_MV     4400
#define VBUS_OVERCURRENT_MA     1000

#endif /* BRIDGE_CONFIG_H */
