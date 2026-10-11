#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "bridge_config.h"

/* Protocol Framing Constants */
#define PROTOCOL_SYNC_BYTE_0    0xAA
#define PROTOCOL_SYNC_BYTE_1    0x55
#define PROTOCOL_HEADER_LEN     6
#define PROTOCOL_TRAILER_LEN    2

/* Protocol Command Opcodes */
#define CMD_PING                0x01
#define CMD_GET_TELEMETRY       0x02
#define CMD_GET_CAPABILITIES    0x03
#define CMD_SET_POWER_MODE      0x04
#define CMD_DATA_BURST          0x10
#define CMD_DATA_ACK            0x11

/* Protocol Response / Error Codes */
#define RESP_OK                 0x00
#define RESP_ERR_SYNC           0x80
#define RESP_ERR_UNSUPPORTED    0x81    /* Returned for USB-A charging requests */
#define RESP_ERR_OVERCURRENT    0x82
#define RESP_ERR_CRC            0x83
#define RESP_ERR_LEN            0x84

#pragma pack(push, 1)
typedef struct {
    uint8_t  sync[2];       /* 0xAA, 0x55 */
    uint8_t  cmd;           /* Command Opcode */
    uint8_t  flags;         /* Stream / control flags */
    uint16_t length;        /* Payload length in bytes */
} packet_header_t;

typedef struct {
    uint8_t  hw_rev_major;
    uint8_t  hw_rev_minor;
    uint8_t  fw_rev_major;
    uint8_t  fw_rev_minor;
    uint32_t uptime_ms;
} ping_response_payload_t;

typedef struct {
    uint16_t vbus_a_mv;
    int16_t  current_a_ma;
    uint16_t vbus_b_mv;
    int16_t  current_b_ma;
    uint8_t  port_a_connected;
    uint8_t  port_b_connected;
    uint8_t  power_mode;        /* 0 = Isolated */
    uint8_t  fault_status;      /* 0 = OK, 1 = Fault */
} telemetry_response_payload_t;

typedef struct {
    uint8_t  high_speed_supported;      /* 1 = Supported (480 Mbps) */
    uint8_t  bidirectional_supported;   /* 1 = Supported */
    uint8_t  charging_supported;        /* 0 = UNSUPPORTED over USB-A */
    uint8_t  isolation_hardware;        /* 1 = Dedicated Diode-OR & Interlocks */
} capabilities_payload_t;
#pragma pack(pop)

/**
 * Calculate CRC16-CCITT (Polynomial 0x1021, Initial 0xFFFF).
 */
uint16_t protocol_crc16(const uint8_t *data, size_t length);

/**
 * Process an incoming command packet and generate the appropriate response packet.
 */
size_t protocol_process_packet(const uint8_t *rx_buf, size_t rx_len,
                              uint8_t *tx_buf, size_t tx_max);

#endif /* PROTOCOL_H */
