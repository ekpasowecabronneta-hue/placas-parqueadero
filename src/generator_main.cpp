#include "parking_core.h"
#include "socket_platform.h"

#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <random>
#include <string>
#include <thread>
#include <vector>

namespace {

void current_timestamp(char* buffer, int size) {
    std::time_t now = std::time(nullptr);
    std::tm tm_local{};
#ifdef _WIN32
    localtime_s(&tm_local, &now);
#else
    localtime_r(&now, &tm_local);
#endif
    std::strftime(buffer, static_cast<size_t>(size), "%Y-%m-%d %H:%M:%S", &tm_local);
}

std::string random_plate(std::mt19937& rng) {
    static const char letters[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    std::uniform_int_distribution<int> letter_dist(0, 25);
    std::uniform_int_distribution<int> digit_dist(0, 9);

    char plate[8];
    plate[0] = letters[letter_dist(rng)];
    plate[1] = letters[letter_dist(rng)];
    plate[2] = letters[letter_dist(rng)];
    plate[3] = static_cast<char>('0' + digit_dist(rng));
    plate[4] = static_cast<char>('0' + digit_dist(rng));
    plate[5] = static_cast<char>('0' + digit_dist(rng));
    plate[6] = '\0';
    return plate;
}

void print_usage(const char* prog) {
    std::fprintf(stderr,
        "Uso: %s <host> <puerto> [intervalo_segundos]\n"
        "  intervalo_segundos: 2 o 5 (default 2)\n",
        prog);
}

}  // namespace

int main(int argc, char* argv[]) {
    if (argc < 3) {
        print_usage(argv[0]);
        return 1;
    }

    const char* host = argv[1];
    int port = std::atoi(argv[2]);
    int interval = (argc >= 4) ? std::atoi(argv[3]) : 2;
    if (interval != 2 && interval != 5) interval = 2;

    if (socket_platform_init() != 0) {
        std::fprintf(stderr, "Error al inicializar sockets\n");
        return 1;
    }

    socket_t sock = ::socket(AF_INET, SOCK_STREAM, 0);
    if (sock == SOCKET_INVALID) {
        std::fprintf(stderr, "Error creando socket cliente\n");
        socket_platform_cleanup();
        return 1;
    }

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(static_cast<uint16_t>(port));
#ifdef _WIN32
    if (InetPtonA(AF_INET, host, &addr.sin_addr) != 1) {
        std::fprintf(stderr, "Host invalido: %s\n", host);
        socket_close(sock);
        socket_platform_cleanup();
        return 1;
    }
#else
    if (inet_pton(AF_INET, host, &addr.sin_addr) <= 0) {
        std::fprintf(stderr, "Host invalido: %s\n", host);
        socket_close(sock);
        socket_platform_cleanup();
        return 1;
    }
#endif

    std::printf("Conectando a %s:%d ...\n", host, port);
    if (::connect(sock, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0) {
        std::fprintf(stderr, "No se pudo conectar al servidor\n");
        socket_close(sock);
        socket_platform_cleanup();
        return 1;
    }

    std::printf("Generador activo (intervalo %d s). Ctrl+C para salir.\n", interval);

    ParkingLot* lot = parking_create();
    std::mt19937 rng(static_cast<unsigned>(
        std::chrono::steady_clock::now().time_since_epoch().count()));

    char timestamp[PARKING_MAX_TIMESTAMP];
    char action[PARKING_MAX_ACTION];
    char line[256];

    std::vector<std::string> recent_plates;

    while (true) {
        std::string plate;
        if (parking_available_count(lot) == 0 && !recent_plates.empty()) {
            plate = recent_plates[rng() % recent_plates.size()];
        } else {
            plate = random_plate(rng);
        }
        current_timestamp(timestamp, sizeof(timestamp));

        int cell = -1;
        int result = parking_process_event(
            lot, plate.c_str(), timestamp, &cell, action, sizeof(action));

        if (result >= 0) {
            if (result == 1) {
                recent_plates.push_back(plate);
                if (recent_plates.size() > 32) {
                    recent_plates.erase(recent_plates.begin());
                }
            }
            parking_format_message(
                plate.c_str(), timestamp, cell, action, line, sizeof(line));

            std::string payload = std::string(line) + "\n";
            send(sock, payload.c_str(), static_cast<int>(payload.size()), 0);
            std::printf("Enviado: %s\n", line);
        } else {
            std::printf("Parqueadero lleno, placa %s descartada\n", plate.c_str());
        }

        std::this_thread::sleep_for(std::chrono::seconds(interval));
    }

    parking_destroy(lot);
    socket_close(sock);
    socket_platform_cleanup();
    return 0;
}
