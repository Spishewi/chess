from tkinter.ttk import Style
from src.menu import *
import src.my_globals as my_globals

if __name__ == "__main__":
    my_globals.init()
    root = tk.Tk()
    app = Menu(master=root)
    app.mainloop()