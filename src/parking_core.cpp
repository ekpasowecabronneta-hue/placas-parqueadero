#include "parking_core.h"

#include <cstring>
#include <cstdio>
#include <algorithm>

struct CellState {
    char plate[PARKING_MAX_PLATE];
    int occupied;
};

struct ParkingLot {
    CellState cells[PARKING_NUM_CELLS];
};

static void copy_str(char* dest, int dest_size, const char* src) {
    if (!dest || dest_size <= 0) return;
    std::snprintf(dest, static_cast<size_t>(dest_size), "%s", src ? src : "");
}

static int find_cell_by_plate(const ParkingLot* lot, const char* plate) {
    for (int i = 0; i < PARKING_NUM_CELLS; ++i) {
        if (lot->cells[i].occupied &&
            std::strcmp(lot->cells[i].plate, plate) == 0) {
            return i;
        }
    }
    return -1;
}

static int find_free_cell(const ParkingLot* lot) {
    for (int i = 0; i < PARKING_NUM_CELLS; ++i) {
        if (!lot->cells[i].occupied) return i;
    }
    return -1;
}

extern "C" {

ParkingLot* parking_create(void) {
    ParkingLot* lot = new ParkingLot();
    for (int i = 0; i < PARKING_NUM_CELLS; ++i) {
        lot->cells[i].plate[0] = '\0';
        lot->cells[i].occupied = 0;
    }
    return lot;
}

void parking_destroy(ParkingLot* lot) {
    delete lot;
}

int parking_process_event(
    ParkingLot* lot,
    const char* plate,
    const char* timestamp,
    int* out_cell,
    char* out_action,
    int action_size) {

    (void)timestamp;
    if (!lot || !plate || !out_cell || !out_action || action_size <= 0) return -1;

    int existing = find_cell_by_plate(lot, plate);
    if (existing >= 0) {
        lot->cells[existing].occupied = 0;
        lot->cells[existing].plate[0] = '\0';
        *out_cell = existing;
        copy_str(out_action, action_size, "RELEASE");
        return 0;
    }

    int cell = find_free_cell(lot);
    if (cell < 0) return -1;

    copy_str(lot->cells[cell].plate, PARKING_MAX_PLATE, plate);
    lot->cells[cell].occupied = 1;
    *out_cell = cell;
    copy_str(out_action, action_size, "OCCUPY");
    return 1;
}

int parking_available_count(const ParkingLot* lot) {
    if (!lot) return 0;
    int n = 0;
    for (int i = 0; i < PARKING_NUM_CELLS; ++i) {
        if (!lot->cells[i].occupied) ++n;
    }
    return n;
}

int parking_occupied_count(const ParkingLot* lot) {
    if (!lot) return 0;
    return PARKING_NUM_CELLS - parking_available_count(lot);
}

int parking_get_num_cells(void) {
    return PARKING_NUM_CELLS;
}

int parking_get_cell_occupied(const ParkingLot* lot, int cell) {
    if (!lot || cell < 0 || cell >= PARKING_NUM_CELLS) return 0;
    return lot->cells[cell].occupied;
}

const char* parking_get_cell_plate(const ParkingLot* lot, int cell) {
    if (!lot || cell < 0 || cell >= PARKING_NUM_CELLS) return "";
    return lot->cells[cell].plate;
}

int parking_format_message(
    const char* plate,
    const char* timestamp,
    int cell,
    const char* action,
    char* buffer,
    int buffer_size) {

    if (!buffer || buffer_size <= 0) return -1;
    return std::snprintf(
        buffer,
        static_cast<size_t>(buffer_size),
        "%s|%s|%d|%s",
        plate ? plate : "",
        timestamp ? timestamp : "",
        cell,
        action ? action : "");
}

int parking_parse_message(
    const char* line,
    char* plate,
    int plate_size,
    char* timestamp,
    int timestamp_size,
    int* cell,
    char* action,
    int action_size) {

    if (!line || !plate || !timestamp || !cell || !action) return -1;

    char local_plate[PARKING_MAX_PLATE];
    char local_ts[PARKING_MAX_TIMESTAMP];
    char local_action[PARKING_MAX_ACTION];
    int local_cell = -1;

    int matched = std::sscanf(
        line,
        "%15[^|]|%31[^|]|%d|%15s",
        local_plate,
        local_ts,
        &local_cell,
        local_action);

    if (matched < 4) return -1;

    copy_str(plate, plate_size, local_plate);
    copy_str(timestamp, timestamp_size, local_ts);
    copy_str(action, action_size, local_action);
    *cell = local_cell;
    return 0;
}

}  // extern "C"
