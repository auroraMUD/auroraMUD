import sys
import os
import signal
import socket
import selectors
import types
import sqlite3 as sql
from sqlite3 import Error

import game
from entities import player

class Server(object):
    def __init__(self, host, port):
        self.selector = selectors.DefaultSelector()
        self.db = sql.connect(r"./database/auroramud.db")
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
        signal.signal(signal.SIGTERM, self.handle_exit)
        self.event_loop()

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



    def handle_exit(self,signum, frame):
        print("bye bye")
        self.send("Server is restarting, please hold\n\n\n")
        os.popen('cp ./database/auroramud.db ./database/auroramud.db.backup')
        self.db.close()
        for i in self.connections:
            self.connections[i].disconnect()
        self.selector.unregister(self.listener)
        self.listener.close()
        self.selector.close()
        sys.exit(0)


