import socket

from app.handshakeMsg import HandshakeMsg
from app.peers import Peers

class Download:
    def __init__(self):
        self.peers = Peers()
        self.handshake = HandshakeMsg()
        self.ip, self.port = self.peers.gen_peers_ip()[0].split(":")

    def handshake_connection(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
            soc.connect((self.ip, int(self.port)))
            soc.send(self.handshake.handshake_msg())

            handshake_reply = soc.recv(68)


