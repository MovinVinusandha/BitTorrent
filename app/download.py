import socket
import struct

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

            protocol_str_len, protocol_str, reserved_bytes, info_hash, peer_id = struct.unpack(
                f'b{self.handshake.protocol_str_len}s8s20s20s',
                handshake_reply
            )

            if info_hash == self.handshake.info_hash:
                msg = struct.pack("Ib", 1, 2)
                soc.send(msg)
                bitfield = soc.recv(68)
                print(self.decode_bitfield(bitfield))

                msg = self.recv_exact(soc, 5)

                length, msg_id = struct.unpack(">IB", msg)
                if msg_id != 1:
                    raise Exception("Expected unchoke")

            else:
                print("info hash not equal")

    def decode_bitfield(self, data):
        bitfield_bytes = data[5:]
        return ''.join(f'{byte:08b}' for byte in bitfield_bytes)

    def recv_exact(self, soc, total_len):
        data = b''
        while len(data) < total_len:
            chunk = soc.recv(total_len - len(data))
            if not chunk:
                raise Exception("Connection closed unexpectedly")
            data += chunk
        return data