"""Streamlit visualizer for parking lot occupancy."""

from __future__ import annotations

import time
from pathlib import Path

import streamlit as st

from parking_bridge import get_parking
from socket_listener import SocketListener

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080


def _init_state() -> None:
    if "events" not in st.session_state:
        st.session_state.events = []
    if "listener" not in st.session_state:
        st.session_state.listener = None
    if "parking" not in st.session_state:
        from parking_bridge import load_parking

        parking, backend = load_parking()
        st.session_state.parking = parking
        st.session_state.backend = backend


def _on_event(event: dict) -> None:
    st.session_state.events.insert(0, event)
    st.session_state.events = st.session_state.events[:50]


def _ensure_listener(host: str, port: int) -> None:
    listener: SocketListener | None = st.session_state.listener
    if listener and listener.connected:
        return
    if listener:
        listener.stop()
    listener = SocketListener(host, port, on_event=_on_event)
    listener.start()
    st.session_state.listener = listener


def _render_grid(parking) -> None:
    cols = st.columns(5)
    num_cells = parking.get_num_cells()
    for i in range(num_cells):
        col = cols[i % 5]
        occupied = parking.get_cell_occupied(i)
        plate = parking.get_cell_plate(i)
        with col:
            if occupied:
                st.error(f"Celda {i + 1}\n{plate}")
            else:
                st.success(f"Celda {i + 1}\nLibre")


def main() -> None:
    st.set_page_config(page_title="Parqueadero", page_icon="P", layout="wide")
    _init_state()
    parking = st.session_state.parking

    st.title("Visualizador de parqueadero")
    backend = getattr(st.session_state, "backend", "unknown")
    st.caption(f"Backend: {backend} | sockets + Streamlit")

    with st.sidebar:
        st.header("Conexion")
        host = st.text_input("Host del servidor", value=DEFAULT_HOST)
        port = st.number_input("Puerto", min_value=1, max_value=65535, value=DEFAULT_PORT)
        interval = st.slider("Intervalo de refresco (s)", 1, 5, 2)

        if st.button("Conectar / Reconectar"):
            _ensure_listener(host, int(port))

        listener: SocketListener | None = st.session_state.listener
        if listener:
            if listener.connected:
                st.success(f"Conectado a {host}:{port}")
            else:
                st.warning("Reconectando...")
                if listener.last_error:
                    st.caption(listener.last_error)
        else:
            st.info("Pulse Conectar para iniciar la escucha.")

        st.divider()
        st.markdown("**Orden de arranque**")
        st.markdown(
            "1. `parking_server.exe <puerto>`\n"
            "2. `parking_generator.exe <ip> <puerto> [2|5]`\n"
            "3. Esta app Streamlit"
        )

    if st.session_state.listener is None:
        _ensure_listener(host, int(port))

    available = parking.available_count()
    occupied = parking.occupied_count()

    m1, m2, m3 = st.columns(3)
    m1.metric("Disponibles", available)
    m2.metric("Ocupados", occupied)
    m3.metric("Total celdas", parking.get_num_cells())

    st.subheader("Estado de celdas")
    _render_grid(parking)

    st.subheader("Historial de eventos")
    if st.session_state.events:
        st.dataframe(st.session_state.events, use_container_width=True)
    else:
        st.info("Esperando eventos del generador...")

    time.sleep(interval)
    st.rerun()


if __name__ == "__main__":
    main()
