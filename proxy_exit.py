from gevent import spawn, spawn_later
from gevent.event import Event
from gevent.socket import create_connection
from gevent.server import StreamServer
from gevent.queue import Queue
from gevent import sleep

from proxy_core import ProxyCore


ENTRY_HOST = "0.0.0.0"
ENTRY_PORT = 5000
ENDPOINTS = [
    ("127.0.0.1", 5005)
]

current_connection = None


class Connection(ProxyCore):
    def reconnect(self):
        self.connected.wait()



def kill_connection():
    print "Killing connection!"
    current_connection.endpoints["client"].close()


def start_session(client_socket, address):
    global current_connection
    print ("New connection from %s:%s" % address)
    # Connect to the server
    if not current_connection:
        current_connection = Connection(client_socket, ENDPOINTS)
        spawn_later(5.5, kill_connection)
    else:
        print "Got new connection!"
        current_connection.endpoints["client"] = client_socket
        current_connection.connected.set()
    # Stream client -> server
    #Connection.stream(client_socket, server_socket)
    # Stream client <- server
    #spawn(stream, server_socket, client_socket)
    


if __name__ == "__main__":
    server = StreamServer((ENTRY_HOST, ENTRY_PORT), start_session)
    print ("Starting STCP server on port %s" % ENTRY_PORT)
    server.serve_forever()
