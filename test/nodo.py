import subprocess
import socket
import threading
import time
from datetime import datetime
import json

# Archivo que contiene las direcciones IP generadas por ip_addr.py
IP_ARCHIVO = "ips_vms.json"

# Ruta completa al ejecutable vmrun (por si deseas ejecutar desde Python)
VMRUN_PATH = r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"

# Puerto utilizado por el servidor y cliente
PORT = 12345
ALMACENAMIENTO = "mensajes_nodo.txt"  # Archivo donde se almacenan los mensajes

# Bloqueo para sincronización de almacenamiento
lock = threading.Lock()


# Función para cargar las IPs desde un archivo JSON generado dinámicamente
def cargar_ips():
    try:
        with open(IP_ARCHIVO, "r") as archivo:
            ips = json.load(archivo)
            return ips
    except Exception as e:
        print(f"[Error] No se pudo cargar el archivo de IPs: {e}")
        return {}


# Función para registrar mensajes en el archivo local
def registrar_mensaje(tipo, mensaje, nodo):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with lock:
        with open(ALMACENAMIENTO, "a") as archivo:
            archivo.write(f"{timestamp} | {tipo} | Nodo: {nodo} | Mensaje: {mensaje}\n")


# Función para iniciar el servidor en el nodo
def iniciar_servidor():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen()
    print(f"[Servidor] Escuchando en el puerto {PORT}")

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=manejar_conexion, args=(conn, addr)).start()


# Función para manejar conexiones entrantes (servidor)
def manejar_conexion(conn, addr):
    try:
        data = conn.recv(1024).decode()
        if data:
            print(f"[Servidor] Mensaje recibido de {addr}: {data}")
            registrar_mensaje("Recibido", data, addr[0])

            # Enviar respuesta automática
            respuesta = f"Mensaje recibido a las {datetime.now().strftime('%H:%M:%S')}"
            conn.send(respuesta.encode())
            registrar_mensaje("Enviado", respuesta, addr[0])
    except Exception as e:
        print(f"[Servidor] Error manejando la conexión: {e}")
    finally:
        conn.close()


# Función para iniciar el cliente en el nodo
def iniciar_cliente(ips_vms):
    while True:
        # Solicitar mensaje a enviar y seleccionar un nodo
        mensaje = input("[Cliente] Escribe el mensaje: ")
        print("[Cliente] Selecciona el nodo destinatario:")
        for i, (nombre_vm, ip) in enumerate(ips_vms.items()):
            print(f"[{i}] {nombre_vm} ({ip})")
        
        try:
            opcion = int(input("-> "))
            if opcion < 0 or opcion >= len(ips_vms):
                print("[Cliente] Nodo inválido.")
                continue

            nombre_vm, ip_destino = list(ips_vms.items())[opcion]

            # Enviar el mensaje al nodo seleccionado
            enviar_mensaje(mensaje, nombre_vm, ip_destino)
        except ValueError:
            print("[Cliente] Entrada no válida.")


# Función para enviar un mensaje a otro nodo (cliente)
def enviar_mensaje(mensaje, nombre_vm, ip_destino):
    timestamp_envio = datetime.now().strftime('%H:%M:%S')
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip_destino, PORT))

        mensaje_con_tiempo = f"{mensaje} | Enviado a las {timestamp_envio}"
        client_socket.send(mensaje_con_tiempo.encode())
        registrar_mensaje("Enviado", mensaje_con_tiempo, nombre_vm)

        # Recibir respuesta del servidor
        respuesta = client_socket.recv(1024).decode()
        print(f"[Cliente] Respuesta desde {nombre_vm}: {respuesta}")
        registrar_mensaje("Recibido", respuesta, nombre_vm)
    except Exception as e:
        print(f"[Cliente] Error enviando al nodo {nombre_vm}: {e}")
    finally:
        client_socket.close()


# Función principal para iniciar el nodo
def iniciar_nodo():
    # Cargar las IPs dinámicas desde el archivo JSON
    ips_vms = cargar_ips()
    if not ips_vms:
        print("[Error] No se encontraron direcciones IP válidas. Verifica el archivo ips_vms.json.")
        return

    # Ejecutar servidor y cliente en hilos paralelos
    threading.Thread(target=iniciar_servidor).start()
    threading.Thread(target=iniciar_cliente, args=(ips_vms,)).start()


# Punto de entrada principal para el script
if __name__ == "__main__":
    print("[Nodo] Iniciando nodo...")
    iniciar_nodo()