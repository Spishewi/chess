import queue
from tkinter import  Toplevel, ttk
import tkinter as tk
from tkinter import scrolledtext
from tkinter.constants import NO
from tkinter.simpledialog import askstring
import src.sockets as sockets
import json
import src.game as game
import src.my_globals as my_globals

class Menu(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.close)
        self.pack()
        self.master_canvas = tk.Canvas(self.master)
        self.choose_connection_menu()
        self.master.resizable(False, False)
        self.theme = json.load(open("theme/theme.json"))
        print(self.theme)

    def choose_connection_menu(self):
        self.master_canvas.destroy()
        self.master_canvas = tk.Canvas(self.master, bd=0, highlightthickness=0)
        self.master.geometry("200x145")

        self.host_entry_label = ttk.Label(self.master_canvas, text="enter here the host IP :")
        
        self.host_entry = ttk.Entry(self.master_canvas)
        self.host_entry.insert(0, "127.0.0.1")
        self.port_entry_label = ttk.Label(self.master_canvas, text="enter here the port :")
        self.port_entry = ttk.Entry(self.master_canvas)
        self.port_entry.insert(0, "5566")
        self.connect_button = ttk.Button(self.master_canvas, text="Connect", command=self.connect)
        self.quit_button = ttk.Button(self.master_canvas, text="quit", command=self.close)

        self.host_entry_label.pack()
        self.host_entry.pack()
        self.port_entry_label.pack()
        self.port_entry.pack()
        self.connect_button.pack()
        self.quit_button.pack()

        self.master_canvas.pack(expand=True, fill=tk.BOTH)

    def connect(self):
        self.connect_button.config(state=tk.DISABLED)
        self.sock = sockets.p2pSocketThread(self.host_entry.get(), int(self.port_entry.get()), 0.001, self.master)
        self.sock.start()
        self.sock.send("connected")
        if self.sock.sock.ishost:
            self.master.title("host")
            self.choose_gamemode_window()
            
        else:
            self.master.title("client")
            self.game_window()

    def close(self):
        try:
            self.sock.stop()
        except:
            pass
        self.master.destroy()
        print("destroyed")

    def game_window(self, gamemode=None):
        
        print(gamemode)
        def new_recv_handler(e):
            while True:
                try:
                    new_recv = self.sock.recv_queue.get_nowait()
                except queue.Empty:
                    break
                else:
                    self.game_instance.handle_socket_message(new_recv)
                
                    
                
        self.master_canvas.destroy()
        self.master_canvas = tk.Canvas(self.master, bd=0, highlightthickness=0)
        self.master.bind('<<new_recv>>', new_recv_handler)
        self.master.resizable(False, False)

        case_size = self.theme['theme']['case_size']
        if case_size < 55:
            case_size=55
        
        
        self.game_canvas = tk.Canvas(self.master_canvas, width=8*case_size, height=8*case_size, bd=1, highlightthickness=0, relief=tk.GROOVE)

        self.game_instance = game.ChessBase(self.game_canvas, gamemode, self.theme, self.sock.send, self)

        

        #ttk.Button(text="test", command=lambda: self.sock.send("test")).pack()
        #self.chat_text_frame.grid(x=20+case_size*8, y=80)
        self.chessboard_read_label_y = []
        if gamemode == None:
            tmp = [1, 2, 3, 4, 5, 6, 7, 8]
        else:
            tmp = [8, 7, 6, 5, 4, 3, 2, 1]
        for i in tmp:
            self.chessboard_read_label_y.append(ttk.Label(self.master_canvas, text=i))
        for i in self.chessboard_read_label_y:
            i.grid(column=0, row=self.chessboard_read_label_y.index(i)+1)
            i.update()
        
        self.chessboard_read_label_x = []
        if gamemode == None:
            tmp = ["h", "g", "f", "e", "d", "c", "b", "a"]
        else:
            tmp = ["a", "b", "c", "d", "e", "f", "g", "h"]
        
        for i in tmp:
            self.chessboard_read_label_x.append(ttk.Label(self.master_canvas, text=i))
        for i in self.chessboard_read_label_x:
            i.grid(column=self.chessboard_read_label_x.index(i)+1, row=9)
            i.update()

        self.buttons_frame = tk.Frame(self.master_canvas, padx=20, pady=10)

        self.file_frame = ttk.Labelframe(self.buttons_frame, text="file")
        self.fonctions_frame = ttk.Labelframe(self.buttons_frame, text="options")

        self.save_button = ttk.Button(self.file_frame, text="save game")
        self.save_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.undo_button = ttk.Button(self.fonctions_frame, text="undo move")
        self.undo_button.grid(column=1, row=0, padx=5, pady=5)

        self.propose_equality_button = ttk.Button(self.fonctions_frame, text="propose an equality")
        self.propose_equality_button.grid(column=2, row=0)

        self.abandon_button = ttk.Button(self.fonctions_frame, text="give up")
        self.abandon_button.grid(column=3, row=0, padx=5, pady=5)


        #self.file_frame.grid(column=0, row=0, padx=5)
        self.fonctions_frame.grid(column=1, row=0, padx=5)
        self.buttons_frame.grid(column=1, row=0, columnspan=8)
        self.buttons_frame.update()
        
        self.master.geometry(f"{case_size*8+self.chessboard_read_label_y[0].winfo_width()}x{case_size*8+self.chessboard_read_label_x[0].winfo_height()+self.buttons_frame.winfo_height()}")
        self.game_canvas.grid(column=1, row=1, columnspan=8, rowspan=8)
        self.master_canvas.pack(expand=True, fill=tk.BOTH)
        

        

    def choose_gamemode_window(self):
        self.master_canvas.destroy()
        self.master_canvas = tk.Canvas(self.master, bd=0, highlightthickness=0)
        self.master.resizable(False, False)
        self.master.geometry('200x235')

        gamemodes = my_globals.gamemodes
        def validate():
            item_selected = self.choice_listbox.curselection()
            if item_selected is not tuple():
                self.game_window(gamemode=self.choice_listbox.get(item_selected[0]))
            
        title_label = ttk.Label(self.master_canvas, text="You are the host,\nplease choose the gamemode.")
        self.choice_listbox = tk.Listbox(self.master_canvas, activestyle=tk.UNDERLINE, relief=tk.GROOVE, selectmode=tk.SINGLE)
        submit_button = ttk.Button(self.master_canvas, text="Validate", command=validate)

        for i in gamemodes:
            self.choice_listbox.insert(0, i)

        title_label.pack()
        self.choice_listbox.pack()
        submit_button.pack()

        self.master_canvas.pack(expand=True, fill=tk.BOTH)