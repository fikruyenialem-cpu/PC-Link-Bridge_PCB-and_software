"""
PC Link - Protocol Command Opcodes and Data Models
"""

# Framing bytes
SYNC_BYTE_0 = 0xAA
SYNC_BYTE_1 = 0x55

# Control Commands (Hardware Bridge)
CMD_PING             = 0x01
CMD_GET_TELEMETRY    = 0x02
CMD_GET_CAPABILITIES = 0x03
CMD_SET_POWER_MODE   = 0x04
CMD_DATA_BURST       = 0x10
CMD_DATA_ACK         = 0x11

# File Transfer Protocol Commands (Peer-to-Peer over Bridge)
CMD_FILE_OFFER       = 0x20  # Sender offers file: metadata (name, size, sha256)
CMD_FILE_ACCEPT      = 0x21  # Receiver accepts transfer
CMD_FILE_REJECT      = 0x22  # Receiver rejects transfer
CMD_FILE_CHUNK       = 0x23  # File chunk payload: offset, length, data
CMD_FILE_CHUNK_ACK   = 0x24  # Acknowledge received chunk offset
CMD_FILE_COMPLETE    = 0x25  # Transfer finished and verified
CMD_FILE_CANCEL      = 0x26  # Either party cancels transfer

# Status / Response Codes
RESP_OK              = 0x00
RESP_ERR_SYNC        = 0x80
RESP_ERR_UNSUPPORTED = 0x81
RESP_ERR_OVERCURRENT = 0x82
RESP_ERR_CRC         = 0x83
RESP_ERR_LEN         = 0x84

# Power Transfer Modes
PWR_MODE_ISOLATED    = 0     # Both host power paths isolated (Safe default)
PWR_MODE_A_TO_B      = 1     # PC A -> PC B (Unsupported over USB-A)
PWR_MODE_B_TO_A      = 2     # PC B -> PC A (Unsupported over USB-A)
