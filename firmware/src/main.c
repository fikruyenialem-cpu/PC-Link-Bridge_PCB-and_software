#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "bridge_config.h"
#include "ft245_bus.h"
#include "power_monitor.h"
#include "protocol.h"

#ifdef PICO_BOARD
#include "pico/stdlib.h"
#include "hardware/watchdog.h"
#else
#define watchdog_enable(ms, pause) (void)(ms)
#define watchdog_update() ((void)0)
#endif

int main(void) {
    /* 1. Hardware Base Initialization */
#ifdef PICO_BOARD
    stdio_init_all();
#endif

    /* 2. Initialize Hardware Power Monitor & Safety Interlocks */
    power_monitor_init();

    /* 3. Initialize FT245 Parallel FIFO Interfaces */
    ft245_bus_init();

    /* 4. Enable Hardware Watchdog Timer (100 ms) */
    watchdog_enable(WATCHDOG_TIMEOUT_MS, 1);

    /* Buffers for in-band command parsing */
    uint8_t cmd_rx_buf[256];
    uint8_t cmd_tx_buf[256];
    size_t cmd_rx_idx = 0;

    /* Main High-Speed Event Loop */
    while (1) {
        /* Refresh hardware watchdog */
        watchdog_update();

        /* Update power rails and safety monitors */
        power_monitor_update();

        /* Bi-directional High-Speed Data Relay */
        /* Forward Port A -> Port B */
        if (ft245_rx_ready(PORT_A) && ft245_tx_ready(PORT_B)) {
            ft245_forward_burst(PORT_A, PORT_B, 256);
        }

        /* Forward Port B -> Port A */
        if (ft245_rx_ready(PORT_B) && ft245_tx_ready(PORT_A)) {
            ft245_forward_burst(PORT_B, PORT_A, 256);
        }

        /* Check for command packets from host */
        if (ft245_rx_ready(PORT_A)) {
            uint8_t b = ft245_read_byte(PORT_A);
            if (cmd_rx_idx < sizeof(cmd_rx_buf)) {
                cmd_rx_buf[cmd_rx_idx++] = b;
            }
            if (cmd_rx_idx >= (PROTOCOL_HEADER_LEN + PROTOCOL_TRAILER_LEN)) {
                size_t resp_len = protocol_process_packet(cmd_rx_buf, cmd_rx_idx,
                                                         cmd_tx_buf, sizeof(cmd_tx_buf));
                if (resp_len > 0) {
                    for (size_t i = 0; i < resp_len; i++) {
                        if (ft245_tx_ready(PORT_A)) {
                            ft245_write_byte(PORT_A, cmd_tx_buf[i]);
                        }
                    }
                    cmd_rx_idx = 0;
                }
            }
        }
    }

    return 0;
}
