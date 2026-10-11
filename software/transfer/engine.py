"""
PC Link - High-Reliability Chunked File Transfer Engine with SHA-256 Verification
"""
import os
import time
import struct
import hashlib
import threading
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from ..protocol.commands import (
    CMD_FILE_OFFER, CMD_FILE_ACCEPT, CMD_FILE_REJECT,
    CMD_FILE_CHUNK, CMD_FILE_CHUNK_ACK, CMD_FILE_COMPLETE, CMD_FILE_CANCEL
)
from ..hardware.bridge_interface import BridgeInterface

class TransferState:
    IDLE = "IDLE"
    OFFERING = "OFFERING"
    SENDING = "SENDING"
    RECEIVING = "RECEIVING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"

class FileTransferEngine:
    def __init__(self, bridge: BridgeInterface, download_dir: str):
        self.bridge = bridge
        self.download_dir = Path(download_dir)
        self.bridge.register_callback(self._on_packet)

        # Active transfer tracking
        self.state = TransferState.IDLE
        self.is_sender = False
        self.current_filename = ""
        self.total_size = 0
        self.transferred_bytes = 0
        self.expected_hash = ""
        self.start_time = 0.0
        self.last_update_time = 0.0
        self.last_bytes = 0
        self.speed_bps = 0.0
        self.eta_seconds = 0.0
        self.active_file_handle = None
        self.part_file_path: Optional[Path] = None
        self.final_file_path: Optional[Path] = None

        self.pause_event = threading.Event()
        self.pause_event.set()  # Unpaused by default
        self.cancel_requested = False
        self.lock = threading.Lock()

        # UI callback hooks
        self.on_progress: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_complete: Optional[Callable[[str, bool, str], None]] = None
        self.on_offer_received: Optional[Callable[[str, int], None]] = None

    def set_download_dir(self, path: str):
        self.download_dir = Path(path)
        os.makedirs(self.download_dir, exist_ok=True)

    def send_file(self, file_path_str: str) -> bool:
        """Initiates sending a file."""
        path = Path(file_path_str)
        if not path.is_file():
            return False

        with self.lock:
            if self.state not in (TransferState.IDLE, TransferState.COMPLETED, TransferState.FAILED, TransferState.CANCELED):
                return False

            self.state = TransferState.OFFERING
            self.is_sender = True
            self.current_filename = path.name
            self.total_size = path.stat().st_size
            self.transferred_bytes = 0
            self.cancel_requested = False
            self.pause_event.set()

        # Compute SHA-256
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        self.expected_hash = sha256.hexdigest()

        # Build offer payload:
        # [name_len: 2B][name: UTF-8][size: 8B][hash_len: 1B][hash: ASCII]
        name_bytes = self.current_filename.encode("utf-8")
        hash_bytes = self.expected_hash.encode("ascii")
        payload = struct.pack(">H", len(name_bytes)) + name_bytes + struct.pack(">Q", self.total_size) + struct.pack(">B", len(hash_bytes)) + hash_bytes

        threading.Thread(target=self._sender_worker, args=(path,), daemon=True).start()
        return self.bridge.send_packet(CMD_FILE_OFFER, payload)

    def pause_transfer(self):
        with self.lock:
            if self.state in (TransferState.SENDING, TransferState.RECEIVING):
                self.pause_event.clear()
                self.state = TransferState.PAUSED
                self._report_progress()

    def resume_transfer(self):
        with self.lock:
            if self.state == TransferState.PAUSED:
                self.pause_event.set()
                self.state = TransferState.SENDING if self.is_sender else TransferState.RECEIVING
                self._report_progress()

    def cancel_transfer(self):
        with self.lock:
            self.cancel_requested = True
            self.pause_event.set()
            self.state = TransferState.CANCELED
            self.bridge.send_packet(CMD_FILE_CANCEL)
            self._cleanup_receive_file()
            self._report_progress()

    def _sender_worker(self, path: Path):
        # Wait for acceptance with timeout
        timeout = 10.0
        start = time.time()
        while self.state == TransferState.OFFERING and (time.time() - start) < timeout:
            time.sleep(0.05)

        if self.state != TransferState.SENDING:
            if self.state == TransferState.OFFERING:
                self.state = TransferState.FAILED
                if self.on_complete:
                    self.on_complete(self.current_filename, False, "Offer timed out (Remote did not respond)")
            return

        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.last_bytes = 0

        chunk_size = 4096
        offset = 0

        try:
            with open(path, "rb") as f:
                while offset < self.total_size:
                    if self.cancel_requested:
                        break

                    self.pause_event.wait()

                    chunk_data = f.read(chunk_size)
                    if not chunk_data:
                        break

                    # Chunk packet: [offset: 8B][len: 2B][data]
                    chunk_payload = struct.pack(">QH", offset, len(chunk_data)) + chunk_data
                    if not self.bridge.send_packet(CMD_FILE_CHUNK, chunk_payload):
                        # Transient failure, wait and retry
                        time.sleep(0.01)
                        continue

                    offset += len(chunk_data)
                    self.transferred_bytes = offset
                    self._update_speed()

            if not self.cancel_requested and offset >= self.total_size:
                # Send complete packet
                self.bridge.send_packet(CMD_FILE_COMPLETE)
                self.state = TransferState.COMPLETED
                if self.on_complete:
                    self.on_complete(self.current_filename, True, "File transfer completed successfully.")
        except Exception as e:
            self.state = TransferState.FAILED
            if self.on_complete:
                self.on_complete(self.current_filename, False, f"Transfer read error: {e}")

    def _on_packet(self, cmd: int, flags: int, payload: bytes):
        if cmd == CMD_FILE_OFFER:
            self._handle_offer(payload)
        elif cmd == CMD_FILE_ACCEPT:
            with self.lock:
                if self.state == TransferState.OFFERING:
                    self.state = TransferState.SENDING
        elif cmd == CMD_FILE_REJECT:
            with self.lock:
                self.state = TransferState.FAILED
                if self.on_complete:
                    self.on_complete(self.current_filename, False, "Remote rejected file offer.")
        elif cmd == CMD_FILE_CHUNK:
            self._handle_chunk(payload)
        elif cmd == CMD_FILE_COMPLETE:
            self._handle_complete()
        elif cmd == CMD_FILE_CANCEL:
            with self.lock:
                self.state = TransferState.CANCELED
                self._cleanup_receive_file()
                if self.on_complete:
                    self.on_complete(self.current_filename, False, "Transfer canceled by peer.")

    def _handle_offer(self, payload: bytes):
        try:
            name_len = struct.unpack_from(">H", payload, 0)[0]
            name = payload[2:2 + name_len].decode("utf-8")
            offset = 2 + name_len
            size = struct.unpack_from(">Q", payload, offset)[0]
            offset += 8
            hash_len = payload[offset]
            expected_hash = payload[offset + 1:offset + 1 + hash_len].decode("ascii")

            with self.lock:
                self.state = TransferState.RECEIVING
                self.is_sender = False
                self.current_filename = name
                self.total_size = size
                self.expected_hash = expected_hash
                self.transferred_bytes = 0
                self.start_time = time.time()
                self.last_update_time = self.start_time
                self.last_bytes = 0

            # Safe destination path resolution (handle collisions)
            dest_dir = self.download_dir
            dest_dir.mkdir(parents=True, exist_ok=True)

            base_name = Path(name).stem
            suffix = Path(name).suffix
            final_path = dest_dir / name
            counter = 1
            while final_path.exists():
                final_path = dest_dir / f"{base_name} ({counter}){suffix}"
                counter += 1

            self.final_file_path = final_path
            self.part_file_path = dest_dir / f"{final_path.name}.part"

            self.active_file_handle = open(self.part_file_path, "wb")
            self.bridge.send_packet(CMD_FILE_ACCEPT)

            if self.on_offer_received:
                self.on_offer_received(name, size)
        except Exception:
            self.bridge.send_packet(CMD_FILE_REJECT)

    def _handle_chunk(self, payload: bytes):
        if self.state != TransferState.RECEIVING or not self.active_file_handle:
            return

        try:
            offset, chunk_len = struct.unpack_from(">QH", payload, 0)
            data = payload[10:10 + chunk_len]

            self.active_file_handle.seek(offset)
            self.active_file_handle.write(data)
            self.transferred_bytes = max(self.transferred_bytes, offset + chunk_len)

            self._update_speed()
            # Send chunk ack
            self.bridge.send_packet(CMD_FILE_CHUNK_ACK, struct.pack(">Q", self.transferred_bytes))
        except Exception as e:
            self.state = TransferState.FAILED
            self._cleanup_receive_file()
            if self.on_complete:
                self.on_complete(self.current_filename, False, f"Write error: {e}")

    def _handle_complete(self):
        if self.state != TransferState.RECEIVING or not self.active_file_handle:
            return

        try:
            self.active_file_handle.close()
            self.active_file_handle = None

            # Verify received file SHA-256
            sha256 = hashlib.sha256()
            with open(self.part_file_path, "rb") as f:
                while chunk := f.read(65536):
                    sha256.update(chunk)
            computed_hash = sha256.hexdigest()

            if computed_hash.lower() == self.expected_hash.lower():
                # Hash match: atomic rename
                if self.final_file_path.exists():
                    self.final_file_path.unlink()
                self.part_file_path.rename(self.final_file_path)
                self.state = TransferState.COMPLETED
                if self.on_complete:
                    self.on_complete(self.current_filename, True, f"Verified and saved to {self.final_file_path.name}")
            else:
                self._cleanup_receive_file()
                self.state = TransferState.FAILED
                if self.on_complete:
                    self.on_complete(self.current_filename, False, "Hash mismatch: Data corrupted in transit.")
        except Exception as e:
            self._cleanup_receive_file()
            self.state = TransferState.FAILED
            if self.on_complete:
                self.on_complete(self.current_filename, False, f"Finalize error: {e}")

    def _cleanup_receive_file(self):
        if self.active_file_handle:
            try:
                self.active_file_handle.close()
            except Exception:
                pass
            self.active_file_handle = None

        if self.part_file_path and self.part_file_path.exists():
            try:
                self.part_file_path.unlink()
            except Exception:
                pass

    def _update_speed(self):
        now = time.time()
        dt = now - self.last_update_time
        if dt >= 0.25:  # Update 4 times per second
            delta_bytes = self.transferred_bytes - self.last_bytes
            self.speed_bps = delta_bytes / dt if dt > 0 else 0.0

            remaining = max(0, self.total_size - self.transferred_bytes)
            self.eta_seconds = (remaining / self.speed_bps) if self.speed_bps > 0 else 0.0

            self.last_update_time = now
            self.last_bytes = self.transferred_bytes
            self._report_progress()

    def _report_progress(self):
        if self.on_progress:
            pct = (self.transferred_bytes / self.total_size * 100) if self.total_size > 0 else 0.0
            data = {
                "state": self.state,
                "filename": self.current_filename,
                "transferred": self.transferred_bytes,
                "total": self.total_size,
                "percent": pct,
                "speed_bps": self.speed_bps,
                "eta_s": self.eta_seconds,
                "is_sender": self.is_sender
            }
            try:
                self.on_progress(data)
            except Exception:
                pass
