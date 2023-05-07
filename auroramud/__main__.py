import server
host='0.0.0.0'
port=6000

def main(host, port):
    server.Server(host, port)

main(host, port)