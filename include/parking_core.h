#ifndef PARKING_CORE_H
#define PARKING_CORE_H

#define PARKING_NUM_CELLS 10
#define PARKING_MAX_PLATE 16
#define PARKING_MAX_TIMESTAMP 32
#define PARKING_MAX_ACTION 16

#ifdef _WIN32
#  ifdef PARKING_CORE_EXPORTS
#    define PARKING_API __declspec(dllexport)
#  else
#    define PARKING_API __declspec(dllimport)
#  endif
#else
#  define PARKING_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef struct ParkingLot ParkingLot;

PARKING_API ParkingLot* parking_create(void);
PARKING_API void parking_destroy(ParkingLot* lot);

/* Returns 1 on occupy, 0 on release, -1 on error. Fills out_cell and out_action. */
PARKING_API int parking_process_event(
    ParkingLot* lot,
    const char* plate,
    const char* timestamp,
    int* out_cell,
    char* out_action,
    int action_size);

PARKING_API int parking_available_count(const ParkingLot* lot);
PARKING_API int parking_occupied_count(const ParkingLot* lot);
PARKING_API int parking_get_num_cells(void);
PARKING_API int parking_get_cell_occupied(const ParkingLot* lot, int cell);
PARKING_API const char* parking_get_cell_plate(const ParkingLot* lot, int cell);

/* Format: PLACA|TIMESTAMP|CELDA|ACCION */
PARKING_API int parking_format_message(
    const char* plate,
    const char* timestamp,
    int cell,
    const char* action,
    char* buffer,
    int buffer_size);

PARKING_API int parking_parse_message(
    const char* line,
    char* plate,
    int plate_size,
    char* timestamp,
    int timestamp_size,
    int* cell,
    char* action,
    int action_size);

/* Apply OCCUPY/RELEASE on the cell from the wire (visualizer sync). */
PARKING_API int parking_apply_wire(
    ParkingLot* lot,
    const char* plate,
    const char* timestamp,
    int cell,
    const char* action);

#ifdef __cplusplus
}
#endif

#endif
