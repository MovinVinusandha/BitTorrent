import hashlib
import socket
import struct
import sys

from app.handshakeMsg import HandshakeMsg
from app.peers import Peers
from app.messages import Messages
from app.torrentRead import TorrentRead

class Download:
    def __init__(self):
        self.torrent_file = sys.argv[2]
        self.torrent_read = TorrentRead(self.torrent_file)
        self.torrent_data = TorrentRead(self.torrent_file)
        self.peers = Peers()
        self.handshake = HandshakeMsg()
        self.ip, self.port = self.peers.gen_peers_ip()[0].split(":")
        self.sock = None

    def __enter__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ip, int(self.port)))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.sock:
            self.sock.close()

    def determine_download_sequence(self):
        with Download() as down:
            handshake_msg_response = self.handshake_connection(down.sock)

            if handshake_msg_response["info_hash"] == self.handshake.info_hash:
                available_pieces = self.bitfield(down.sock)
                self.wait_for_unchoke(down.sock)
                self.download_pieces(down.sock, available_pieces)

            else:
                print("Invalid Hash")

    def handshake_connection(self, soc):
        """Return dictionary containing parsed handshake message response"""
        soc.send(self.handshake.handshake_msg())
        return self.handshake.handshake_msg_unpack(soc)

    def bitfield(self, soc):
        """Return list of available piece indexes extracted from bitfield"""
        message = Messages(soc)
        bitfield = message.interested()

        bitfield_str = self.decode_bitfield(bitfield)
        return [i for i, bit in enumerate(bitfield_str) if bit == '1']

    def wait_for_unchoke(self, soc):
        """Verify peer has unchoked us; raise exception if still choked"""
        msg = self.recv_exact(soc, 5)
        length, msg_id = struct.unpack(">IB", msg)
        if msg_id != 1:
            raise Exception("Expected unchoke")

    def download_pieces(self, soc, available_pieces):
        """Return byte string containing downloaded piece data"""
        message = Messages(soc)

        full_length = self.torrent_data.return_full_data()["length"]
        standard_piece_length = self.torrent_data.return_full_data()["piece length"]
        block_size = 16384

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

                message.request(piece_index, begin, block_len)

                response = self.recv_exact(soc, 13 + block_len)
                block_data = response[13:]

                piece_data += block_data

            piece_hash = hashlib.sha1(piece_data).hexdigest()
            expected_hash = self.torrent_data.return_full_data()["pieces hash"][piece_index]

            if piece_hash == expected_hash:
                full_file += piece_data

                have_msg = struct.pack(">IbI", 5, 4, piece_index)
                soc.sendall(have_msg)
            else:
                print(f"Piece {piece_index} hash validation failed!")

        return full_file

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