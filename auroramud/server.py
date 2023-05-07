import sys
import socket
import selectors
import types
import sqlite3 as sql
from sqlite3 import Error

from . import game
from .entities import player

class Server(object):
    def __init__(self, host, port):
        self.selector = selectors.DefaultSelector()
        self.db = sql.connect(r"./auroramud.db")
        self.db_cursor = self.db.cursor()
        self.db_cursor.execute("""CREATE TABLE IF NOT EXISTS accounts (
            name text NOT NULL,
            password text NOT NULL,
            immortle_character bool DEFAULT(FALSE),
            address text NOT NULL,
            career text NOT NULL,
            description text DEFAULT('In character creation'),
            location text
        );""")
        self.host = str(host)
        self.port = int(port)

        self.game = game.Game(self)
        self.connections={}

        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind((host, port))
        self.listener.listen()
        self.listener.setblocking(False)

        self.selector.register(self.listener, selectors.EVENT_READ, data=None)
        try: self.event_loop()
        except KeyboardInterrupt: 
             self.selector.close()
             self.db.close()
             sys.exit()

    def event_loop(self):
        while True:
            events = self.selector.select(timeout=None)
            for key, mask in events:    
                if key.data is None:
                    self.accept_wrapper(key.fileobj)
                else:
                    self.service_connection(key, mask)

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.selector.register(conn, events=events, data=data)
        self.connections[conn]=player.Player(self, conn, addr)
        conn.send(b"\tWelcome to aurora MUD!\nType `login` to login to an existing account \nor \ntype `create` to create a new account.\n\n")


    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)
            if recv_data: 
                data.outb += recv_data
            else: 
                self.selector.unregister(sock)
                sock.close()
        #if mask & selectors.EVENT_WRITE:
            if data.outb and data.outb.endswith(b"\n"):
                sent = sock.send(data.outb)
                self.game.handle_socket_state(sock, data.outb)
                data.outb=data.outb[sent:]

    def send(self,text):
        for i in self.connections:
            if self.connections[i].is_logged_in(): self.connections[i].send(text)



