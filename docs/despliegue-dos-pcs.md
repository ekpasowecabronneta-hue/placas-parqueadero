# Despliegue en dos PCs

## Roles

| PC | Rol | Programas |
|----|-----|-----------|
| PC A (generador) | Servidor + generador C++ | `parking_server.exe`, `parking_generator.exe` |
| PC B (visualizador) | Interfaz Streamlit | `streamlit run python/app.py` |

## PC A — Servidor y generador

En Mac Mini remoto ver [mac-mini.md](mac-mini.md).

1. Obtener la IP local: `ipconfig` / `ifconfig` (ej. `192.168.1.50` o IP Tailscale).
2. Permitir el puerto **8080** en el firewall de Windows.
3. Compilar: `build.bat`
4. Terminal 1:
   ```
   build\Release\parking_server.exe 8080
   ```
5. Terminal 2:
   ```
   build\Release\parking_generator.exe 127.0.0.1 8080 2
   ```
   Use intervalo `2` o `5` segundos segun la especificacion.

## PC B — Visualizador

1. Clonar el repositorio e instalar dependencias:
   ```
   pip install -r python/requirements.txt
   ```
2. Copiar `parking_core_shared.dll` y el modulo SWIG `_parking.pyd` desde PC A (`build\Release\` y `build\python\`) o compilar localmente.
3. Ejecutar:
   ```
   streamlit run python/app.py
   ```
4. En la barra lateral, configurar **Host** = IP de PC A (ej. `192.168.1.50`) y **Puerto** = `8080`.
5. Pulsar **Conectar / Reconectar**.

## Prueba local (una sola PC)

Tres terminales:

```
build\Release\parking_server.exe 8080
build\Release\parking_generator.exe 127.0.0.1 8080 2
streamlit run python\app.py
```

## Evidencia para sustentacion

- Captura de `ipconfig` en PC A.
- Captura del servidor y generador en ejecucion.
- Captura de Streamlit mostrando celdas ocupadas/libres y metricas.
- Opcional: video corto del flujo completo.

## Solucion de problemas

| Problema | Solucion |
|----------|----------|
| No conecta desde PC B | Verificar firewall, misma red, IP correcta |
| Sin eventos en Streamlit | Confirmar que el generador esta enviando y el servidor reenvia |
| Error al importar parking | Ejecutar `build.bat` y copiar DLL/PYD a `build/python` |
