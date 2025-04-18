from utils import getTimestamp
def initialize():
  with open('log.txt', 'w') as archivo:
    archivo.write(f"[{getTimestamp()}] Inicializando log...\n")

def write(message):
  with open('log.txt', 'a') as archivo:
    archivo.write(f"[{getTimestamp()}] {message}\n")
    print(f"[{getTimestamp()}] {message}")