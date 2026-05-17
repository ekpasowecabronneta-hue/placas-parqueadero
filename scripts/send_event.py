#!/usr/bin/env python3
import socket
import sys

host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
line = sys.argv[3] if len(sys.argv) > 3 else "TST001|2026-05-18 00:00:00|0|OCCUPY"

s = socket.create_connection((host, port), timeout=5)
s.sendall((line + "\n").encode())
s.close()
print("sent", line)
