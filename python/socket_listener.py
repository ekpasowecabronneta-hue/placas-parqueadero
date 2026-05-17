"""Background TCP client: receives plate events and updates parking_core via SWIG/ctypes."""

from __future__ import annotations

import socket
import threading
import time
from typing import Callable

from parking_bridge import get_parking


class SocketListener:
    def __init__(
        self,
        host: str,
        port: int,
        on_event: Callable[[dict], None] | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.on_event = on_event
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._connected = False
        self._last_error: str | None = None
        self._parking = get_parking()
        self._lock = threading.Lock()

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def last_error(self) -> str | None:
        return self._last_error

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._connected = False

    def _run(self) -> None:
        while not self._stop.is_set():
            sock = None
            try:
                sock = socket.create_connection((self.host, self.port), timeout=5)
                sock.settimeout(30.0)
                self._connected = True
                self._last_error = None
                buffer = ""
                while not self._stop.is_set():
                    try:
                        chunk = sock.recv(4096)
                    except socket.timeout:
                        continue
                    if not chunk:
                        break
                    buffer += chunk.decode("utf-8", errors="replace")
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if not line:
                            continue
                        event = self._parking.process_line(line)
                        if event and self.on_event:
                            with self._lock:
                                self.on_event(event)
            except OSError as exc:
                self._connected = False
                self._last_error = str(exc)
                time.sleep(2)
            finally:
                self._connected = False
                if sock is not None:
                    try:
                        sock.close()
                    except OSError:
                        pass
