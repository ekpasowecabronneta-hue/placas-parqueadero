#include "socket_platform.h"

int socket_platform_init(void) {
#ifdef _WIN32
    WSADATA wsaData;
    return WSAStartup(MAKEWORD(2, 2), &wsaData) == 0 ? 0 : -1;
#else
    return 0;
#endif
}

void socket_platform_cleanup(void) {
#ifdef _WIN32
    WSACleanup();
#endif
}
