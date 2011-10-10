from gevent import spawn
from gevent.socket import create_connection
from gevent.server import StreamServer
from gevent.queue import Queue
import json


EXIT_HOST = 5001
EXIT_PORT = 5001
LISTEN_INTERFACE = "0.0.0.0"
LISTEN_PORT = 5000

all_sessions = {}


class Session(object):
    def __init__ (self, host, port):
        self.clients = {}
        # Store the target info
        self.target_host
        self.target_port


    def start(self):
        # Connect to the target
        self.target = create_connection(self.target)
        # Stream client <- self <- target
        self.stream(self.target, self.incoming)
        # Stream client -> self -> target
        self.stream(self.current_client, self.outgoing)


    def outgoing(self, data):
        print "Sending data: %s" % data
        self.current_client.send(data)

    def incoming(self, data, endpoint=None):
        print "Received data form %s: %s" % (endpoint, data)
        self.target.send(data)

    
    def register_client(self, socket, host, port):
        """
        Registers a client-connected socket with this Session,
        which is described by the given host and port.
        """

        self.clients[(host, port)] = socket
        self.current_client = socket


    @classmethod
    def _stream(cls, source, handler, *args):
        print "New session started."
        while True:
            handler(source.recv(4096), *args)
    
    @classmethod
    def stream(cls, source, handler, *args):
        spawn(cls._stream, source, handler, *args)




def spawn_handler(*args):
    """ Spawn handle_connection in a green thread. """
    spawn(handle_connection, *args)


def handle_connection(socket, address):
    """ Handle a new BaseServer connection. """
    
    print ("New connection from %s:%s" % address)
    host, port = address
    # Read in the request as JSON
    request = json.loads(socket.recv(4096))
    # If the client needs to start a new Session...
    if request["action"] == "new":
        # Start a new Session with the given request and socket
        target = sesion["target"]
        session = Session(target["host"], target["port"])
        session.register(socket, host, port)
        # Get the Session's ID, and store the Session under it
        sid = session.id
        all_sessions[sid] = session
        # Also, give the client the Session ID for use in future connections
        socket.send(json.dumps({
            "status": "OK",
            "session_id": sid
        }))
        # At this point, the client should start streaming data,
        # which we'll let the Session object handle
        session.start()
    # If the client want's to join an existing Session...
    elif request["action"] == "join":
        # Try to register this socket with the right Session
        try:
            sid = request["session_id"]
            s = all_sessions[sid]
            # Register this socket with the session
            s.register(socket)
            # All set
            socket.send(json.dumps({
                "status": "OK",
                "session_id": sid
            }))
        # No luck
        except KeyError:
            socket.send(json.dumps({
                "status": "Error",
                "reason": "Invalid session_id"
            }))
            socket.send("Invalid session_id")
            socket.close()


if __name__ == "__main__":
    servers = {}
    servers[e] = StreamServer((LISTEN_INTERFACE, LISTEN_PORT), handle_connection)
    print ("Starting STCP server on port %s" % LISTEN_PORT)
    spawn(server.serve_forever)
