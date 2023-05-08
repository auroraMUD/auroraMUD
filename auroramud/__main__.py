import os
import server
host='0.0.0.0'
port=6000


def main(host, port):
    if not os.path.exists("./database/"):
        os.mkdir("./database/")
    try:
        server = server.Server(host, port)
    except KeyboardInterrupt:
        os.popen('cp ./database/auroramud.db ./database/auroramud.db.backup')
        server.db.close()
        for i in server.connections:
            server.connections[i].disconnect()
        server.listener.close()
        del server
        sys.exit()



main(host, port)