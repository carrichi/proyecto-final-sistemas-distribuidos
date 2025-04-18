import socket
import time
import services.log as log
def start_client():
  log.write(f'Inicializando cliente...')
  HOST = socket.gethostbyname(socket.gethostname())
  PORT = 65432

  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client_socket.connect((HOST, PORT))


  time.sleep(3)
  print('>>>> Se conectó al servidor, escribe "salir" para terminar.')

  while True:
    message = input("> ")
    log.write(f'[Cliente ] Enviando mensaje a {HOST}: {message}')
    client_socket.sendall(message.encode())

    if message.lower() == "salir":
      response = client_socket.recv(1024)
      log.write(f'[Cliente ] {HOST} respondió con: {response.decode()}')
      break

    response = client_socket.recv(1024)
    log.write(f'[Cliente ] {HOST} respondió con: {response.decode()}')
  
  client_socket.close()
  log.write(f'[Cliente ] Conexión cerrada.')
