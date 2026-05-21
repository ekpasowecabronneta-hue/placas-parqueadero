### Diagrama de Clases del Sistema

```mermaid
classDiagram
    %% Lado del Core en C++ (Librería Dinámica)
    class Celda {
        +int id
        +string placa
        +long timestamp
        +bool ocupada
        +Celda(int id)
        +void ocupar(string placa, long ts)
        +void vaciar()
    }

    class ParkingController {
        -vector~Celda~ celdas
        -int capacidad
        +ParkingController(int n)
        +void procesarEvento(string placa, int celdaId, string accion)
        +vector~Celda~ getEstadoActual()
    }

    %% Componentes de Red (Sockets)
    class SocketServer {
        -int port
        -SOCKET listenSocket
        +void start()
        +void stop()
        -void listenLoop()
    }

    class ParkingGenerator {
        -string serverIp
        -int port
        +void connect()
        +void enviarPlacaAleatoria()
        +string generarPlaca()
    }

    %% Lado de Python (Interfaz y Bridge)
    class ParkingBridge {
        <<interface>>
        +get_celdas_info()
        +update_from_socket(data)
    }

    class StreamlitApp {
        +render_grid()
        +show_statistics()
        +refresh_data()
    }

    %% Relaciones
    ParkingController "1" *-- "many" Celda : contiene
    SocketServer ..> ParkingController : notifica eventos a
    ParkingGenerator ..> SocketServer : envía datos vía TCP (Protocolo: PLACA|TS|CELDA|ACCION)
    ParkingBridge ..> ParkingController : consume vía SWIG (.pyd/.so)
    StreamlitApp ..> ParkingBridge : obtiene datos para visualizar


