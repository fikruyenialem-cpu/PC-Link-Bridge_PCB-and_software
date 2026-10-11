#ifndef POWER_MONITOR_H
#define POWER_MONITOR_H

#include <stdint.h>
#include <stdbool.h>
#include "bridge_config.h"

typedef struct {
    uint16_t voltage_mv;        /* Bus voltage in millivolts */
    int16_t  current_ma;        /* Current draw in milliamperes (signed) */
    uint32_t power_mw;          /* Calculated power in milliwatts */
    bool     connected;         /* Host connection detected (voltage > 4.0V) */
    bool     overcurrent_fault; /* Current exceeded threshold */
    bool     overvoltage_fault; /* Voltage exceeded threshold */
} port_telemetry_t;

typedef enum {
    PWR_MODE_ISOLATED = 0,      /* Default safe mode: VBUS_A and VBUS_B isolated */
    PWR_MODE_A_TO_B   = 1,      /* Unsupported over USB-A */
    PWR_MODE_B_TO_A   = 2       /* Unsupported over USB-A */
} power_transfer_mode_t;

/**
 * Initialize I2C peripheral and calibrate INA219 sensors U8 and U9.
 * Enforces hardware isolation pull-downs.
 */
void power_monitor_init(void);

/**
 * Update voltage and current measurements from both INA219 sensors.
 */
void power_monitor_update(void);

/**
 * Get cached telemetry for Port A or Port B.
 */
void power_monitor_get_telemetry(bridge_port_t port, port_telemetry_t *out_telem);

/**
 * Request power mode change.
 * STRICT SAFETY POLICY: Returns false for any mode other than PWR_MODE_ISOLATED.
 * Unsupported modes are strictly rejected to protect host hardware.
 */
bool power_monitor_set_mode(power_transfer_mode_t mode, uint8_t *out_error_code);

/**
 * Check if any electrical fault condition is currently active.
 */
bool power_monitor_has_fault(void);

#endif /* POWER_MONITOR_H */
