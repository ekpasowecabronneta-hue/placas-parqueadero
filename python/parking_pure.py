"""Implementacion Python del nucleo (fallback si no hay DLL/SWIG)."""

from __future__ import annotations

NUM_CELLS = 10


class PurePythonParking:
    def __init__(self) -> None:
        self._cells: list[dict] = [
            {"plate": "", "occupied": False} for _ in range(NUM_CELLS)
        ]

    def available_count(self) -> int:
        return sum(1 for c in self._cells if not c["occupied"])

    def occupied_count(self) -> int:
        return NUM_CELLS - self.available_count()

    def get_num_cells(self) -> int:
        return NUM_CELLS

    def get_cell_occupied(self, cell: int) -> bool:
        return self._cells[cell]["occupied"]

    def get_cell_plate(self, cell: int) -> str:
        return self._cells[cell]["plate"]

    def _find_by_plate(self, plate: str) -> int:
        for i, c in enumerate(self._cells):
            if c["occupied"] and c["plate"] == plate:
                return i
        return -1

    def _find_free(self) -> int:
        for i, c in enumerate(self._cells):
            if not c["occupied"]:
                return i
        return -1

    def process_line(self, line: str) -> dict | None:
        parts = line.strip().split("|")
        if len(parts) != 4:
            return None
        plate, timestamp, cell_s, action = parts
        event = self._apply(plate, timestamp)
        if event is None:
            return None
        return event

    def _apply(self, plate: str, timestamp: str) -> dict | None:
        existing = self._find_by_plate(plate)
        if existing >= 0:
            self._cells[existing]["occupied"] = False
            self._cells[existing]["plate"] = ""
            return {
                "plate": plate,
                "timestamp": timestamp,
                "cell": existing,
                "action": "RELEASE",
            }
        cell = self._find_free()
        if cell < 0:
            return None
        self._cells[cell]["occupied"] = True
        self._cells[cell]["plate"] = plate
        return {
            "plate": plate,
            "timestamp": timestamp,
            "cell": cell,
            "action": "OCCUPY",
        }
