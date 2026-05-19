# Mac Mini — juanjosearevalocamargo@100.99.72.63

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
