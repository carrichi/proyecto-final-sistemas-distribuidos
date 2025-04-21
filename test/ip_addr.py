import subprocess
import json

# Ruta completa al ejecutable vmrun
VMRUN_PATH = r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"

# Diccionario con nombres descriptivos de las VMs y sus rutas .vmx
VMX_PATHS = {
    "Debian 1": r"C:\Users\sergi\Documents\Virtual Machines\Debian\Debian.vmx",
    "Debian 2": r"C:\Users\sergi\Documents\Virtual Machines\Debian_2\Debian_2.vmx",
    "Debian 3": r"C:\Users\sergi\Documents\Virtual Machines\Debian_3\Debian_3.vmx",
    "Debian 4": r"C:\Users\sergi\Documents\Virtual Machines\Debian_4\Debian_4.vmx"
}

# Función para obtener la dirección IP de una máquina virtual
def obtener_ip(vmx_path):
    try:
        # Ejecutar el comando vmrun para obtener la IP
        resultado = subprocess.run(
            [VMRUN_PATH, "getGuestIPAddress", vmx_path, "-wait"],
            capture_output=True, text=True
        )
        
        # Verificar salida del comando
        if resultado.returncode == 0:
            ip = resultado.stdout.strip()  # Limpiar espacios en blanco
            return ip
        else:
            print(f"[Error] No se pudo obtener la IP para {vmx_path}: {resultado.stderr}")
            return None
    except Exception as e:
        print(f"[Exception] Ocurrió un error: {e}")
        return None

# Diccionario para almacenar las IPs de las VMs
ips_vms = {}

# Procesar cada VM y guardar sus direcciones IP en el diccionario
for nombre_vm, ruta_vmx in VMX_PATHS.items():
    print(f"Obteniendo IP para {nombre_vm}...")
    ip_vm = obtener_ip(ruta_vmx)
    if ip_vm:
        ips_vms[nombre_vm] = ip_vm
        print(f"{nombre_vm}: {ip_vm}")
    else:
        ips_vms[nombre_vm] = "No disponible"
        print(f"{nombre_vm}: No se pudo obtener la dirección IP.")

# Mostrar el resultado final
print("\nDirecciones IP de las VMs:")
for nombre_vm, ip in ips_vms.items():
    print(f"{nombre_vm} - {ip}")

# Guardar el resultado en un archivo JSON
output_file = "ips_vms.json"
with open(output_file, "w") as archivo_json:
    json.dump(ips_vms, archivo_json, indent=4)

print(f"\nLas direcciones IP se han guardado en '{output_file}'.")