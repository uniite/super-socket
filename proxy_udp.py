from proxy_core import stream_udp
from gevent import spawn, sleep
from sys import argv




if __name__ == "__main__":
    if len(argv) > 1 and argv[1] == "server":
        SOURCE_ADDR = ("0.0.0.0", 38052)
        TARGET_ADDR = ("127.0.0.1", 443)
        stream_udp(SOURCE_ADDR, TARGET_ADDR)
    else:
        SOURCE_ADDR = ("0.0.0.0", 443)
        TARGET_ADDR = ("199.34.124.250", 38052)
        stream_udp(SOURCE_ADDR, TARGET_ADDR)
