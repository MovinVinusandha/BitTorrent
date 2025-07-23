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
        """Establish TCP connection with peer, perform handshake, download entire file, and save it"""
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

                msg = self.recv_exact(soc, 5)
                length, msg_id = struct.unpack(">IB", msg)
                if msg_id != 1:
                    raise Exception("Expected unchoke")

                full_length = self.torrent_read.get_data()["length"]
                standard_piece_length = self.torrent_read.get_data()["piece length"]
                block_size = 16384

                bitfield_str = self.decode_bitfield(bitfield)
                available_pieces = [i for i, bit in enumerate(bitfield_str) if bit == '1']

                full_file = b""
                for piece_index in available_pieces:
                    print(f"Downloading piece index: {piece_index}")

                    total_pieces = (full_length + standard_piece_length - 1) // standard_piece_length
                    if piece_index == total_pieces - 1:
                        piece_size = self.get_last_piece_length(full_length, standard_piece_length)
                    else:
                        piece_size = standard_piece_length

                    piece_data = b""
                    for begin in range(0, piece_size, block_size):
                        block_len = min(block_size, piece_size - begin)

                        msg = struct.pack(">IbIII", 13, 6, piece_index, begin, block_len)
                        soc.sendall(msg)

                        response = self.recv_exact(soc, 13 + block_len)
                        block_data = response[13:]

                        piece_data += block_data

                    piece_hash = hashlib.sha1(piece_data).hexdigest()
                    expected_hash = self.hash.get_data()["pieces hash"][piece_index]

                    if piece_hash == expected_hash:
                        full_file += piece_data

                        have_msg = struct.pack(">IbI", 5, 4, piece_index)
                        soc.sendall(have_msg)
                    else:
                        print(f"Piece {piece_index} hash validation failed!")

                with open("./downloaded_file.txt", "wb") as f:
                    f.write(full_file)
                    print("---File downloaded successfully---")

            else:
                print("Info hash mismatch")

    def get_last_piece_length(self, total_length, piece_length):
        """Return integer representing the length of the last piece"""
        remainder = total_length % piece_length
        return remainder if remainder != 0 else piece_length

    def decode_bitfield(self, data):
        """Return decoded bitfield as a string"""
        bitfield_bytes = data[5:]
        return ''.join(f'{byte:08b}' for byte in bitfield_bytes)

    def recv_exact(self, soc, total_len):
        """Return bytes object of length total_len read from socket, blocking until complete"""
        data = b''
        while len(data) < total_len:
            chunk = soc.recv(total_len - len(data))
            if not chunk:
                raise Exception("Connection closed unexpectedly")
            data += chunk
        return data