# AppVentas - Gestión de Clientes y Papelería

Este proyecto es una aplicación de escritorio en Python para gestionar clientes, pedidos de papelería y usuarios. La interfaz gráfica se construye con `customtkinter` y `tkinter`, y los datos se guardan en archivos JSON.

## Qué hace el programa

- Permite registrar usuarios y autenticarse.
- Gestiona clientes y pedidos de papelería.
- Agrega productos desde una lista predefinida de artículos de papelería.
- Calcula subtotal, IVA (21%) y total del pedido.
- Guarda los datos de clientes en `clientes.json`.
- Guarda los datos de usuario en `datos_papeleria.json`.
- Ofrece vistas:
  - Dashboard con estadísticas.
  - Gestión de clientes.
  - Configuración del sistema.
  - Pantallas de login y registro.

## Archivos principales

- `cliente.py` - código principal de la aplicación.
- `clientes.json` - archivo de almacenamiento de clientes y pedidos.
- `datos_papeleria.json` - archivo de almacenamiento de usuarios y configuración.

## Requisitos

- Python 3.x
- `customtkinter`
- `tkinter` (incluido en la mayoría de distribuciones de Python)

## Instalación

1. Abre una terminal en la carpeta del proyecto.
2. Instala la dependencia con pip:

```bash
pip install -r requirements.txt
```

## Ejecución

Desde la carpeta del proyecto, ejecuta:

```bash
python cliente.py
```

Si tu instalación de Python usa `python3`, ejecuta:

```bash
python3 cliente.py
```

## Notas

- El archivo `clientes.json` se crea o actualiza automáticamente cuando se guardan clientes.
- El archivo `datos_papeleria.json` se utiliza para almacenar usuarios registrados.
- Si `clientes.json` o `datos_papeleria.json` no existen, la aplicación los crea cuando es necesario.
