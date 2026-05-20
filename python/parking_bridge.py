"""Bridge to parking_core: prefers SWIG module, falls back to ctypes DLL."""

from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD_DIRS = [
    ROOT / "build" / "python",
    ROOT / "build" / "Release",
    ROOT / "build" / "Debug",
    ROOT / "build",
]


def _find_library() -> Path | None:
    names = ["parking_core_shared.dll", "libparking_core_shared.so", "parking_core_shared.dll"]
    for base in BUILD_DIRS:
        for name in names:
            candidate = base / name
            if candidate.exists():
                return candidate
    return None


class _CtypesParking:
    def __init__(self) -> None:
        lib_path = _find_library()
        if lib_path is None:
            raise FileNotFoundError(
                "No se encontro parking_core_shared. Compile con CMake primero."
            )
        self._lib = ctypes.CDLL(str(lib_path))
        self._lot = self._lib.parking_create()

        self._lib.parking_destroy.argtypes = [ctypes.c_void_p]
        self._lib.parking_create.restype = ctypes.c_void_p
        self._lib.parking_available_count.argtypes = [ctypes.c_void_p]
        self._lib.parking_available_count.restype = ctypes.c_int
        self._lib.parking_occupied_count.argtypes = [ctypes.c_void_p]
        self._lib.parking_occupied_count.restype = ctypes.c_int
        self._lib.parking_get_num_cells.restype = ctypes.c_int
        self._lib.parking_get_cell_occupied.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._lib.parking_get_cell_occupied.restype = ctypes.c_int
        self._lib.parking_get_cell_plate.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._lib.parking_get_cell_plate.restype = ctypes.c_char_p
        self._lib.parking_process_event.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_char_p,
            ctypes.c_int,
        ]
        self._lib.parking_process_event.restype = ctypes.c_int
        self._lib.parking_parse_message.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_char_p,
            ctypes.c_int,
        ]
        self._lib.parking_parse_message.restype = ctypes.c_int
        self._lib.parking_apply_wire.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
        ]
        self._lib.parking_apply_wire.restype = ctypes.c_int

    def available_count(self) -> int:
        return int(self._lib.parking_available_count(self._lot))

    def occupied_count(self) -> int:
        return int(self._lib.parking_occupied_count(self._lot))

    def get_num_cells(self) -> int:
        return int(self._lib.parking_get_num_cells())

    def get_cell_occupied(self, cell: int) -> bool:
        return bool(self._lib.parking_get_cell_occupied(self._lot, cell))

    def get_cell_plate(self, cell: int) -> str:
        raw = self._lib.parking_get_cell_plate(self._lot, cell)
        return raw.decode("utf-8") if raw else ""

    def process_line(self, line: str) -> dict | None:
        plate = ctypes.create_string_buffer(16)
        timestamp = ctypes.create_string_buffer(32)
        action = ctypes.create_string_buffer(16)
        cell = ctypes.c_int(-1)

        if self._lib.parking_parse_message(
            line.encode("utf-8"),
            plate,
            16,
            timestamp,
            32,
            ctypes.byref(cell),
            action,
            16,
        ) != 0:
            return None

        result = self._lib.parking_apply_wire(
            self._lot,
            plate.value,
            timestamp.value,
            int(cell.value),
            action.value,
        )
        if result < 0:
            return None

        return {
            "plate": plate.value.decode("utf-8"),
            "timestamp": timestamp.value.decode("utf-8"),
            "cell": int(cell.value),
            "action": action.value.decode("utf-8"),
        }


class _SwigParking:
    def __init__(self, mod) -> None:
        self._mod = mod
        self._lot = mod.parking_create()

    def available_count(self) -> int:
        return int(self._mod.parking_available_count(self._lot))

    def occupied_count(self) -> int:
        return int(self._mod.parking_occupied_count(self._lot))

    def get_num_cells(self) -> int:
        return int(self._mod.parking_get_num_cells())

    def get_cell_occupied(self, cell: int) -> bool:
        return bool(self._mod.parking_get_cell_occupied(self._lot, cell))

    def get_cell_plate(self, cell: int) -> str:
        return self._mod.parking_get_cell_plate(self._lot, cell) or ""

    def process_line(self, line: str) -> dict | None:
        plate_buf = " " * 16
        ts_buf = " " * 32
        action_buf = " " * 16
        cell = -1

        if self._mod.parking_parse_message(line, plate_buf, 16, ts_buf, 32, cell, action_buf, 16) != 0:
            return None

        wire_cell = cell[0] if isinstance(cell, list) else cell
        wire_action = action_buf.strip("\x00 ").strip()
        plate_s = plate_buf.strip("\x00 ").strip()
        ts_s = ts_buf.strip("\x00 ").strip()

        if hasattr(self._mod, "parking_apply_wire"):
            result = self._mod.parking_apply_wire(
                self._lot, plate_s, ts_s, wire_cell, wire_action
            )
            if result < 0:
                return None
        else:
            return None

        return {
            "plate": plate_s,
            "timestamp": ts_s,
            "cell": wire_cell,
            "action": wire_action,
        }


def load_parking():
    global _singleton, _backend

    if _singleton is not None:
        return _singleton, _backend

    for path in BUILD_DIRS:
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))

    try:
        import parking as swig_mod  # type: ignore

        _singleton, _backend = _SwigParking(swig_mod), "swig"
    except ImportError:
        try:
            _singleton, _backend = _CtypesParking(), "ctypes"
        except (FileNotFoundError, OSError):
            from parking_pure import PurePythonParking

            _singleton, _backend = PurePythonParking(), "python"

    return _singleton, _backend


_singleton = None
_backend = "unknown"


def get_parking():
    if _singleton is None:
        load_parking()
    return _singleton


def get_backend() -> str:
    if _singleton is None:
        load_parking()
    return _backend
