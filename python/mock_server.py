"""Servidor de prueba en Python (sin compilar C++) para validar Streamlit."""

from __future__ import annotations

import random
import socket
import string
import threading
import time
from datetime import datetime

from parking_pure import PurePythonParking

HOST = "0.0.0.0"
PORT = 8080
INTERVAL = 2

clients: list[socket.socket] = []
clients_lock = threading.Lock()
lot = PurePythonParking()


def broadcast(line: str) -> None:
    payload = (line + "\n").encode("utf-8")
    with clients_lock:
        dead = []
        for c in clients:
            try:
                c.sendall(payload)
            except OSError:
                dead.append(c)
        for d in dead:
            clients.remove(d)


def handle_client(conn: socket.socket) -> None:
    with clients_lock:
        clients.append(conn)
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
    except OSError:
        pass
    finally:
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()


def generator_loop() -> None:
    while True:
        plate = "".join(random.choices(string.ascii_uppercase, k=3)) + "".join(
            random.choices(string.digits, k=3)
        )
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event = lot._apply(plate, ts)
        if event:
            line = f"{event['plate']}|{event['timestamp']}|{event['cell']}|{event['action']}"
            print("Evento:", line)
            broadcast(line)
        time.sleep(INTERVAL)


def main() -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(10)
    print(f"Mock server en {HOST}:{PORT}")
    threading.Thread(target=generator_loop, daemon=True).start()
    while True:
        conn, addr = srv.accept()
        print("Cliente:", addr)
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()
