"""
PC Link - Virtual Hardware Bridge & Multi-Instance Local Relay
Simulates the RP2040 hardware bridge for development and coordinates two PC Link instances.
"""
import socket
import threading
import time
import struct
from typing import Callable, Optional, Dict, Any
from .bridge_interface import BridgeInterface
from ..protocol.framing import pack_packet, PacketParser
from ..protocol.commands import (
    CMD_PING, CMD_GET_TELEMETRY, CMD_GET_CAPABILITIES, CMD_SET_POWER_MODE,
    RESP_OK, RESP_ERR_UNSUPPORTED, PWR_MODE_ISOLATED
)

SERVER_PORT = 54128

class VirtualHardwareBridge(BridgeInterface):
    """
    Virtual Bridge that emulates the RP2040 dual-FT232HL hardware bridge.
    Connects to or hosts a local loopback relay daemon to enable multi-instance coordination.
    """
    def __init__(self, role: str = "PC A"):
        self.role = role  # "PC A" or "PC B"
        self.is_connected_flag = False
        self.callbacks = []
        self.parser = PacketParser()
        self.sock: Optional[socket.socket] = None
        self.server_sock: Optional[socket.socket] = None
        self.client_sock: Optional[socket.socket] = None
        self.is_server = False
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

        # Telemetry simulating dual INA219 sensors and RP2040 state
        self.telemetry = {
            "vbus_a_mv": 5040,
            "current_a_ma": 95,
            "vbus_b_mv": 4980,
            "current_b_ma": 90,
            "port_a_connected": True,
            "port_b_connected": True,
            "power_mode": PWR_MODE_ISOLATED,
            "fault_status": False,
            "raw_status": "Virtual Bridge Active"
        }

    def register_callback(self, callback: Callable[[int, int, bytes], None]) -> None:
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def connect(self) -> bool:
        if self.is_connected_flag:
            return True

        self.running = True
        # Try to connect as client first (if another PC Link instance is already running)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.connect(("127.0.0.1", SERVER_PORT))
            self.sock = s
            self.is_server = False
            self.is_connected_flag = True
            self.worker_thread = threading.Thread(target=self._client_rx_loop, daemon=True)
            self.worker_thread.start()
            self._update_remote_status(True)
            return True
        except Exception:
            # We are the first instance; start local virtual bridge hub
            pass

        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("127.0.0.1", SERVER_PORT))
            srv.listen(1)
            self.server_sock = srv
            self.is_server = True
            self.is_connected_flag = True
            self.worker_thread = threading.Thread(target=self._server_accept_loop, daemon=True)
            self.worker_thread.start()
            # Initial state: only local port connected
            if self.role == "PC A":
                self.telemetry["port_b_connected"] = False
            else:
                self.telemetry["port_a_connected"] = False
            return True
        except Exception as e:
            self.telemetry["raw_status"] = f"Virtual Bridge Error: {e}"
            return False

    def disconnect(self) -> None:
        self.running = False
        self.is_connected_flag = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None
        if self.client_sock:
            try:
                self.client_sock.close()
            except Exception:
                pass
            self.client_sock = None
        if self.server_sock:
            try:
                self.server_sock.close()
            except Exception:
                pass
            self.server_sock = None

    def is_connected(self) -> bool:
        return self.is_connected_flag

    def send_packet(self, cmd: int, payload: bytes = b"", flags: int = 0) -> bool:
        if not self.is_connected():
            return False

        # 1. Handle hardware control commands locally (simulating the RP2040 MCU)
        if cmd == CMD_PING:
            resp_payload = struct.pack(">BBBB", 1, 0, 1, 0) + struct.pack(">I", int(time.time() * 1000) & 0xFFFFFFFF)
            self._notify_callbacks(RESP_OK, 0, resp_payload)
            return True

        if cmd == CMD_GET_TELEMETRY:
            telem = self.telemetry
            resp_payload = struct.pack(
                ">HhHhBBBB",
                telem["vbus_a_mv"], telem["current_a_ma"],
                telem["vbus_b_mv"], telem["current_b_ma"],
                1 if telem["port_a_connected"] else 0,
                1 if telem["port_b_connected"] else 0,
                telem["power_mode"],
                1 if telem["fault_status"] else 0
            )
            self._notify_callbacks(RESP_OK, 0, resp_payload)
            return True

        if cmd == CMD_GET_CAPABILITIES:
            # 1: High-Speed (480Mbps), 1: Bidirectional, 0: Charging UNSUPPORTED, 1: Hardware Isolation
            resp_payload = struct.pack(">BBBB", 1, 1, 0, 1)
            self._notify_callbacks(RESP_OK, 0, resp_payload)
            return True

        if cmd == CMD_SET_POWER_MODE:
            # Strict safety check: Any mode other than ISOLATED (0) is rejected
            mode = payload[0] if payload else 0
            if mode == PWR_MODE_ISOLATED:
                self.telemetry["power_mode"] = PWR_MODE_ISOLATED
                self._notify_callbacks(RESP_OK, 0, b"")
            else:
                # Firmware error: RESP_ERR_UNSUPPORTED
                self._notify_callbacks(RESP_ERR_UNSUPPORTED, 0, b"")
            return True

        # 2. Peer-to-peer data / file transfer packets are relayed across the virtual bridge link
        frame = pack_packet(cmd, payload, flags)
        try:
            with self.lock:
                target = self.client_sock if self.is_server else self.sock
                if target:
                    target.sendall(frame)
                    return True
        except Exception:
            self._update_remote_status(False)
            return False
        return True

    def get_telemetry(self) -> Dict[str, Any]:
        return dict(self.telemetry)

    def _update_remote_status(self, connected: bool):
        if self.role == "PC A":
            self.telemetry["port_b_connected"] = connected
        else:
            self.telemetry["port_a_connected"] = connected

    def _notify_callbacks(self, cmd: int, flags: int, payload: bytes):
        for cb in self.callbacks:
            try:
                cb(cmd, flags, payload)
            except Exception:
                pass

    def _server_accept_loop(self):
        while self.running and self.server_sock:
            try:
                client, addr = self.server_sock.accept()
                client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.client_sock = client
                self._update_remote_status(True)
                self._rx_stream(client)
            except Exception:
                break
        self._update_remote_status(False)

    def _client_rx_loop(self):
        if self.sock:
            self._rx_stream(self.sock)
        self._update_remote_status(False)

    def _rx_stream(self, sock_obj: socket.socket):
        parser = PacketParser()
        while self.running:
            try:
                data = sock_obj.recv(4096)
                if not data:
                    break
                packets = parser.feed(data)
                for cmd, flags, payload in packets:
                    self._notify_callbacks(cmd, flags, payload)
            except Exception:
                break
        self._update_remote_status(False)
