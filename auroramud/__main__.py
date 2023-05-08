import os
import server
host='0.0.0.0'
port=6000


def main(host, port):
    srv=None
    if not os.path.exists("./database/"):
        os.mkdir("./database/")
    try:
        srv=server.Server(host, port)
    except KeyboardInterrupt:
        os.popen('cp ./database/auroramud.db ./database/auroramud.db.backup')
        srv.db.close()
        for i in srv.connections:
            srv.connections[i].disconnect()
        srv.listener.close()
        del srv
        sys.exit()



main(host, port)