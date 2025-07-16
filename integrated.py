import socket
import threading
import sys
from tkinter import *
from tkinter import simpledialog
import time

class Client:
    def __init__(self, gui, HOST, PORT):
        self.gui = gui
        self.socket = socket.socket()
        try:
            self.socket.connect((HOST, PORT))
        except ConnectionRefusedError:
            self.gui.show_message(f"Could not connect to server at {HOST}:{PORT}")
            return

        self.name = None
        self.running = True

    def start(self, name):
        self.name = name
        try:
            self.socket.send(self.name.encode())
        except Exception as e:
            self.gui.show_message(f"Failed to send username: {e}")
            return

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self, msg):
        if not self.name or not msg.strip():
            return
        try:
            client_message = self.name + ": " + msg
            self.socket.send(client_message.encode())
        except Exception as e:
            self.gui.show_message(f"Failed to send message: {e}")

    def receive_messages(self):
        while self.running:
            try:
                server_message = self.socket.recv(1024).decode()
                if not server_message:
                    self.gui.show_message("Server disconnected.")
                    break
                self.gui.show_message(server_message)
            except Exception as e:
                self.gui.show_message(f"Error receiving message: {e}")
                break

        self.socket.close()
        self.running = False

    def close(self):
        self.running = False
        self.socket.close()

class ChatGUI:
    def __init__(self, root):
        self.root = root
        root.title('Renichat')
        root.geometry('700x600')
        root.config(bg="black")

        self.txt = Text(root, bg="#000000", fg="#ffa500", font='Helvetica 14', width=60)
        self.txt.pack(padx=10, pady=10, fill=BOTH, expand=True)

        self.input_frame = Frame(root, bg="#000000")
        self.input_frame.pack(fill=X, pady=10)

        self.e = Entry(self.input_frame, bg="#2C3E50", fg="#ffa500", font='Helvetica 14', width=55)
        self.e.pack(side=LEFT, padx=10)
        self.e.bind('<Return>', self.send_msg)
