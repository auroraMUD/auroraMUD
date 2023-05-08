import os
import sys

import server
host='0.0.0.0'
port=6000

srv= None
def main(host, port):
    if not os.path.exists("./database/"):
        os.mkdir("./database/")
    srv = server.Server(host, port)




main(host, port)