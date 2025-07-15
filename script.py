from tkinter import *
import time
import datetime

# Create window and title
root = Tk()
root.title('Renichat')

# Remove the default title bar
root.overrideredirect(True)

# Set window dimensions
window_width = 700
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
root.config(bg="black")

# Custom title bar
title_bar = Frame(root, bg='orange', relief='raised', bd=0)
title_bar.pack(fill=X)

# Title label (optional)
title_label = Label(title_bar, text='RENICHAT', bg='orange', fg='black', font='stencil')
title_label.pack(side=LEFT, padx=10)

# Close button
close_button = Button(title_bar, text='X', command=root.destroy, bg='red', fg='white', bd=0, padx=5, pady=2)
close_button.pack(side=RIGHT)

# Bind the window drag to title bar
def move_window(event):
    root.geometry(f'+{event.x_root}+{event.y_root}')

title_bar.bind('<B1-Motion>', move_window)
title_label.bind('<B1-Motion>', move_window)

# Colours and fonts
BG_COLOUR = '#000000'
BUTTON_COLOUR = '#ffa500'
TEXT_COLOUR = '#ffa500'
FONT = 'Helvetica 10'
FONT_BOLD = 'Helvetica 9 bold'

# Chat text area
txt = Text(root, bg=BG_COLOUR, fg=TEXT_COLOUR, font=FONT, width=60)
txt.pack(padx=10, pady=(5, 0), fill=BOTH, expand=True)

# Entry and send button frame
input_frame = Frame(root, bg=BG_COLOUR)
input_frame.pack(fill=X, pady=10)

# Message entry
e = Entry(input_frame, bg="#2C3E50", fg=TEXT_COLOUR, font=(FONT, 12), width=55)
e.pack(side=LEFT, padx=10)

# Send function, when the send button is pressed the message is displayed 
def send_msg():
    user_text = e.get()
    if user_text.strip() != '':
        date = time.strftime('%H:%M')
        txt.insert(END, f"\nYou -> {user_text} [{date}]")
        e.delete(0, END)

# Send button
send_btn = Button(input_frame, text="Send", font=(FONT_BOLD, 25), bg=TEXT_COLOUR, command=send_msg)
send_btn.pack(side=LEFT, padx=5)

# Run the application
root.mainloop()
