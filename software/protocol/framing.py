"""
PC Link - Protocol Framing, CRC16, and Packet Serialization
"""
import struct
from typing import Tuple, Optional, List
from .commands import SYNC_BYTE_0, SYNC_BYTE_1

def compute_crc16(data: bytes) -> int:
    """
    Computes CRC16-CCITT (Polynomial 0x1021, Initial 0xFFFF)
    Identical to the embedded firmware implementation in protocol.c
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc

def pack_packet(cmd: int, payload: bytes = b"", flags: int = 0) -> bytes:
    """
    Packs a frame:
    [SYNC0: 1B][SYNC1: 1B][CMD: 1B][FLAGS: 1B][LEN: 2B (big-endian)][PAYLOAD: N bytes][CRC16: 2B (big-endian)]
    """
    length = len(payload)
    header = struct.pack(">BBBBH", SYNC_BYTE_0, SYNC_BYTE_1, cmd, flags, length)
    body = header + payload
    crc = compute_crc16(body)
    return body + struct.pack(">H", crc)

class PacketParser:
    """
    Stream parser for extracting validated packets from raw byte streams.
    """
    def __init__(self):
        self.buffer = bytearray()

    def feed(self, data: bytes) -> List[Tuple[int, int, bytes]]:
        """
        Feeds incoming bytes into the parser buffer.
        Returns a list of parsed packets: [(cmd, flags, payload), ...]
        """
        self.buffer.extend(data)
        packets = []

        while len(self.buffer) >= 8:  # Minimum packet size: 2 sync + 1 cmd + 1 flags + 2 len + 2 crc
            # Scan for sync sequence
            sync_idx = -1
            for i in range(len(self.buffer) - 1):
                if self.buffer[i] == SYNC_BYTE_0 and self.buffer[i+1] == SYNC_BYTE_1:
                    sync_idx = i
                    break

            if sync_idx == -1:
                # No sync found; keep only the last byte in case it's SYNC0
                if self.buffer and self.buffer[-1] == SYNC_BYTE_0:
                    self.buffer = self.buffer[-1:]
                else:
                    self.buffer.clear()
                break

            # Discard bytes prior to sync
            if sync_idx > 0:
                del self.buffer[:sync_idx]

            if len(self.buffer) < 6:
                break

            # Extract header
            cmd, flags, payload_len = struct.unpack_from(">BBH", self.buffer, 2)
            total_packet_len = 6 + payload_len + 2

            if len(self.buffer) < total_packet_len:
                # Waiting for complete packet payload
                break

            # Extract full frame
            frame_data = self.buffer[:total_packet_len - 2]
            expected_crc = struct.unpack_from(">H", self.buffer, total_packet_len - 2)[0]
            actual_crc = compute_crc16(bytes(frame_data))

            if actual_crc == expected_crc:
                payload = bytes(self.buffer[6:6 + payload_len])
                packets.append((cmd, flags, payload))
                del self.buffer[:total_packet_len]
            else:
                # Corrupt packet; advance past SYNC to resynchronize
                del self.buffer[:2]

        return packets
