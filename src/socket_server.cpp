#include "parking_core.h"
#include "socket_platform.h"

#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

namespace {

std::mutex g_clients_mutex;
std::vector<socket_t> g_clients;

void add_client(socket_t client) {
    std::lock_guard<std::mutex> lock(g_clients_mutex);
    g_clients.push_back(client);
}

void remove_client(socket_t client) {
    std::lock_guard<std::mutex> lock(g_clients_mutex);
    g_clients.erase(
        std::remove(g_clients.begin(), g_clients.end(), client),
        g_clients.end());
}

void broadcast_line(const std::string& line, socket_t except_sock) {
    std::lock_guard<std::mutex> lock(g_clients_mutex);
    for (socket_t client : g_clients) {
        if (client == except_sock) continue;
        send(client, line.c_str(), static_cast<int>(line.size()), 0);
    }
}

void handle_client(socket_t client_sock) {
    add_client(client_sock);
    std::printf("Cliente conectado\n");

    char buffer[512];
    std::string pending;

    while (true) {
        int received = recv(client_sock, buffer, sizeof(buffer) - 1, 0);
        if (received <= 0) break;

        buffer[received] = '\0';
        pending.append(buffer);

        size_t pos = 0;
        while ((pos = pending.find('\n')) != std::string::npos) {
            std::string line = pending.substr(0, pos);
            pending.erase(0, pos + 1);

            if (line.empty()) continue;

            char plate[PARKING_MAX_PLATE];
            char timestamp[PARKING_MAX_TIMESTAMP];
            char action[PARKING_MAX_ACTION];
            int cell = -1;

            if (parking_parse_message(
                    line.c_str(), plate, sizeof(plate),
                    timestamp, sizeof(timestamp), &cell,
                    action, sizeof(action)) != 0) {
                std::printf("Mensaje invalido: %s\n", line.c_str());
                continue;
            }

            std::string payload = line + "\n";
            broadcast_line(payload, client_sock);
            std::printf("Reenviado: %s -> %zu clientes\n",
                        line.c_str(), g_clients.size());
        }
    }

    remove_client(client_sock);
    socket_close(client_sock);
    std::printf("Cliente desconectado\n");
}

void print_usage(const char* prog) {
    std::fprintf(stderr, "Uso: %s <puerto>\n", prog);
}

}  // namespace

int main(int argc, char* argv[]) {
    if (argc < 2) {
        print_usage(argv[0]);
        return 1;
    }

    int port = std::atoi(argv[1]);

    if (socket_platform_init() != 0) {
        std::fprintf(stderr, "Error al inicializar Winsock/sockets\n");
        return 1;
    }

    socket_t server_sock = ::socket(AF_INET, SOCK_STREAM, 0);
    if (server_sock == SOCKET_INVALID) {
        std::fprintf(stderr, "Error creando socket servidor\n");
        socket_platform_cleanup();
        return 1;
    }

    int opt = 1;
    setsockopt(server_sock, SOL_SOCKET, SO_REUSEADDR,
               reinterpret_cast<const char*>(&opt), sizeof(opt));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(static_cast<uint16_t>(port));

    if (bind(server_sock, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0) {
        std::fprintf(stderr, "Error en bind puerto %d\n", port);
        socket_close(server_sock);
        socket_platform_cleanup();
        return 1;
    }

    if (listen(server_sock, 10) != 0) {
        std::fprintf(stderr, "Error en listen\n");
        socket_close(server_sock);
        socket_platform_cleanup();
        return 1;
    }

    std::printf("Servidor parqueadero escuchando en 0.0.0.0:%d\n", port);
    std::printf("Ejecute el generador: parking_generator.exe <ip> %d [2|5]\n", port);

    while (true) {
        sockaddr_in client_addr{};
#ifdef _WIN32
        int addrlen = sizeof(client_addr);
#else
        socklen_t addrlen = sizeof(client_addr);
#endif
        socket_t client_sock = accept(
            server_sock,
            reinterpret_cast<sockaddr*>(&client_addr),
            &addrlen);

        if (client_sock == SOCKET_INVALID) continue;

        std::thread(handle_client, client_sock).detach();
    }

    socket_close(server_sock);
    socket_platform_cleanup();
    return 0;
}
