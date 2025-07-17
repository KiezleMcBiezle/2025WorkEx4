import socket
import json
from threading import Thread

class Server:
    clients = []

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
        print(f"Server started on {host}:{port}, waiting for connections...")

    def listen(self):
        while True:
            try:
                client_socket, address = self.socket.accept()
                print(f"New connection from: {address}")

                # Receive the username
                username = client_socket.recv(1024).decode('utf-8').strip()
                if not username:
                    client_socket.close()
                    continue

                client = {
                    "name": username,
                    "socket": client_socket
                }

                # Inform others
                self.broadcast_message({
                    "type": "text",
                    "sender": "Server",
                    "data": f"{username} has joined the chat."
                })

                self.clients.append(client)

                # Start a thread for this client
                Thread(target=self.handle_client, args=(client,), daemon=True).start()
            except Exception as e:
                print(f"[ERROR] Accepting connection: {e}")

    def handle_client(self, client):
        name = client["name"]
        sock = client["socket"]
        buffer = ""

        try:
            while True:
                data = sock.recv(262144)
                if not data:
                    break  # Client disconnected

                buffer += data.decode('utf-8')

                # Process multiple messages from buffer
                while True:
                    try:
                        msg_obj, idx = json.JSONDecoder().raw_decode(buffer)
                        buffer = buffer[idx:].lstrip()
                        print(f"[RECV from {name}]: {msg_obj}")

                        self.broadcast_message(msg_obj, exclude=name)

                    except json.JSONDecodeError:
                        break  # Wait for more data

        except Exception as e:
            print(f"[ERROR] Communication with {name}: {e}")

        finally:
            # Remove the client
            if client in self.clients:
                self.clients.remove(client)
                print(f"{name} has disconnected.")
                self.broadcast_message({
                    "type": "text",
                    "sender": "Server",
                    "data": f"{name} has left the chat."
                })
            sock.close()

    def broadcast_message(self, message, exclude=None):
        message_str = json.dumps(message)
        for client in self.clients:
            try:
                if client["name"] != exclude:
                    client["socket"].sendall(message_str.encode('utf-8'))
            except Exception as e:
                print(f"[ERROR] Sending to {client['name']}: {e}")
                client["socket"].close()
                self.clients.remove(client)

if __name__ == '__main__':
    server = Server('0.0.0.0', 12345)
    server.listen()
