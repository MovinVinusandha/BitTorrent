import socket

class Socket:
    def __init__(self, ip, port, timeout=5.0):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.sock = None

    def connect(self):
        """Establishes a TCP connection to the specified IP and port."""
        self.sock = socket.create_connection((self.ip, int(self.port)), timeout=self.timeout)
        return self

    def close(self):
        """Closes the socket connection if it is open."""
        if self.sock:
            self.sock.close()
            self.sock = None