"""Background TCP client: receives plate events and updates parking_core via SWIG/ctypes."""

from __future__ import annotations

import json
import queue
import socket
import threading
import time
from pathlib import Path
from typing import Callable

from parking_bridge import get_parking

_DEBUG_LOG = Path(__file__).resolve().parent.parent / "debug-6dd3d8.log"


def _dbg(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    # #region agent log
    try:
        payload = {
            "sessionId": "6dd3d8",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        with _DEBUG_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except OSError:
        pass
    # #endregion


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
        self._event_queue: queue.Queue[dict] = queue.Queue()

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
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def drain_events(self) -> list[dict]:
        drained: list[dict] = []
        while True:
            try:
                drained.append(self._event_queue.get_nowait())
            except queue.Empty:
                break
        if drained:
            _dbg(
                "D",
                "socket_listener.drain_events",
                "events drained for main thread",
                {"count": len(drained)},
            )
        return drained

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
                        if event:
                            # #region agent log
                            _dbg(
                                "F",
                                "socket_listener._run",
                                "wire event applied",
                                {
                                    "thread": threading.current_thread().name,
                                    "plate": event.get("plate"),
                                    "cell": event.get("cell"),
                                    "action": event.get("action"),
                                },
                            )
                            # #endregion
                            self._event_queue.put(event)
                            if self.on_event:
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
