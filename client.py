from gevent import socket
from time import sleep


if __name__ == '__main__':
    s = socket.create_connection(("127.0.0.1", 5001))
    i = 0
    while True:
        i += 1
        s.send("Tick%s\n" % i)
        print s.recv(4096)
        sleep(1)
