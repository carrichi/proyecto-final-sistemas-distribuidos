import time
import socket
import services.log as log

def start_server():
  HOST = socket.gethostbyname(socket.gethostname())
  PORT = 65432
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_socket.bind((HOST, PORT))
  server_socket.listen(1)

  log.write(f'[Servidor] Escuchando desde {HOST}:{PORT}')

  time.sleep(3)

  connection, addr = server_socket.accept()
  log.write(f'[Servidor] Se encontro un cliente en: {addr}')

  with connection:
    try:
      while True:
        data = connection.recv(1024)
        if not data:
          break
        message = data.decode()
        log.write(f'[Servidor] [INFO] Mensaje recibido: {message}')

        if message.lower() == 'salir':
          connection.sendall(f'Conexion finalizada por el cliente {addr}'.encode())
          break

        connection.sendall(message.encode())
    except:
      log.write('[Servidor] [ERROR] El cliente cerró la conexion de forma inesperada...')
  log.write('[Servidor] Cerrando conexion')
  connection.close()
  server_socket.close()
  log.write('[Servidor] Finalizado')