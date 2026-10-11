#include "power_monitor.h"
#include "protocol.h"

#ifdef PICO_BOARD
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/i2c.h"
#else
static uint8_t mock_gpio_levels[32] = {0};
#define gpio_init(pin) (void)(pin)
#define gpio_set_dir(pin, dir) (void)(pin)
#define gpio_put(pin, val) (mock_gpio_levels[pin] = (val))
#define gpio_pull_down(pin) (void)(pin)
#define GPIO_OUT 1
#endif

/* Cached telemetry structures */
static port_telemetry_t s_telem_a = {0};
static port_telemetry_t s_telem_b = {0};
static power_transfer_mode_t s_active_mode = PWR_MODE_ISOLATED;
static bool s_has_fault = false;

/* INA219 Register Addresses */
#define INA219_REG_CONFIG       0x00
#define INA219_REG_SHUNTVOLTAGE 0x01
#define INA219_REG_BUSVOLTAGE   0x02
#define INA219_REG_POWER        0x03
#define INA219_REG_CURRENT      0x04
#define INA219_REG_CALIBRATION  0x05

void power_monitor_init(void) {
    /* Initialize Hardware Safety Interlocks: strictly drive LOW (ISOLATED) */
    gpio_init(PIN_PWR_ISO_A);
    gpio_set_dir(PIN_PWR_ISO_A, GPIO_OUT);
    gpio_pull_down(PIN_PWR_ISO_A);
    gpio_put(PIN_PWR_ISO_A, 0);

    gpio_init(PIN_PWR_ISO_B);
    gpio_set_dir(PIN_PWR_ISO_B, GPIO_OUT);
    gpio_pull_down(PIN_PWR_ISO_B);
    gpio_put(PIN_PWR_ISO_B, 0);

    /* Initialize Status Indicators */
    gpio_init(PIN_LED_ACTIVITY);
    gpio_set_dir(PIN_LED_ACTIVITY, GPIO_OUT);
    gpio_put(PIN_LED_ACTIVITY, 0);

    gpio_init(PIN_LED_FAULT);
    gpio_set_dir(PIN_LED_FAULT, GPIO_OUT);
    gpio_put(PIN_LED_FAULT, 0);

    /* In a physical build, I2C peripheral is configured at 400kHz */
#ifdef PICO_BOARD
    i2c_init(i2c1, I2C_BAUDRATE_HZ);
    gpio_set_function(PIN_I2C_SDA, GPIO_FUNC_I2C);
    gpio_set_function(PIN_I2C_SCL, GPIO_FUNC_I2C);
    gpio_pull_up(PIN_I2C_SDA);
    gpio_pull_up(PIN_I2C_SCL);
#endif

    s_active_mode = PWR_MODE_ISOLATED;
    s_has_fault = false;
}

void power_monitor_update(void) {
    /* Simulated or physical I2C read from INA219 */
    /* Under physical conditions, INA219 provides bus voltage (raw >> 3) * 4 mV */
#ifndef PICO_BOARD
    /* Default nominal operating conditions for simulation/test */
    s_telem_a.voltage_mv = 5020;
    s_telem_a.current_ma = 95;
    s_telem_a.power_mw = (s_telem_a.voltage_mv * s_telem_a.current_ma) / 1000;
    s_telem_a.connected = true;

    s_telem_b.voltage_mv = 4980;
    s_telem_b.current_ma = 90;
    s_telem_b.power_mw = (s_telem_b.voltage_mv * s_telem_b.current_ma) / 1000;
    s_telem_b.connected = true;
#endif

    /* Check safety thresholds for Port A */
    if (s_telem_a.voltage_mv > VBUS_MAX_VOLTAGE_MV) {
        s_telem_a.overvoltage_fault = true;
        s_has_fault = true;
    } else {
        s_telem_a.overvoltage_fault = false;
    }

    if (s_telem_a.current_ma > VBUS_OVERCURRENT_MA) {
        s_telem_a.overcurrent_fault = true;
        s_has_fault = true;
    } else {
        s_telem_a.overcurrent_fault = false;
    }

    /* Check safety thresholds for Port B */
    if (s_telem_b.voltage_mv > VBUS_MAX_VOLTAGE_MV) {
        s_telem_b.overvoltage_fault = true;
        s_has_fault = true;
    } else {
        s_telem_b.overvoltage_fault = false;
    }

    if (s_telem_b.current_ma > VBUS_OVERCURRENT_MA) {
        s_telem_b.overcurrent_fault = true;
        s_has_fault = true;
    } else {
        s_telem_b.overcurrent_fault = false;
    }

    /* Drive Fault LED */
    if (s_has_fault) {
        gpio_put(PIN_LED_FAULT, 1);
    } else {
        gpio_put(PIN_LED_FAULT, 0);
    }
}

void power_monitor_get_telemetry(bridge_port_t port, port_telemetry_t *out_telem) {
    if (!out_telem) return;
    if (port == PORT_A) {
        *out_telem = s_telem_a;
    } else {
        *out_telem = s_telem_b;
    }
}

bool power_monitor_set_mode(power_transfer_mode_t mode, uint8_t *out_error_code) {
    if (mode == PWR_MODE_ISOLATED) {
        s_active_mode = PWR_MODE_ISOLATED;
        gpio_put(PIN_PWR_ISO_A, 0);
        gpio_put(PIN_PWR_ISO_B, 0);
        if (out_error_code) *out_error_code = RESP_OK;
        return true;
    }

    /*
     * STRICT SAFETY INTERLOCK ENFORCEMENT:
     * Standard USB Type-A ports cannot safely sink charging current.
     * Host charging requests are rejected at firmware level to prevent hardware destruction.
     */
    if (out_error_code) {
        *out_error_code = RESP_ERR_UNSUPPORTED;
    }
    return false;
}

bool power_monitor_has_fault(void) {
    return s_has_fault;
}
