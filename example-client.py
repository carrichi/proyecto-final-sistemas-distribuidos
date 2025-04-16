# cliente.py
import socket

# Crear socket TCP/IP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar al servidor
server_address = ('localhost', 65432)
client_socket.connect(server_address)

try:
    # Enviar un mensaje
    mensaje = "Hola, servidor"
    client_socket.sendall(mensaje.encode())

    # Esperar respuesta
    respuesta = client_socket.recv(1024)
    print("Respuesta del servidor:", respuesta.decode())

finally:
    client_socket.close()
