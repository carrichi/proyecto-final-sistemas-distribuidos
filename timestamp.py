from datetime import datetime
import time

# Obtener timestamp y hora formateada
timestamp_actual = time.time()
hora_formateada = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Guardar en un archivo
with open('registro_hora.txt', 'w') as archivo:
    archivo.write(f"Timestamp: {timestamp_actual}\n")
    archivo.write(f"Hora: {hora_formateada}\n")

print("Hora y timestamp guardados.")