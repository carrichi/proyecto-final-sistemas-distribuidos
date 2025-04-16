# servidor.py
import socket

# Crear socket TCP/IP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Enlace a una dirección y puerto (host, port)
server_address = ('localhost', 65432)
server_socket.bind(server_address)

# Escuchar conexiones entrantes
server_socket.listen(1)
print(f"Servidor escuchando en {server_address}")

# Esperar una conexión
connection, client_address = server_socket.accept()
with connection:
    print(f"Conexión establecida con {client_address}")
    while True:
        data = connection.recv(1024)
        if not data:
            break
        print("Mensaje recibido:", data.decode())
        connection.sendall(b"Recibido: " + data)