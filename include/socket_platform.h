#ifndef SOCKET_PLATFORM_H
#define SOCKET_PLATFORM_H

#ifdef _WIN32
#  ifndef WIN32_LEAN_AND_MEAN
#    define WIN32_LEAN_AND_MEAN
#  endif
#  include <winsock2.h>
#  include <ws2tcpip.h>
#  pragma comment(lib, "ws2_32.lib")
  typedef SOCKET socket_t;
#  define SOCKET_INVALID INVALID_SOCKET
#  define socket_close closesocket
#else
#  include <arpa/inet.h>
#  include <netinet/in.h>
#  include <sys/socket.h>
#  include <unistd.h>
  typedef int socket_t;
#  define SOCKET_INVALID (-1)
#  define socket_close close
#endif

int socket_platform_init(void);
void socket_platform_cleanup(void);

#endif
