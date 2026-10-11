#!/usr/bin/env python3
"""
Automated Test Suite for PC Link Software & Protocol
Verifies:
1. Protocol CRC16 calculation and packet framing/unframing
2. Virtual hardware bridge communication and telemetry responses
3. Safety interlock enforcement (rejection of unsupported charging commands)
4. End-to-end bidirectional file transfer with SHA-256 verification
"""
import os
import sys
import time
import struct
import hashlib
import tempfile
import threading
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from software.protocol.commands import (
    CMD_PING, CMD_GET_TELEMETRY, CMD_GET_CAPABILITIES, CMD_SET_POWER_MODE,
    RESP_OK, RESP_ERR_UNSUPPORTED, PWR_MODE_ISOLATED, PWR_MODE_A_TO_B
)
from software.protocol.framing import compute_crc16, pack_packet, PacketParser
from software.hardware.virtual_bridge import VirtualHardwareBridge
from software.transfer.engine import FileTransferEngine, TransferState

class TestPCLinkProtocol(unittest.TestCase):
    def test_crc16_integrity(self):
        # Known test vectors
        test_data = b"PC_LINK_TEST_12345"
        crc1 = compute_crc16(test_data)
        crc2 = compute_crc16(test_data)
        self.assertEqual(crc1, crc2)
        # Bit flip alters CRC
        self.assertNotEqual(crc1, compute_crc16(b"PC_LINK_TEST_12346"))

    def test_packet_framing_roundtrip(self):
        parser = PacketParser()
        payload = b"Hello, PC B! High-speed link active."
        packet = pack_packet(CMD_PING, payload, flags=0x01)

        parsed = parser.feed(packet)
        self.assertEqual(len(parsed), 1)
        cmd, flags, out_payload = parsed[0]
        self.assertEqual(cmd, CMD_PING)
        self.assertEqual(flags, 0x01)
        self.assertEqual(out_payload, payload)

class TestPCLinkHardwareSafety(unittest.TestCase):
    def test_virtual_bridge_telemetry_and_safety(self):
        bridge = VirtualHardwareBridge(role="PC A")
        self.assertTrue(bridge.connect())

        # Test telemetry
        received_packets = []
        bridge.register_callback(lambda cmd, flags, payload: received_packets.append((cmd, payload)))

        bridge.send_packet(CMD_GET_TELEMETRY)
        time.sleep(0.05)
        self.assertTrue(len(received_packets) >= 1)
        cmd, payload = received_packets[-1]
        self.assertEqual(cmd, RESP_OK)
        self.assertGreaterEqual(len(payload), 10)

        # Test Capabilities
        received_packets.clear()
        bridge.send_packet(CMD_GET_CAPABILITIES)
        time.sleep(0.05)
        self.assertTrue(len(received_packets) >= 1)
        cmd, payload = received_packets[-1]
        self.assertEqual(cmd, RESP_OK)
        # Charging supported must be 0 (UNSUPPORTED)
        hs, bidi, chg, iso = struct.unpack(">BBBB", payload)
        self.assertEqual(hs, 1)
        self.assertEqual(bidi, 1)
        self.assertEqual(chg, 0, "Charging must be reported as UNSUPPORTED over USB-A")
        self.assertEqual(iso, 1)

        # Test Safety Interlock: Attempt to activate PC A -> PC B power transfer
        received_packets.clear()
        bridge.send_packet(CMD_SET_POWER_MODE, bytes([PWR_MODE_A_TO_B]))
        time.sleep(0.05)
        self.assertTrue(len(received_packets) >= 1)
        cmd, _ = received_packets[-1]
        self.assertEqual(
            cmd, RESP_ERR_UNSUPPORTED,
            "Hardware bridge must reject power transfer mode change with RESP_ERR_UNSUPPORTED (0x81)"
        )

        bridge.disconnect()

class TestPCLinkFileTransfer(unittest.TestCase):
    def test_end_to_end_file_transfer(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source_file = tmp_path / "test_data_packet.bin"
            dest_dir = tmp_path / "received"
            dest_dir.mkdir()

            # Create test payload (256 KB of pseudorandom data)
            test_content = os.urandom(256 * 1024)
            source_file.write_bytes(test_content)
            expected_sha256 = hashlib.sha256(test_content).hexdigest()

            # Start Host A (Server) and Host B (Client)
            bridge_a = VirtualHardwareBridge(role="PC A")
            bridge_b = VirtualHardwareBridge(role="PC B")

            self.assertTrue(bridge_a.connect())
            time.sleep(0.1)
            self.assertTrue(bridge_b.connect())
            time.sleep(0.1)

            engine_a = FileTransferEngine(bridge_a, download_dir=str(dest_dir))
            engine_b = FileTransferEngine(bridge_b, download_dir=str(dest_dir))

            completed_event = threading.Event()
            success_result = [False]

            def on_complete(filename, success, msg):
                success_result[0] = success
                completed_event.set()

            engine_b.on_complete = on_complete

            # Send from A to B
            self.assertTrue(engine_a.send_file(str(source_file)))

            # Wait for transfer completion (timeout 10s)
            self.assertTrue(completed_event.wait(timeout=10.0), "File transfer timed out")
            self.assertTrue(success_result[0], "File transfer completed with failure")

            # Verify received file
            received_file = dest_dir / "test_data_packet.bin"
            self.assertTrue(received_file.exists())
            actual_sha256 = hashlib.sha256(received_file.read_bytes()).hexdigest()
            self.assertEqual(expected_sha256, actual_sha256, "SHA-256 hash mismatch")

            bridge_a.disconnect()
            bridge_b.disconnect()

if __name__ == "__main__":
    unittest.main()
