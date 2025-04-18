import time
import socket
import threading
from services.server import start_server
from services.client import start_client
import services.log as log

def main():
  print(f'Inicializando...')
  log.initialize()
  server_th = threading.Thread(target=start_server, daemon=True)
  server_th.start()
  time.sleep(1)

  client_th = threading.Thread(target=start_client)
  client_th.start()

  server_th.join()
  print(f'Ejecución finalizada.')

main()