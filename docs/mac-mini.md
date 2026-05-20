# Mac Mini — [juanjosearevalocamargo@100.99.72.63](mailto:juanjosearevalocamargo@100.99.72.63)

## Servidor (Mac Mini)

```bash
ssh juanjosearevalocamargo@100.99.72.63
cd ~/placas-parqueadero
bash scripts/build_mac.sh
bash scripts/run_mac_server.sh 8080 2
```

## Visualizador (tu PC)

```bat
pip install -r python\requirements.txt
python -m streamlit run python\app.py
```

Host por defecto: `100.99.72.63`, puerto `8080`.

## Probar conexion

```bat
python scripts\test_client.py 100.99.72.63 8080
```

## Reiniciar

```bash
ssh juanjosearevalocamargo@100.99.72.63 "bash ~/placas-parqueadero/scripts/run_mac_server.sh 8080 2"
```

## Ver logs en la Mac Mini

Al arrancar con `run_mac_server.sh`, los procesos escriben en:

| Archivo | Contenido |
|---------|-----------|
| `/tmp/parking_server.log` | Conexiones y mensajes **reenviados** a clientes (Streamlit, test_client, etc.) |
| `/tmp/parking_generator.log` | Placas **enviadas** al servidor (`Enviado: ...`) |

### Seguir logs en tiempo real (desde tu PC)

Terminal 1 — servidor (reenvíos):

```bash
ssh juanjosearevalocamargo@100.99.72.63 "tail -f /tmp/parking_server.log"
```

Terminal 2 — generador (envíos):

```bash
ssh juanjosearevalocamargo@100.99.72.63 "tail -f /tmp/parking_generator.log"
```

### Ver últimas líneas (una sola vez)

```bash
ssh juanjosearevalocamargo@100.99.72.63 "tail -20 /tmp/parking_server.log /tmp/parking_generator.log"
```

### Validar intercambio entre dos PCs

1. **Mac Mini (servidor):** en `parking_server.log` debe aparecer `Reenviado: PLACA|... -> N clientes` (N ≥ 1 si Streamlit está conectado).
2. **Tu PC (cliente):** `python scripts\test_client.py 100.99.72.63 8080` o Streamlit con historial de eventos.
3. **Generador:** en `parking_generator.log` debe aparecer `Enviado: PLACA|TIMESTAMP|CELDA|ACCION`.

Ejemplo de línea válida:

```
Reenviado: QWK921|2026-05-19 19:08:51|7|OCCUPY -> 4 clientes
```

Eso confirma que el servidor recibió la placa del generador y la reenvió a los visualizadores conectados por red.

