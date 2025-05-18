"""
Communication System between Nodes - Versión Corregida
Implementación de un sistema distribuido con confirmación de mensajes
"""

import socket
import threading
import json
from datetime import datetime

class Node:
    def __init__(self, id_node, port, nodes_info, node_ip='0.0.0.0', server_ready_event=None, base_port=5000):
        """
        Args:
            id_node: Identificador único del nodo (1, 2, 3...)
            port: Puerto de escucha
            nodes_info: Diccionario {puerto: ip} de nodos disponibles
            node_ip: IP del nodo
            server_ready_event: Evento para sincronización
            base_port: Puerto base para cálculo de IDs
        """
        self.id_node = id_node
        self.port = port
        self.ip = node_ip
        self.nodes_info = nodes_info
        self.messages = []
        self.server = None
        self.server_ready_event = server_ready_event
        self.base_port = base_port

    def start_server(self):
        """Inicia el servidor TCP para recibir mensajes"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            self.server = s
            s.bind((self.ip, self.port))
            s.listen()
            print(f"Node {self.id_node} Server is ready and listening on {self.ip}:{self.port}")
            if self.server_ready_event:
                self.server_ready_event.set()

            while True:
                try:
                    conn, addr = s.accept()
                    threading.Thread(
                        target=self.handle_connection,
                        args=(conn, addr),
                        daemon=True
                    ).start()
                except Exception as e:
                    print(f"[Node {self.id_node}] Server error: {e}")

    def handle_connection(self, conn, addr):
        """Maneja una conexión entrante"""
        with conn:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    return

                message = json.loads(data)
                hour = datetime.fromisoformat(message['timestamp']).strftime("%H:%M:%S")
                print(f"[Node {self.id_node}] Received from {message['origin']} at {hour}: {message['content']}")

                self.messages.append(message)

                # Enviar ACK al puerto correcto
                if not message['content'].startswith("ACK:"):
                    ack = {
                        'origin': self.id_node,
                        'destination': self.base_port + message['origin'],  # Calcula puerto destino
                        'content': f"ACK: {message['content']}",
                        'timestamp': datetime.now().isoformat()
                    }

                    if self.send_message(ack):
                        print(f"[Node {self.id_node}] ACK sent to {message['origin']}: {ack['content']}")
                    else:
                        print(f"[Node {self.id_node}] Failed to send ACK to {message['origin']}")

            except json.JSONDecodeError:
                print(f"[Node {self.id_node}] Invalid message format")
            except Exception as e:
                print(f"[Node {self.id_node}] Connection error: {e}")

    def send_message(self, message_dict):
        """Envía un mensaje a otro nodo"""
        try:
            dest_port = message_dict['destination']
            if dest_port == self.port:
                print(f"[Node {self.id_node}] Warning: Cannot send message to self.")
                return False

            dest_ip = self.nodes_info.get(dest_port)
            if not dest_ip:
                print(f"[Node {self.id_node}] Error: Unknown destination port {dest_port}")
                return False

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5.0)

                s.connect((dest_ip, dest_port))

                message_dict['origin'] = self.id_node
                message_dict['timestamp'] = datetime.now().isoformat()

                s.sendall(json.dumps(message_dict).encode('utf-8'))
                self.messages.append(message_dict)
                print(f"[Node {self.id_node}] Sent to {dest_port}: {message_dict['content']}")
                return True

        except ConnectionRefusedError:
            print(f"[Node {self.id_node}] Error: Node {dest_port - self.base_port} not available")
        except socket.timeout:
            print(f"[Node {self.id_node}] Error: Connection timeout with node {dest_port - self.base_port}")
        except Exception as e:
            print(f"[Node {self.id_node}] Send error: {e}")
        
        return False

    def user_interface(self):
        """Interfaz de línea de comandos"""
        print(f"\nNode {self.id_node} - Command Interface")
        print("=" * 40)

        while True:
            try:
                print("\nOptions:")
                print("1. Send message")
                print("2. View message history")
                print("3. Export history")
                print("4. Exit")

                choice = input("Select option: ").strip()

                if choice == "1":
                    self._send_message_ui()
                elif choice == "2":
                    self._show_history()
                elif choice == "3":
                    self.export_history()
                elif choice == "4":
                    print("Exiting...")
                    break
                else:
                    print("Invalid option")

            except Exception as e:
                print(f"Error: {e}")

    def _send_message_ui(self):
        """Maneja el envío de mensajes desde la UI"""
        available_ids = [p - self.base_port for p in self.nodes_info.keys()]
        print("\nAvailable node IDs:", available_ids)
        try:
            dest_node_id = int(input("Destination node ID: "))
            dest_port = self.base_port + dest_node_id
            
            if dest_port not in self.nodes_info:
                print("Error: Invalid destination node ID")
                return

            content = input("Message: ").strip()
            if not content:
                print("Error: Message cannot be empty")
                return

            message = {
                'destination': dest_port,
                'content': content
            }
            self.send_message(message)

        except ValueError:
            print("Error: Please enter a valid node ID")

    def _show_history(self):
        """Muestra el historial de mensajes"""
        print("\nMessage History:")
        print("=" * 40)
        for i, msg in enumerate(self.messages, 1):
            direction = f"{msg.get('origin', '?')} -> {msg['destination'] - self.base_port}"
            print(f"{i}. [{msg['timestamp']}] {direction}: {msg['content']}")

    def export_history(self):
        """Exporta el historial a JSON"""
        filename = f"node_{self.id_node}_history.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'node_id': self.id_node,
                    'timestamp': datetime.now().isoformat(),
                    'messages': self.messages
                }, f, indent=2, ensure_ascii=False)
            print(f"History exported to {filename}")
        except Exception as e:
            print(f"Export failed: {e}")

if __name__ == "__main__":
    # Configuración - CAMBIAR POR CADA NODO
    NODE_ID = 1  # Cambiar este valor (1, 2, 3...)
    BASE_PORT = 5000
    NODE_IPS = {
        5001: '192.168.100.62',
        5002: '192.168.100.63',
        5003: '192.168.100.64',
        5004: '192.168.100.65'
    }

    server_ready = threading.Event()
    node = Node(
        id_node=NODE_ID,
        port=BASE_PORT + NODE_ID,
        nodes_info={p: ip for p, ip in NODE_IPS.items() if p != BASE_PORT + NODE_ID},
        server_ready_event=server_ready,
        base_port=BASE_PORT
    )

    threading.Thread(target=node.start_server, daemon=True).start()
    server_ready.wait()
    node.user_interface()
