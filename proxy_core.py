from gevent import spawn, spawn_later
from gevent.event import Event
from gevent.socket import create_connection
from gevent import socket
from gevent.server import StreamServer
from gevent.queue import Queue
from gevent import sleep


class ProxyCore(object):
    def __init__ (self, client, endpoints):
        """
        Set up a connection between the client_socket and multiple endpoints.

        endpoints should be an array of (host, port) pairs.
        """

        # We'll need these later
        self.client = client
        self.outgoing_queue = Queue()
        self.connected = Event()
        self.connected.set()
        # Setup the endpoint connections and store them
        self.endpoints = {}
        for host, port in endpoints:
            key = "%s:%s" % (host, port)
            # Connect to the endpoint
            endpoint = create_connection((host, port))
            # Stream client <- self <- endpoint
            self.stream(key, self.incoming, (host, port))
            # Store the endpoint
            self.endpoints[key] = endpoint
        # Pick which endpoint to use first
        self.current_endpoint = self.endpoints.keys()[0]
        self.endpoints["client"] = self.client
        # Stream client -> self -> endpoint
        self.stream("client", self.outgoing)


    def reconnect_and_send(self):
        try:
            print "Waiting for reconnection..."
            self.reconnect()
            print "Reconnection successful, sending..."
            while not self.outgoing_queue.empty():
                print "Sending queue item."
                handler, data, args = self.outgoing_queue.get()
                handler(data, *args)
            self.connected.set()
        except:
            print "Reconnect failed, trying again later..."
            spawn_later(1, self.reconnect_and_send)


    def outgoing(self, data):
        socket = self.endpoints[self.current_endpoint]
        socket.send(data)
        socket.flush()
        print "Sent data to %s: %s" % (self.current_endpoint, data)



    def incoming(self, data, endpoint=None):
        self.client.send(data)
        self.client.flush()
        print "Sent data to client: %s" % data


    def _stream(self, source, handler, *args):
        print "New stream started for source %s to %s" % (str(source), handler)
        while True:
            print "Streaming from %s" % source
            source_socket = self.endpoints[source]
            try:
                data = source_socket.recv(4096)
                if not data:
                    raise Exception()
                print "Got data from %s: %s" % (source, data)
                handler(data, *args)
            except Exception, e:
                print e
                print e.message
                if self.connected.is_set():
                    spawn_later(1, self.reconnect_and_send)
                    self.connected.clear()
                if data:
                    self.outgoing_queue.put((handler, data, args))
                print "Recv error, waiting for %s..." % source
                self.connected.wait()
                print "Restarting recv for %s..." % source
                sleep(1)


    def stream(self, source, handler, *args):
        spawn(self._stream, source, handler, *args)


def _stream_udp_incoming(source, target):
    while True:
        data, addr = source["socket"].recvfrom(65535)
        print "Recv from %s" % str(addr)
        target["socket"].sendto(data, target["addr"])

def _stream_udp(source, target):
    incoming_stream = None
    while True:
        data, addr = source["socket"].recvfrom(65535)
        print "Recv from %s" % str(addr)
        target["socket"].sendto(data, target["addr"])
        if incoming_stream == None:
            print "Setting up incoming stream"
            source["addr"] = addr
            incoming_stream = spawn(_stream_udp, target, source, {})

def stream_udp(bind_addr, target_addr):
    # Setup the sockets
    source = {
        "socket": socket.socket(socket.AF_INET, socket.SOCK_DGRAM),
        "addr": None
    }
    source["socket"].bind(bind_addr)
    target = {
        "socket": socket.socket(socket.AF_INET, socket.SOCK_DGRAM),
        "addr": target_addr
    }

    # Source -> Target
    _stream_udp(source, target)


