import os
import server
host='0.0.0.0'
port=6000


def main(host, port):
    if not os.path.exists("./database/"):
        os.makedirs("./database/")
    
    server.Server(host, port)

main(host, port)