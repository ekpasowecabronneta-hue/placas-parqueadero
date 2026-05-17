# Protocolo de mensajes

Cada evento es una linea de texto terminada en `\n`:

```
PLACA|TIMESTAMP|CELDA|ACCION
```

| Campo | Ejemplo | Descripcion |
|-------|---------|-------------|
| PLACA | `ABC123` | Identificador del vehiculo (3 letras + 3 digitos) |
| TIMESTAMP | `2026-05-17 14:30:00` | Hora del evento |
| CELDA | `3` | Indice de celda (0-9) |
| ACCION | `OCCUPY` o `RELEASE` | Ocupar o liberar celda |

## Regla de negocio

Si el generador envia una **placa que ya esta ocupada**, la accion es `RELEASE` y se libera la celda asociada.

## Ejemplo

```
XYZ789|2026-05-17 10:00:05|2|OCCUPY
XYZ789|2026-05-17 10:00:15|2|RELEASE
```
