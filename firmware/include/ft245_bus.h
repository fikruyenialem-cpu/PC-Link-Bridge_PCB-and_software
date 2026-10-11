#ifndef FT245_BUS_H
#define FT245_BUS_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef enum {
    PORT_A = 0,
    PORT_B = 1
} bridge_port_t;

/**
 * Initialize GPIOs and direction states for Port A and Port B FT245 buses.
 */
void ft245_bus_init(void);

/**
 * Check if data is available to read from the specified port.
 * Returns true if RXF# is asserted (low).
 */
bool ft245_rx_ready(bridge_port_t port);

/**
 * Check if the specified port's transmit FIFO can accept data.
 * Returns true if TXE# is asserted (low).
 */
bool ft245_tx_ready(bridge_port_t port);

/**
 * Read a single byte from the specified port's FIFO.
 * Asserts RD# low, latches data bus, deasserts RD#.
 */
uint8_t ft245_read_byte(bridge_port_t port);

/**
 * Write a single byte to the specified port's FIFO.
 * Drives data bus, asserts WR# low, deasserts WR#.
 */
void ft245_write_byte(bridge_port_t port, uint8_t byte);

/**
 * Perform high-speed burst transfer of available bytes from source port to destination port.
 * Returns number of bytes forwarded in the burst.
 */
size_t ft245_forward_burst(bridge_port_t src, bridge_port_t dst, size_t max_bytes);

#endif /* FT245_BUS_H */
