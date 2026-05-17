# placas-parqueadero

Simulacion de parqueadero: generador de placas en **C++** (cliente/servidor por sockets) y visualizador en **Python + Streamlit** con libreria dinamica via **SWIG**.

## Arquitectura

```
PC generador                    PC visualizador
parking_server.exe  <--- TCP ---  socket_listener.py
parking_generator.exe           parking (SWIG .pyd)
                                  app.py (Streamlit)
```

## Requisitos

- Windows 10+ (Winsock)
- CMake 3.16+ y Visual Studio (C++) para compilar
- Python 3.10+
- SWIG 4.x (opcional, para modulo `parking`)

## Compilacion

```bat
build.bat
```

Binarios en `build\Release\`:

- `parking_server.exe` — servidor socket
- `parking_generator.exe` — cliente generador
- `parking_core_shared.dll` — libreria para SWIG/ctypes

Modulo SWIG (si CMake detecta SWIG): `build\python\_parking.pyd`

### Compilacion manual (MinGW)

```bat
g++ -std=c++17 -I include -D PARKING_CORE_EXPORTS -shared -o build/parking_core_shared.dll src/parking_core.cpp
g++ -std=c++17 -I include -o build/parking_server.exe src/socket_server.cpp -L build -lparking_core_shared -lws2_32
g++ -std=c++17 -I include -o build/parking_generator.exe src/generator_main.cpp -L build -lparking_core_shared -lws2_32
```

## Ejecucion local

Terminal 1 — servidor:

```bat
build\Release\parking_server.exe 8080
```

Terminal 2 — generador (cada 2 o 5 segundos):

```bat
build\Release\parking_generator.exe 127.0.0.1 8080 2
```

Terminal 3 — visualizador:

```bat
pip install -r python\requirements.txt
streamlit run python\app.py
```

## Protocolo

Mensaje por linea: `PLACA|TIMESTAMP|CELDA|ACCION`

Ver [docs/protocolo.md](docs/protocolo.md).

## Dos PCs

Ver [docs/despliegue-dos-pcs.md](docs/despliegue-dos-pcs.md).

## Estructura

```
include/          parking_core.h, socket_platform.h
src/              nucleo, servidor, generador
swig/             parking.i
python/           Streamlit, socket_listener, parking_bridge
docs/             protocolo, despliegue, UML
specs/            rúbrica y documento del curso
examples/         demos Winsock
```

## UML

- [docs/uml/clases.puml](docs/uml/clases.puml)
- [docs/uml/secuencia.puml](docs/uml/secuencia.puml)

## Ramas Git sugeridas

- `main` — estable
- `feature/core-cpp` — nucleo parking
- `feature/sockets` — servidor y generador
- `feature/swig` — bindings SWIG
- `feature/streamlit` — interfaz

## Rúbrica

| Criterio | Ubicacion |
|----------|-----------|
| Funcionalidad | `src/parking_core.cpp`, generador |
| Comunicacion PCs | `socket_server`, host en Streamlit |
| SWIG | `swig/parking.i`, `build/python/` |
| GUI | `python/app.py` |
| Git, docs, UML | ramas, `docs/`, README |
