#include "ft245_bus.h"
#include "bridge_config.h"

#ifdef PICO_BOARD
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#else
/* Host simulation / test harness stubs */
static uint8_t mock_gpio_levels[32] = {0};
static uint8_t mock_gpio_dirs[32] = {0};
#define gpio_init(pin) (void)(pin)
#define gpio_set_dir(pin, dir) (mock_gpio_dirs[pin] = (dir))
#define gpio_put(pin, val) (mock_gpio_levels[pin] = (val))
#define gpio_get(pin) (mock_gpio_levels[pin])
#define gpio_pull_up(pin) (void)(pin)
#define GPIO_IN 0
#define GPIO_OUT 1
#endif

void ft245_bus_init(void) {
    /* Initialize Port A Control Pins */
    gpio_init(PIN_FIFO_A_RXF_N);
    gpio_set_dir(PIN_FIFO_A_RXF_N, GPIO_IN);
    gpio_pull_up(PIN_FIFO_A_RXF_N);

    gpio_init(PIN_FIFO_A_TXE_N);
    gpio_set_dir(PIN_FIFO_A_TXE_N, GPIO_IN);
    gpio_pull_up(PIN_FIFO_A_TXE_N);

    gpio_init(PIN_FIFO_A_RD_N);
    gpio_set_dir(PIN_FIFO_A_RD_N, GPIO_OUT);
    gpio_put(PIN_FIFO_A_RD_N, 1); /* Deasserted HIGH */

    gpio_init(PIN_FIFO_A_WR_N);
    gpio_set_dir(PIN_FIFO_A_WR_N, GPIO_OUT);
    gpio_put(PIN_FIFO_A_WR_N, 1); /* Deasserted HIGH */

    /* Initialize Port A Data Bus (Default: Input) */
    for (int pin = PIN_FIFO_A_D0; pin <= PIN_FIFO_A_D7; pin++) {
        gpio_init(pin);
        gpio_set_dir(pin, GPIO_IN);
    }

    /* Initialize Port B Control Pins */
    gpio_init(PIN_FIFO_B_RXF_N);
    gpio_set_dir(PIN_FIFO_B_RXF_N, GPIO_IN);
    gpio_pull_up(PIN_FIFO_B_RXF_N);

    gpio_init(PIN_FIFO_B_TXE_N);
    gpio_set_dir(PIN_FIFO_B_TXE_N, GPIO_IN);
    gpio_pull_up(PIN_FIFO_B_TXE_N);

    gpio_init(PIN_FIFO_B_RD_N);
    gpio_set_dir(PIN_FIFO_B_RD_N, GPIO_OUT);
    gpio_put(PIN_FIFO_B_RD_N, 1); /* Deasserted HIGH */

    gpio_init(PIN_FIFO_B_WR_N);
    gpio_set_dir(PIN_FIFO_B_WR_N, GPIO_OUT);
    gpio_put(PIN_FIFO_B_WR_N, 1); /* Deasserted HIGH */

    /* Initialize Port B Data Bus (Default: Input) */
    for (int pin = PIN_FIFO_B_D0; pin <= PIN_FIFO_B_D7; pin++) {
        gpio_init(pin);
        gpio_set_dir(pin, GPIO_IN);
    }
}

bool ft245_rx_ready(bridge_port_t port) {
    if (port == PORT_A) {
        return (gpio_get(PIN_FIFO_A_RXF_N) == 0);
    } else {
        return (gpio_get(PIN_FIFO_B_RXF_N) == 0);
    }
}

bool ft245_tx_ready(bridge_port_t port) {
    if (port == PORT_A) {
        return (gpio_get(PIN_FIFO_A_TXE_N) == 0);
    } else {
        return (gpio_get(PIN_FIFO_B_TXE_N) == 0);
    }
}

uint8_t ft245_read_byte(bridge_port_t port) {
    uint8_t data = 0;
    int rd_pin = (port == PORT_A) ? PIN_FIFO_A_RD_N : PIN_FIFO_B_RD_N;
    int base_d_pin = (port == PORT_A) ? PIN_FIFO_A_D0 : PIN_FIFO_B_D0;

    /* Ensure data pins are inputs */
    for (int i = 0; i < 8; i++) {
        gpio_set_dir(base_d_pin + i, GPIO_IN);
    }

    /* Assert RD# active low */
    gpio_put(rd_pin, 0);

    /* Read parallel data bus */
    for (int i = 0; i < 8; i++) {
        if (gpio_get(base_d_pin + i)) {
            data |= (uint8_t)(1 << i);
        }
    }

    /* Deassert RD# high */
    gpio_put(rd_pin, 1);

    return data;
}

void ft245_write_byte(bridge_port_t port, uint8_t byte) {
    int wr_pin = (port == PORT_A) ? PIN_FIFO_A_WR_N : PIN_FIFO_B_WR_N;
    int base_d_pin = (port == PORT_A) ? PIN_FIFO_A_D0 : PIN_FIFO_B_D0;

    /* Set data pins to outputs */
    for (int i = 0; i < 8; i++) {
        gpio_set_dir(base_d_pin + i, GPIO_OUT);
        gpio_put(base_d_pin + i, (byte >> i) & 1);
    }

    /* Assert WR# active low */
    gpio_put(wr_pin, 0);

    /* Deassert WR# high */
    gpio_put(wr_pin, 1);

    /* Return data pins to input */
    for (int i = 0; i < 8; i++) {
        gpio_set_dir(base_d_pin + i, GPIO_IN);
    }
}

size_t ft245_forward_burst(bridge_port_t src, bridge_port_t dst, size_t max_bytes) {
    size_t count = 0;

    while (count < max_bytes && ft245_rx_ready(src) && ft245_tx_ready(dst)) {
        uint8_t b = ft245_read_byte(src);
        ft245_write_byte(dst, b);
        count++;
    }

    return count;
}
