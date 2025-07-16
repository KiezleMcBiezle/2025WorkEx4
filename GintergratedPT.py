import socket
import threading
import sys
import time
from tkinter import *

class Client:
    def __init__(self, HOST, PORT, gui_callback):
        self.socket = socket.socket()
        self.gui_callback = gui_callback  # Function to update GUI with received messages

        try:
            self.socket.connect((HOST, PORT))
        except ConnectionRefusedError:
            print(f"Could not connect to server at {HOST}:{PORT}")
            sys.exit(1)

        self.name = input("Enter your name: ")
        self.socket.send(self.name.encode('utf-8'))

        # Start receiving messages in a background thread
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self, message):
        try:
            full_message = f"{self.name}: {message}"
            self.socket.send(full_message.encode('utf-8'))
        except (BrokenPipeError, ConnectionResetError):
            self.gui_callback("Disconnected from server.")
        except Exception as e:
            self.gui_callback(f"Error sending message: {e}")

    def receive_messages(self):
        while True:
            try:
                server_message = self.socket.recv(1024).decode('utf-8')
                if not server_message:
                    self.gui_callback("Server disconnected.")
                    break
                self.gui_callback(server_message)
            except Exception as e:
                self.gui_callback(f"Error receiving message: {e}")
                break


class ChatGUI:
    def __init__(self, host='127.0.0.1', port=12345):
        self.client = None

        # Initialize GUI
        self.root = Tk()
        self.root.title('Renichat')
        self.root.overrideredirect(True)

        # Window dimensions
        window_width = 700
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.config(bg="black")

        # Title bar
        title_bar = Frame(self.root, bg='orange')
        title_bar.pack(fill=X)
        title_label = Label(title_bar, text='RENICHAT', bg='orange', fg='black', font='stencil')
        title_label.pack(side=LEFT, padx=10)
        close_button = Button(title_bar, text='X', command=self.root.destroy, bg='red', fg='white', bd=0)
        close_button.pack(side=RIGHT)

        def move_window(event):
            self.root.geometry(f'+{event.x_root}+{event.y_root}')
        title_bar.bind('<B1-Motion>', move_window)
        title_label.bind('<B1-Motion>', move_window)

        # Chat text area
        self.txt = Text(self.root, bg="#000000", fg="#ff6600", font='Helvetica 14', width=60)
        self.txt.pack(padx=10, pady=(5, 0), fill=BOTH, expand=True)
        self.txt.config(state=DISABLED)

        # Input field
        input_frame = Frame(self.root, bg="black")
        input_frame.pack(fill=X, pady=10)
        self.entry = Entry(input_frame, bg="#2C3E50", fg="#ff6600", font='Helvetica 14', width=55)
        self.entry.pack(side=LEFT, padx=10)
        self.entry.bind("<Return>", lambda event: self.send_msg())

        send_btn = Button(input_frame, text="Send", font='Helvetica 13 bold', bg='#ff6600', command=self.send_msg)
        send_btn.pack(side=LEFT, padx=5)

        # Start the client connection
        self.client = Client(host, port, self.receive_msg)

        self.root.mainloop()

    def send_msg(self):
        user_text = self.entry.get().strip()
        if user_text:
            time_str = time.strftime('%H:%M')
            self.display_msg(f"You -> {user_text} [{time_str}]")
            self.client.send_message(user_text)
            self.entry.delete(0, END)

    def receive_msg(self, message):
        time_str = time.strftime('%H:%M')
        self.display_msg(f"{message} [{time_str}]")

    def display_msg(self, message):
        self.txt.config(state=NORMAL)
        self.txt.insert(END, f"\n{message}")
        self.txt.config(state=DISABLED)
        self.txt.see(END)


if __name__ == '__main__':
    ChatGUI('192.168.55.16', 12345)  # Update IP/port as needed
