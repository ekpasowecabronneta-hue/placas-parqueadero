# Especificacion del proyecto

## Componentes

1. **Generador (C++)** — proceso cliente que envia placas cada 2 o 5 segundos por socket.
2. **Servidor (C++)** — proceso servidor que recibe eventos y los reenvia a visualizadores.
3. **Visualizador (Python + Streamlit)** — consume la libreria dinamica (SWIG) y muestra ocupacion.

## Mensaje

Cada evento incluye **hora**, **placa** y **celda**. Si la placa se repite, se **libera** la celda.

Ver [protocolo.md](protocolo.md).

## Rúbrica

| Criterio | Implementacion |
|----------|----------------|
| Funcionalidad | `parking_core`, generador, liberacion por placa repetida |
| Comunicacion entre PCs | Servidor `INADDR_ANY`, host configurable en Streamlit |
| SWIG | `swig/parking.i` + modulo `parking` |
| GUI | `python/app.py` (Streamlit) |
| Git, docs, UML | Ramas, README, `docs/uml/` |
