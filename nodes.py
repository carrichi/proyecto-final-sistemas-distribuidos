"""
Communication System between Nodes
Description:
Implementation of a distributed system where various nodes act simultaneously
as clients and servers, allowing messages to be sent, received and stored.

Characteristics:
-Bidirectional communication between nodes
-Local storage of message history
-Automatic confirmation response
-Timestamp include in each message
- User interface for each console

Authors:
Mendoza Flores Axel Fernando
Sergio Jair
Leysha

Date: 17/ 04/ 2025
"""

import socket
import threading
import json
#import time
from datetime import datetime
#ip = '192.168.122.35'
class Node:
    """
    Class that represents an individual node

    Attributes:
        id_node(int): ID of the node
        port (int): Port where the server is listening
        more_nodes (list): List of nodes ports available
        messages (dict): Dictionary of  sent/received messages
        server (socket): Server socket instance

    """
    def _init_(self, id_node, port, more_nodes):
        """
        New instance of Node.

        Args:
            id_node (int): ID of the node
            port (int): Port where the server is listening
            more_nodes (list): List of nodes ports available
        """
        self.id_node = id_node
        self.port = port
        self.more_nodes = more_nodes
        self.messages = [] #Almacenamiento de mensajes
        self.server = None

    def start_server(self):
        """Start The TCP server in a separate thread

        Listening entry connections and creates a new thread
        for each received connection.

        The server executes in second plane allowing program finishing although
        thread still active.
        """
        with (socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s):
            self.server = s
            s.bind(('0.0.0.0', self.port))
            s.listen()
            print(f"Receiving messages from {self.port}")


            while True:
                try:
                    conn, addr = s.accept()
                    #New thread for each connection
                    threading.Thread(
                        target=self.handle_connection,
                        args=(conn,),
                        daemon=True
                    ).start()
                except Exception as e:
                    print(f"[Node {self.id_node}] Error accepting connection: {e}")

    def handle_connection(self, conn):
        """Handles an incoming connection and process received message

        Args:
            conn (socket): Cliente connection Object

        Process:
        1. Receive and decode message
        2. Store message
        3. Send automatic confirmation to the sender
        4. Close connection

        """
        with conn:
            try:
                data = conn.recv(1024).decode()
                message = json.loads(data)
                print(f"Node {self.id_node} received: {message['content']} from {message['origin']}")

                #Save received message
                self.messages.append(message)

                #Automatic export after save each message
                if len(self.messages) % 5 == 0: #Each five messages
                    self.export_history()

                #Auto confirmation response
                response = {
                    'origin' : self.id_node,
                    'destiny' : message['destiny'],
                    'content' : f"Received:: {message['content']}",
                    'timestamp' : datetime.now().isoformat()
                }
                self.send_message(response)
            except json.JSONDecodeError:
                print(f"[Node {self.id_node}] Error message]")

    def send_message(self, message_dict):
        """Send message to other node
        Args:
        message_dict (dict): Dictionary of message

        Expected structure:
        {
        'origin' : int, # ID origin node
        'destiny' : int, # Port destiny node
        'content' : str, # Content of message
        'timestamp' : int, # ISO format timestamp
        }
        The message is serialized to JSON before being sent.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((message_dict['destiny_ip'], message_dict['destiny_port']))
                s.sendall(json.dumps(message_dict).encode())

                #Save message sent
                self.messages.append(message_dict)
                print(f"[Node {self.id_node}] Message sent to {message_dict['destiny']}")

        except ConnectionRefusedError:
            print(f"[Node {self.id_node}] Error: Destiny error {message_dict['destiny']} not available")
        except Exception as e:
            print(f"Error sending the message: {e}")

    def user_interface(self):
        """Commandline to send messages

        Show a menu allowing:
        1. Select destiny node
        2. Type text for the message
        3. Send the message
        """

        #Thread for messages sent by the user
        while True:
            try:
                print("Available nodes: ", self.more_nodes)
                destiny = int(input(f"Send to (options: {self.more_nodes}): )"))
                if destiny not in self.more_nodes:
                    print("Invalid destiny node")
                    continue

                content = input("Type your message: ").strip()
                if not content:
                    print("Error: Message cannot be empty")
                    continue

                #Build message structure
                message = {
                    'destiny_port' : self.port,
                    'destiny_ip' : destiny,
                    'content' : content,
                    'timestamp' : datetime.now().isoformat()
                }
                self.send_message(message)
            except ValueError:
                print("Error: Type a node number valid")
            except Exception as e:
                print(f"unexpect error: {e}")

    def export_history(self):
        """Export the history to a JSON file"""
        filename = f"history_{self.id_node}.json"
        with open(filename, 'w') as f:
            json.dump(self.messages, f, ident=2)
        print(f"History exported to {filename}")


if _name_ == "_main_":
    """Required configuration:
    -ID for each node
    - Base port (+ ID = binding)
    -List of node ports 
    
    Example for 4 nodes (run in separate terminals):
    Node 1: nodes.py (port 5001)
    Node 2: nodes.py (port 5002)
    Node 3: nodes.py (port 5003)
    Node 4: nodes.py (port 5004)
    
    """

    id_node = 2
    port = 5000 + id_node
    more_nodes = [p for p in range(5001,5005) if p != port ]

    node = Node(id_node, port, more_nodes)

    #start server in another thread
    threading.Thread(
        target=node.start_server,
        daemon=True
    ).start()

    #start  user interface
    node.user_interface()