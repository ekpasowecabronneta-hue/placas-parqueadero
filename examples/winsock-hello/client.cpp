/* Demo original movido desde specs/ - ver specs/client.cpp historico */
#include <iostream>
#include <winsock2.h>
#pragma comment(lib, "ws2_32.lib")
#define PORT 8080
int main() {
    WSADATA wsaData;
    SOCKET sock = INVALID_SOCKET;
    struct sockaddr_in serv_addr;
    char buffer[1024] = {0};
    const char* mensaje = "Hola desde el cliente!";
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) return 1;
    sock = socket(AF_INET, SOCK_STREAM, 0);
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) == SOCKET_ERROR) return 1;
    send(sock, mensaje, (int)strlen(mensaje), 0);
    recv(sock, buffer, 1024, 0);
    closesocket(sock);
    WSACleanup();
    return 0;
}
