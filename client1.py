import socket
from threading import Thread
import sys

class Client:
    def __init__(self, HOST, PORT):
        self.socket = socket.socket()
        try:
            self.socket.connect((HOST, PORT))
        except ConnectionRefusedError:
            print(f"Could not connect to server at {HOST}:{PORT}")
            sys.exit(1)

        self.name = input("Enter your name: ")
        self.talk_to_server()

    def talk_to_server(self):
        try:
            self.socket.send(self.name.encode())
        except Exception as e:
            print(f"Failed to send username: {e}")
            sys.exit(1)

        Thread(target=self.receive_message, daemon=True).start()
        self.send_message()

    def send_message(self):
        try:
            while True:
                client_input = input()
                client_message = self.name + ": " + client_input
                self.socket.send(client_message.encode())
        except (BrokenPipeError, ConnectionResetError):
            print("Disconnected from server.")
            sys.exit(0)
        except KeyboardInterrupt:
            print("\nExiting.")
            self.socket.close()
            sys.exit(0)

    def receive_message(self):
        try:
            while True:
                server_message = self.socket.recv(1024).decode()
                if not server_message.strip():
                    print("Server disconnected.")
                    sys.exit(0)

                print("\033[1;31;40m" + server_message + "\033[0m")
        except Exception as e:
            print(f"Error receiving message: {e}")
            sys.exit(0)

if __name__ == '__main__':
    Client('192.168.55.3', 12345)  # Adjust the IP and port as needed
