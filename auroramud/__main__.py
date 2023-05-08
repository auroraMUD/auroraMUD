import os
import signal
import sys

import server
host='0.0.0.0'
port=6000

srv= None
def main(host, port):
    if not os.path.exists("./database/"):
        os.mkdir("./database/")
    
    srv = server.Server(host, port)
    signal.signal(signal.SIGTERM, handle_exit)


def handle_exit(signum, frame):
    print("bye bye")
    srv.send("Server is restarting, please hold\n\n\n")
    os.popen('cp ./database/auroramud.db ./database/auroramud.db.backup')
    srv.db.close()
    for i in srv.connections:
        srv.connections[i].disconnect()
    srv.listener.close()
    srv.selector.close()
    del srv
    sys.exit(0)



main(host, port)