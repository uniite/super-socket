from gevent import spawn, spawn_later
from gevent.event import Event
from gevent.socket import create_connection
from gevent.server import StreamServer
from gevent.queue import Queue
from gevent import sleep

from proxy_core import ProxyCore


ENTRY_HOST = "127.0.0.1"
ENTRY_PORT = 5001
ENDPOINTS = [
    ("127.0.0.1", 5000)
]



class Connection(ProxyCore):
    def reconnect(self):
        addr = self.current_endpoint.split(":")
        self.endpoints[self.current_endpoint] = create_connection(addr)
    


def start_session(client_socket, address):
    print ("New connection from %s:%s" % address)
    # Connect to the server
    server_socket = Connection(client_socket, ENDPOINTS)
    # Stream client -> server
    #Connection.stream(client_socket, server_socket)
    # Stream client <- server
    #spawn(stream, server_socket, client_socket)
    


if __name__ == "__main__":
    server = StreamServer((ENTRY_HOST, ENTRY_PORT), start_session)
    print ("Starting STCP server on port %s" % ENTRY_PORT)
    server.serve_forever()
