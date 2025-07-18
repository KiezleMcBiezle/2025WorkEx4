import socket
import threading
import time
import tkinter as tk

class Client:
    """Create an object that can send/recieve data over the network and communicate with the GUI."""
    def __init__(self, host, port, name, gui_callback): # Create the object.
        self.name = name
        self.gui_callback = gui_callback # A function to send data to the GUI.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect((host, port))
            self.socket.send(self.name.encode('utf-8'))
        except ConnectionRefusedError as e:
            self.gui_callback(f"❌ Could not connect: {e}")
            return

        self.running = True
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self, message): # Send a message and the user who sent it to the server as binary.
        if not self.running:
            return
        try:
            full_message = f"{self.name}: {message}"
            self.socket.send(full_message.encode('utf-8'))
        except (socket.timeout, socket.error):
            self.gui_callback("❌ Response timeout, please try again later.")
            self.running = False
        except Exception as e:
            self.gui_callback(f"❌ Error sending message: {e}")
            self.running = False

    def receive_messages(self): # Recieve binary from the server and turn it into usable data.
        while self.running:
            try:
                message = self.socket.recv(1024).decode('utf-8')
                if not message:
                    self.gui_callback("⚠️ Server disconnected.")
                    self.running = False
                    break
                self.gui_callback(message)
            except (BrokenPipeError, ConnectionResetError):
                self.gui_callback("❌ Disconnected from server.")
            except Exception as e:
                self.gui_callback(f"❌ Error sending message: {e}")

    def close(self): # End the connection with the server and delete the client object.
        self.running = False
        try:
            self.socket.close()
        except (socket.error, OSError):
            pass


class ChatGUI:
    """Create a user interface for entering a username and displaying/sending messages."""
    username = None
    txt = None
    entry = None
    def __init__(self, host='127.0.0.1', port=12345): # Create an object with pre-set information used to connect to the server later.
        self.host = host
        self.port = port
        self.client = None

        self.root = tk.Tk()
        self.root.withdraw()
        self.ask_username()
        self.root.mainloop()

    def ask_username(self): # Take the user input to use as a username.
        self.username_window = tk.Toplevel()
        self.username_window.title("Enter Username")
        self.username_window.geometry("300x100")
        self.username_window.resizable(False, False)
        self.username_window.grab_set()

        tk.Label(self.username_window, text="Enter your username:").pack(pady=5)
        self.username_entry = tk.Entry(self.username_window)
        self.username_entry.pack(pady=5)
        self.username_entry.focus()
        self.username_entry.bind('<Return>', lambda event: self.submit_username())

        tk.Button(self.username_window, text="Submit", command=self.submit_username).pack()

    def submit_username(self): # Assign the username only if one has been submitted.
        name = self.username_entry.get().strip()
        if name:
            self.username = name
            self.username_window.destroy()
            self.setup_main_window()

    def setup_main_window(self): # Create a pop-up window that can be made interactive later.
        self.root.deiconify()
        self.root.title("Renichat")
        self.root.geometry("700x600")
        self.root.configure(bg="black")

        self.create_title_bar()
        self.create_chat_window()
        self.create_input_area()

        self.client = Client(self.host, self.port, self.username, self.safe_display_message)

    def create_title_bar(self):
        title_bar = tk.Frame(self.root, bg='orange')
        title_bar.pack(fill=tk.X)

        tk.Label(title_bar, text='RENICHAT', bg='orange', fg='black', font='Stencil 16').pack(side=tk.LEFT, padx=10)
        tk.Button(title_bar, text='X', bg='red', fg='white', bd=0, command=self.close).pack(side=tk.RIGHT)

        def move_window(event): # Move the window to the centre of the screen.
            self.root.geometry(f'+{event.x_root}+{event.y_root}')
        title_bar.bind('<B1-Motion>', move_window)

    def create_chat_window(self): # Create a pop-up window that prompts the user for a login.
        self.txt = tk.Text(self.root, bg="black", fg="#ff6600", font='Helvetica 14', state=tk.DISABLED, wrap=tk.WORD)
        self.txt.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def create_input_area(self): # Add a space in the main window to input messages and send them.
        input_frame = tk.Frame(self.root, bg="black")
        input_frame.pack(fill=tk.X, pady=10)

        self.entry = tk.Entry(input_frame, bg="#2C3E50", fg="#ff6600", font='Helvetica 14')
        self.entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.entry.bind("<Return>", lambda event: self.send_msg())

        send_btn = tk.Button(input_frame, text="Send", font='Helvetica 13 bold', bg='#ff6600', command=self.send_msg)
        send_btn.pack(side=tk.LEFT, padx=5)

    def send_msg(self): # Take an input and sends it to the server aswell as the display_message function.
        message = self.entry.get().strip()
        if message:
            time_str = time.strftime('%H:%M')
            self.display_message(f"You -> {message} [{time_str}]")
            self.client.send_message(message)
            self.entry.delete(0, tk.END)

            if message.lower() == 'bye':
                self.close()

    def display_message(self, message): # Take an input and print it to the users' window.
        self.txt.config(state=tk.NORMAL)
        self.txt.insert(tk.END, f"\n{message}")
        self.txt.config(state=tk.DISABLED)
        self.txt.see(tk.END)

    def safe_display_message(self, message): # Print a message that doesn't get deleted later.
        self.root.after(0, lambda: self.display_message(f"{message} [{time.strftime('%H:%M')}]"))

    def close(self):
        if self.client:
            self.client.send_message("bye")
            self.client.close()
        self.root.quit()


if __name__ == '__main__':
    ChatGUI('192.168.55.16', 12345)  # Replace with your server IP if needed
