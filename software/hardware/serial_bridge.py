"""
PC Link - Physical Serial / FTDI USB Hardware Bridge
"""
import threading
import time
import struct
from typing import Callable, Optional, Dict, Any
import serial
import serial.tools.list_ports
from .bridge_interface import BridgeInterface
from ..protocol.framing import pack_packet, PacketParser
from ..protocol.commands import (
    CMD_GET_TELEMETRY, CMD_GET_CAPABILITIES, CMD_SET_POWER_MODE,
    RESP_OK, RESP_ERR_UNSUPPORTED, PWR_MODE_ISOLATED
)

class SerialHardwareBridge(BridgeInterface):
    def __init__(self, port: str = "AUTO", baud: int = 115200):
        self.port_name = port
        self.baud_rate = baud
        self.serial_conn: Optional[serial.Serial] = None
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.parser = PacketParser()
        self.callbacks = []
        self.lock = threading.Lock()
        self.telemetry = {
            "vbus_a_mv": 0,
            "current_a_ma": 0,
            "vbus_b_mv": 0,
            "current_b_ma": 0,
            "port_a_connected": False,
            "port_b_connected": False,
            "power_mode": PWR_MODE_ISOLATED,
            "fault_status": False,
            "raw_status": "Disconnected"
        }

    def register_callback(self, callback: Callable[[int, int, bytes], None]) -> None:
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def _find_port(self) -> Optional[str]:
        if self.port_name != "AUTO":
            return self.port_name
        ports = serial.tools.list_ports.comports()
        # Look for FTDI device or first available COM port
        for p in ports:
            if "FTDI" in p.description.upper() or "USB" in p.description.upper():
                return p.device
        return ports[0].device if ports else None

    def connect(self) -> bool:
        if self.is_connected():
            return True

        target_port = self._find_port()
        if not target_port:
            return False

        try:
            self.serial_conn = serial.Serial(
                target_port,
                self.baud_rate,
                timeout=0.1,
                write_timeout=0.5
            )
            self.running = True
            self.worker_thread = threading.Thread(target=self._rx_loop, daemon=True)
            self.worker_thread.start()
            self.telemetry["raw_status"] = f"Connected ({target_port})"
            # Query initial telemetry
            self.send_packet(CMD_GET_TELEMETRY)
            return True
        except Exception as e:
            self.telemetry["raw_status"] = f"Error: {e}"
            return False

    def disconnect(self) -> None:
        self.running = False
        if self.serial_conn:
            try:
                self.serial_conn.close()
            except Exception:
                pass
            self.serial_conn = None
        self.telemetry["raw_status"] = "Disconnected"

    def is_connected(self) -> bool:
        return self.serial_conn is not None and self.serial_conn.is_open

    def send_packet(self, cmd: int, payload: bytes = b"", flags: int = 0) -> bool:
        if not self.is_connected():
            return False
        frame = pack_packet(cmd, payload, flags)
        try:
            with self.lock:
                self.serial_conn.write(frame)
                self.serial_conn.flush()
            return True
        except Exception:
            return False

    def get_telemetry(self) -> Dict[str, Any]:
        return dict(self.telemetry)

    def _rx_loop(self):
        while self.running and self.serial_conn and self.serial_conn.is_open:
            try:
                raw = self.serial_conn.read(512)
                if raw:
                    packets = self.parser.feed(raw)
                    for cmd, flags, payload in packets:
                        self._handle_internal_packet(cmd, flags, payload)
                        for cb in self.callbacks:
                            try:
                                cb(cmd, flags, payload)
                            except Exception:
                                pass
                else:
                    time.sleep(0.01)
            except Exception:
                break
        self.disconnect()

    def _handle_internal_packet(self, cmd: int, flags: int, payload: bytes):
        if cmd == RESP_OK and len(payload) >= 10:
            # Telemetry response payload unpacking
            try:
                v_a, c_a, v_b, c_b, p_a, p_b, p_mode, fault = struct.unpack_from(">HhHhBBBB", payload)
                self.telemetry.update({
                    "vbus_a_mv": v_a,
                    "current_a_ma": c_a,
                    "vbus_b_mv": v_b,
                    "current_b_ma": c_b,
                    "port_a_connected": bool(p_a),
                    "port_b_connected": bool(p_b),
                    "power_mode": p_mode,
                    "fault_status": bool(fault),
                    "raw_status": "Active"
                })
            except Exception:
                pass
