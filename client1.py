import socket
import threading
import time
import json
import base64
from tkinter import *
from tkinter import filedialog, Toplevel
from PIL import Image, ImageTk
import io


class Client:
    def __init__(self, HOST, PORT, name, gui_callback):
        self.socket = socket.socket()
        self.gui_callback = gui_callback  # Функция обновления GUI
        self.name = name

        try:
            self.socket.connect((HOST, PORT))
        except ConnectionRefusedError:
            self.gui_callback(f"Could not connect to server at {HOST}:{PORT}")
            return

        # Отправляем имя пользователя (простой текст)
        self.socket.send(self.name.encode('utf-8'))

        # Запускаем приём сообщений в фоне
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self, message):
        try:
            msg_dict = {
                "type": "text",
                "sender": self.name,
                "data": message
            }
            self.socket.send(json.dumps(msg_dict).encode('utf-8'))
        except (BrokenPipeError, ConnectionResetError):
            self.gui_callback("Disconnected from server.")
        except Exception as e:
            self.gui_callback(f"Error sending message: {e}")

    def send_image(self, img_b64):
        try:
            msg_dict = {
                "type": "image",
                "sender": self.name,
                "data": img_b64
            }
            self.socket.send(json.dumps(msg_dict).encode('utf-8'))
        except (BrokenPipeError, ConnectionResetError):
            self.gui_callback("Disconnected from server.")
        except Exception as e:
            self.gui_callback(f"Error sending image: {e}")

    def receive_messages(self):
        buffer = ""
        while True:
            try:
                data = self.socket.recv(262144)
                if not data:
                    self.gui_callback("Server disconnected.")
                    break

                buffer += data.decode('utf-8')

                while True:
                    try:
                        obj, idx = json.JSONDecoder().raw_decode(buffer)
                        buffer = buffer[idx:].lstrip()
                        self.gui_callback(json.dumps(obj))  # передаём обратно как JSON-строку
                    except json.JSONDecodeError:
                        break  # ждём больше данных
            except Exception as e:
                self.gui_callback(f"Error receiving message: {e}")
                break


class ChatGUI:
    def __init__(self, host='127.0.0.1', port=12345):
        self.client = None
        self.host = host
        self.port = port
        self.images = []  # Хранение изображений для предотвращения удаления сборщиком мусора
        self.ask_username()

    def ask_username(self):
        self.root = Tk()
        self.root.withdraw()

        self.username_window = Toplevel()
        self.username_window.title("Enter Username")
        self.username_window.geometry("300x100")
        self.username_window.resizable(False, False)
        self.username_window.grab_set()

        label = Label(self.username_window, text="Enter your username:")
        label.pack(pady=5)

        self.username_entry = Entry(self.username_window)
        self.username_entry.pack(pady=5)
        self.username_entry.focus()

        submit_btn = Button(self.username_window, text="Submit", command=self.submit_username)
        submit_btn.pack()

        self.username_entry.bind('<Return>', lambda event: self.submit_username())

        self.root.mainloop()

    def submit_username(self):
        name = self.username_entry.get().strip()
        if name:
            self.username = name
            self.username_window.destroy()
            self.setup_main_window()

    def setup_main_window(self):
        self.root.deiconify()
        self.root.title('Renichat')
        self.root.geometry('700x600')
        self.root.config(bg="black")

        # Текстовое поле для чата
        self.txt = Text(self.root, bg="#000000", fg="#ff6600", font='Helvetica 14', width=60)
        self.txt.pack(padx=10, pady=(5, 0), fill=BOTH, expand=True)
        self.txt.config(state=DISABLED)

        # Поле ввода и кнопки
        input_frame = Frame(self.root, bg="black")
        input_frame.pack(fill=X, pady=10)

        self.entry = Entry(input_frame, bg="#2C3E50", fg="#ff6600", font='Helvetica 14', width=40)
        self.entry.pack(side=LEFT, padx=10)
        self.entry.bind("<Return>", lambda event: self.send_msg())

        send_btn = Button(input_frame, text="Send", font='Helvetica 13 bold', bg='#ff6600', command=self.send_msg)
        send_btn.pack(side=LEFT, padx=5)

        send_img_btn = Button(input_frame, text="Send Image", font='Helvetica 13 bold', bg='#008000', fg='white', command=self.send_image)
        send_img_btn.pack(side=LEFT, padx=5)

        # Подключаемся к серверу
        self.client = Client(self.host, self.port, self.username, self.receive_msg)

    def send_msg(self):
        user_text = self.entry.get().strip()
        if user_text:
            time_str = time.strftime('%H:%M')
            self.display_msg(f"You -> {user_text} [{time_str}]")
            self.client.send_message(user_text)
            self.entry.delete(0, END)

    def send_image(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if not filepath:
            return
        try:
            with open(filepath, "rb") as img_file:
                img_bytes = img_file.read()
            img_b64 = base64.b64encode(img_bytes).decode('utf-8')
            self.client.send_image(img_b64)
            time_str = time.strftime('%H:%M')
            self.display_msg(f"You -> [Image sent] [{time_str}]")
        except Exception as e:
            self.display_msg(f"[Error sending image: {e}]")

    def receive_msg(self, message):
        try:
            msg_dict = json.loads(message)
            msg_type = msg_dict.get("type", "text")
            sender = msg_dict.get("sender", "Unknown")

            if msg_type == "text":
                text = msg_dict.get("data", "")
                time_str = time.strftime('%H:%M')
                self.display_msg(f"{sender}: {text} [{time_str}]")

            elif msg_type == "image":
                img_b64 = msg_dict.get("data", "")
                self.display_image(sender, img_b64)

            else:
                self.display_msg("[Unknown message type received]")

        except Exception:
            # Если не JSON — выводим как обычный текст
            time_str = time.strftime('%H:%M')
            self.display_msg(f"{message} [{time_str}]")

    def display_msg(self, message):
        self.txt.config(state=NORMAL)
        self.txt.insert(END, f"\n{message}")
        self.txt.config(state=DISABLED)
        self.txt.see(END)

    def display_image(self, sender, img_b64):
        try:
            img_data = base64.b64decode(img_b64)
            image = Image.open(io.BytesIO(img_data))

            time_str = time.strftime('%H:%M')
            self.display_msg(f"{sender} sent an image [{time_str}]")

            # Открыть картинку в отдельном окне
            self.open_image_window(image)

        except Exception as e:
            self.display_msg(f"[Error displaying image: {e}]")

    def open_image_window(self, pil_image):
        win = Toplevel(self.root)
        win.title("Received Image")

        # Масштабируем если слишком большая (максимум 600x600)
        pil_image.thumbnail((600, 600))

        photo = ImageTk.PhotoImage(pil_image)

        label = Label(win, image=photo)
        label.image = photo  # сохранить, чтобы не удалился
        label.pack()


if __name__ == '__main__':
    ChatGUI('192.168.55.16', 12346)  # Подставь IP и порт сервера
