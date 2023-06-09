
class Player():
    def __init__(self, server, socket, address):
        self.socket=socket
        self.address=address
        self.state='connected'
        self.server=server
        self.name=""
        self.password=""
        self.immortle_character=False
        self.career=""
        self.description=""
        self.location=""
    
    def send(self, text):
        try: self.socket.sendall(bytearray(text, 'utf-8'))
        except: self.disconnect()


    def is_logged_in(self):
        return True if self.state=='logged_in' else False 

    def save(self):
        self.server.db_cursor.execute(f"""UPDATE accounts SET
        name={self.name},
        password={self.password},
        immortle_character={self.immortle_character},
        address={self.address},
        description={self.description},
        location={self.location};
        """)
        self.server.db.commit()

    def disconnect(self):
        try: self.server.selector.unregister(self.socket)
        except: pass
        self.server.connections.pop(self.socket)
        try: self.socket.close()
        except: pass
        del self