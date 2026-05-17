# VPS capadonna@100.97.151.69

## Despliegue actual

Servicios en el VPS (Ubuntu, Tailscale `100.97.151.69`):

```bash
cd ~/placas-parqueadero
bash scripts/deploy_vps.sh      # compilar
bash scripts/run_vps_server.sh 8080 2   # servidor + generador
```

## Desde tu PC (visualizador)

```bat
pip install -r python\requirements.txt
streamlit run python\app.py
```

En la barra lateral: **Host** = `100.97.151.69`, **Puerto** = `8080`.

## Probar conexion rapida

```bat
python scripts\test_client.py 100.97.151.69 8080
```

## Reiniciar servicios

```bash
ssh capadonna@100.97.151.69 "bash ~/placas-parqueadero/scripts/run_vps_server.sh 8080 2"
```

## Notas

- El servidor escucha en `0.0.0.0:8080` (accesible por Tailscale y red publica si el firewall lo permite).
- El generador se conecta a `127.0.0.1:8080` en el mismo VPS.
- Si no llegan eventos, reinicie: el parqueadero puede quedar lleno (10 celdas); el generador ahora reutiliza placas para liberar celdas.
