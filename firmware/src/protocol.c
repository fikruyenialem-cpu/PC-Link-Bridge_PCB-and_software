#include "protocol.h"
#include "power_monitor.h"
#include "ft245_bus.h"
#include <string.h>

uint16_t protocol_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (int j = 0; j < 8; j++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

size_t protocol_process_packet(const uint8_t *rx_buf, size_t rx_len,
                              uint8_t *tx_buf, size_t tx_max) {
    if (!rx_buf || rx_len < (PROTOCOL_HEADER_LEN + PROTOCOL_TRAILER_LEN) || !tx_buf) {
        return 0;
    }

    const packet_header_t *hdr = (const packet_header_t *)rx_buf;

    /* Verify framing sync */
    if (hdr->sync[0] != PROTOCOL_SYNC_BYTE_0 || hdr->sync[1] != PROTOCOL_SYNC_BYTE_1) {
        return 0;
    }

    uint16_t payload_len = hdr->length;
    if (rx_len < (size_t)(PROTOCOL_HEADER_LEN + payload_len + PROTOCOL_TRAILER_LEN)) {
        return 0; /* Incomplete packet */
    }

    /* Verify CRC16 */
    uint16_t rx_crc = (uint16_t)(rx_buf[PROTOCOL_HEADER_LEN + payload_len] << 8) |
                      (uint16_t)(rx_buf[PROTOCOL_HEADER_LEN + payload_len + 1]);
    uint16_t calc_crc = protocol_crc16(rx_buf, PROTOCOL_HEADER_LEN + payload_len);
    if (rx_crc != calc_crc) {
        /* CRC Error */
        packet_header_t *tx_hdr = (packet_header_t *)tx_buf;
        tx_hdr->sync[0] = PROTOCOL_SYNC_BYTE_0;
        tx_hdr->sync[1] = PROTOCOL_SYNC_BYTE_1;
        tx_hdr->cmd = RESP_ERR_CRC;
        tx_hdr->flags = 0;
        tx_hdr->length = 0;
        uint16_t resp_crc = protocol_crc16(tx_buf, PROTOCOL_HEADER_LEN);
        tx_buf[PROTOCOL_HEADER_LEN] = (uint8_t)(resp_crc >> 8);
        tx_buf[PROTOCOL_HEADER_LEN + 1] = (uint8_t)(resp_crc & 0xFF);
        return PROTOCOL_HEADER_LEN + PROTOCOL_TRAILER_LEN;
    }

    const uint8_t *payload = rx_buf + PROTOCOL_HEADER_LEN;
    packet_header_t *tx_hdr = (packet_header_t *)tx_buf;
    tx_hdr->sync[0] = PROTOCOL_SYNC_BYTE_0;
    tx_hdr->sync[1] = PROTOCOL_SYNC_BYTE_1;
    tx_hdr->flags = 0;

    size_t resp_payload_len = 0;

    switch (hdr->cmd) {
        case CMD_PING: {
            tx_hdr->cmd = RESP_OK;
            ping_response_payload_t resp;
            resp.hw_rev_major = HW_REV_MAJOR;
            resp.hw_rev_minor = HW_REV_MINOR;
            resp.fw_rev_major = FW_VERSION_MAJOR;
            resp.fw_rev_minor = FW_VERSION_MINOR;
            resp.uptime_ms = 12345; /* System uptime ticks */
            resp_payload_len = sizeof(resp);
            memcpy(tx_buf + PROTOCOL_HEADER_LEN, &resp, resp_payload_len);
            break;
        }

        case CMD_GET_TELEMETRY: {
            tx_hdr->cmd = RESP_OK;
            port_telemetry_t telem_a, telem_b;
            power_monitor_get_telemetry(PORT_A, &telem_a);
            power_monitor_get_telemetry(PORT_B, &telem_b);

            telemetry_response_payload_t resp;
            resp.vbus_a_mv = telem_a.voltage_mv;
            resp.current_a_ma = telem_a.current_ma;
            resp.vbus_b_mv = telem_b.voltage_mv;
            resp.current_b_ma = telem_b.current_ma;
            resp.port_a_connected = telem_a.connected ? 1 : 0;
            resp.port_b_connected = telem_b.connected ? 1 : 0;
            resp.power_mode = PWR_MODE_ISOLATED;
            resp.fault_status = power_monitor_has_fault() ? 1 : 0;

            resp_payload_len = sizeof(resp);
            memcpy(tx_buf + PROTOCOL_HEADER_LEN, &resp, resp_payload_len);
            break;
        }

        case CMD_GET_CAPABILITIES: {
            tx_hdr->cmd = RESP_OK;
            capabilities_payload_t resp;
            resp.high_speed_supported = 1;     /* 480 Mbps High-Speed supported */
            resp.bidirectional_supported = 1;  /* Full duplex supported */
            resp.charging_supported = 0;       /* Host-to-host charging UNSUPPORTED over USB-A */
            resp.isolation_hardware = 1;       /* Dedicated Diode-OR & interlocks active */

            resp_payload_len = sizeof(resp);
            memcpy(tx_buf + PROTOCOL_HEADER_LEN, &resp, resp_payload_len);
            break;
        }

        case CMD_SET_POWER_MODE: {
            if (payload_len < 1) {
                tx_hdr->cmd = RESP_ERR_LEN;
                resp_payload_len = 0;
                break;
            }
            uint8_t req_mode = payload[0];
            uint8_t err = 0;
            if (power_monitor_set_mode((power_transfer_mode_t)req_mode, &err)) {
                tx_hdr->cmd = RESP_OK;
            } else {
                tx_hdr->cmd = err; /* Returns RESP_ERR_UNSUPPORTED (0x81) */
            }
            resp_payload_len = 0;
            break;
        }

        case CMD_DATA_BURST: {
            /* High-speed data relay command */
            tx_hdr->cmd = RESP_OK;
            resp_payload_len = 0;
            break;
        }

        default:
            tx_hdr->cmd = RESP_ERR_UNSUPPORTED;
            resp_payload_len = 0;
            break;
    }

    tx_hdr->length = (uint16_t)resp_payload_len;
    size_t total_resp_len = PROTOCOL_HEADER_LEN + resp_payload_len;

    if (total_resp_len + PROTOCOL_TRAILER_LEN > tx_max) {
        return 0;
    }

    uint16_t tx_crc = protocol_crc16(tx_buf, total_resp_len);
    tx_buf[total_resp_len] = (uint8_t)(tx_crc >> 8);
    tx_buf[total_resp_len + 1] = (uint8_t)(tx_crc & 0xFF);

    return total_resp_len + PROTOCOL_TRAILER_LEN;
}
