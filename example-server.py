from datetime import datetime
import time

def guardar_hora_en_archivo(nombre_archivo='registro_hora.txt'):
    """
    Obtiene el timestamp y la hora actual, y los guarda en un archivo.
    
    Args:
        nombre_archivo (str): Nombre del archivo donde se guardará la hora. Valor por defecto: 'registro_hora.txt'.
    
    Returns:
        None
    """
    # Obtener timestamp y hora formateada
    timestamp_actual = time.time()
    hora_formateada = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Guardar en un archivo
    with open(nombre_archivo, 'w') as archivo:
        archivo.write(f"Timestamp: {timestamp_actual}\n")
        archivo.write(f"Hora: {hora_formateada}\n")
    
    print(f"Hora y timestamp guardados en {nombre_archivo}.")

# Llamada a la función
guardar_hora_en_archivo()