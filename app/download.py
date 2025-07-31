import hashlib
import struct

from app.Download.HandshakeValidator import HandshakeValidator
from app.handshakeMsg import HandshakeMsg
from app.messages import Messages
from app.Download.NetworkConnectionManager import NetworkConnectionManager

class Download:
    def __init__(self, peers_pieces, torrent_read_class, handshake_handler):
        self.torrent_data = torrent_read_class
        self.handshake = HandshakeMsg(torrent_read_class)
        self.peerPieces = peers_pieces
        self.already_downloaded_pieces = []
        self.handshake_handler = handshake_handler
        self.handshake_validator = HandshakeValidator(handshake_handler.get_expected_info_hash())
        self.connection_manager = NetworkConnectionManager()

    def download(self, ip, port, pieces):
        print(f"\n=== Starting download from {ip}:{port} ===")
        connection = self.connection_manager.connect_to_peer(ip, port)

        with connection:
            print(f"\nConnect to {ip}")

            handshake_msg_response = self.handshake_handler.perform_handshake(connection.sock)
            if self.handshake_validator.validate_and_log(handshake_msg_response, f"{ip}:{port}"):
                self.peerPieces.bitfield(connection.sock)
                self.wait_for_unchoke(connection.sock)

                file = self.download_pieces(connection.sock, pieces)

                return file
            else:
                print("handshake validate fail")
                return None

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
            if not piece_index in self.already_downloaded_pieces:
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

                    self.already_downloaded_pieces.append(piece_index)
                else:
                    print(f"Piece {piece_index} hash validation failed!")

        return full_file

    def get_last_piece_length(self, total_length, piece_length):
        """Return integer representing the length of the last piece"""
        remainder = total_length % piece_length
        return remainder if remainder != 0 else piece_length

    def recv_exact(self, soc, total_len):
        """Return bytes object of length total_len read from socket, blocking until complete"""
        data = b''
        while len(data) < total_len:
            chunk = soc.recv(total_len - len(data))
            if not chunk:
                raise Exception("Connection closed unexpectedly")
            data += chunk
        return data