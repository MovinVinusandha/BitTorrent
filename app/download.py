import hashlib
import socket
import struct
import sys

from app.hashGen import Hash
from app.torrentFile import TorrentRead
from app.handshakeMsg import HandshakeMsg
from app.peers import Peers

class Download:
    def __init__(self):
        self.torrent_file = sys.argv[2]
        self.torrent_read = TorrentRead(self.torrent_file)
        self.hash = Hash()
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

                full_length = self.torrent_read.get_data()["length"]
                piece_index = 0
                piece_length = self.torrent_read.get_data()["piece length"]
                block_size = 16384

                full_file = b""
                for begin in range(0, piece_length, block_size):
                    block_len = min(block_size, piece_length - begin)
                    msg = struct.pack(">IbIII", 13, 6, piece_index, begin, block_len)
                    soc.sendall(msg)
                    data = self.recv_exact(soc, 13 + block_len)

                    block = data[13:]

                    full_file += block

                msg = struct.pack(">IbI", 5, 4, piece_index)
                soc.sendall(msg)

                sh1 = hashlib.sha1()
                sh1.update(full_file)
                full_hash = sh1.hexdigest()
                piece_hash_list = self.hash.get_data()["pieces hash"]
                if full_hash == piece_hash_list[piece_index]:
                    print("--Piece Hash validate successfully--")
                else:
                    print("--Piece Hash validate unsuccessfully--")

                with open("./full file.txt", "wb") as f:
                    f.write(full_file)
                    print("--File create successfully--")

                with open("./full file.txt", "rb") as f:
                    file = f.read()
                    print("\n======================\tFile\t======================\n")
                    print(file)


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