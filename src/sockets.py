import socket
import threading
import queue
import tkinter

class P2PSocket():
    def __init__(self, timeout=1):
        
        self.timeout = timeout
        self.recv_rest = None
    
    def connect(self, address, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((address, port))
            self.address = address
            self.ishost = False
            self.conn, self.address = None, None
            self.sock.settimeout(self.timeout)
            print("is client")
        except:
            print("is server")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(('', port))
            self.sock.listen()
            launched = True
            while launched:
                self.conn, self.address = self.sock.accept()
                if self.conn is not None:
                    launched = False
            self.ishost = True
            self.conn.settimeout(self.timeout)
            self.sock.settimeout(self.timeout)
            print("connected to", self.address)
    
    def send(self, msg):
        if self.ishost:
            self.conn.sendall(chr(len(msg)).encode("utf8")+msg.encode("utf8"))
            #print("send :", chr(len(msg)), f"{chr(len(msg))}{msg}".encode("utf8"))
        else:
            self.sock.sendall(chr(len(msg)).encode("utf8")+msg.encode("utf8"))
            #print("send :", chr(len(msg)), f"{chr(len(msg))}{msg}".encode("utf8"))
    
    
    def recv(self):
        #récupération de la taille de la chaine
        if self.ishost:
            data_size = self.conn.recv(1)
            if data_size == b'':
                return
            data_size = ord(data_size.decode("utf8"))
        else:
            data_size = self.sock.recv(1)
            if data_size == b'':
                return
            data_size = ord(data_size.decode("utf8"))
        
        #récupération de mes données
        if self.ishost:
            data = self.conn.recv(data_size)
        else:
            data = self.sock.recv(data_size)
        #print(f'{data_size} == {len(data.decode("utf8"))}')
        
        #retour
        return data.decode("utf8")
    def close(self):
        try:
            self.conn.close()
        except:
            pass
        self.sock.close()

class p2pSocketThread(threading.Thread):
    def __init__(self, address, port, timeout, window):
        threading.Thread.__init__(self)
        
        self.timeout = timeout
        self.address = address
        self.port = port
        self.window = window

        self.sock = P2PSocket(self.timeout)
        self.sock.connect(self.address, self.port)

        self.recv_queue = queue.Queue(0)
        self.must_stop = False
    def run(self):
        self.launched = True
        while self.launched:
            try:
                recv = self.sock.recv()
                if recv is not None:
                    self.recv_queue.put(recv)
                    self.window.event_generate("<<new_recv>>")

            except socket.timeout as e:
                #print(e)
                if self.must_stop:
                    self.launched = False
                    self.sock.close()
            except:
                self.launched = False
                self.sock.close()

    def stop(self):
        self.must_stop = True
        self.launched = False
        self.sock.close()

    """
    def get_recv_queue(self):
        launched = True
        recv_list = []
        while launched:
            try:
                recv_list.append(self.recv_queue.get())
                self.recv_queue.task_done()
            except queue.Empty as e:
                launched = False
        return recv_list
    """
    def send(self, msg):
        self.sock.send(msg)
        
        