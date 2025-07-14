from tkinter import *

#create window and title
root = Tk()
root.title('Renichat')

window_width = 700
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)

root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

#colours
BG_COLOUR = '#000000'
BUTTON_COLOUR = '#ffa500'
TEXT_COLOUR = '#ffa500'
FONT = 'Helvetica 14'
FONT_BOLD = 'Helvetica 13 bold'
root.config(bg="black")

# Send function
def send():
    send = "You -> " + e.get()
    txt.insert(END, "\n" + send)
    e.delete(0, END)


txt = Text(root, bg=BG_COLOUR, fg=TEXT_COLOUR, font=FONT, width=60)
txt.grid(row=1, column=0, columnspan=2)

send = Button(root, text="Send", font=FONT_BOLD, bg=TEXT_COLOUR, command=send).grid(row=2, column=1)

e = Entry(root, bg="#2C3E50", fg=TEXT_COLOUR, font=FONT, width=55)
e.grid(row=2, column=0)







#end program
root.mainloop()


