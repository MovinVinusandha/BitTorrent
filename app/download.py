import struct

from app.Download.HandshakeValidator import HandshakeValidator
from app.handshakeMsg import HandshakeMsg
from app.messages import Messages
from app.Download.NetworkConnectionManager import NetworkConnectionManager
from app.Download.PieceDownloader import PieceDownloader
from app.Download.DataReceiver import DataReceiver
from app.Download.PieceValidator import PieceValidator

class Download:
    def __init__(self, peers_pieces, torrent_read_class, handshake_handler):
        self.torrent_data = torrent_read_class
        self.handshake = HandshakeMsg(torrent_read_class)
        self.peerPieces = peers_pieces
        self.already_downloaded_pieces = []
        self.handshake_handler = handshake_handler
        self.handshake_validator = HandshakeValidator(handshake_handler.get_expected_info_hash())
        self.connection_manager = NetworkConnectionManager()
        self.data_receiver = DataReceiver()
        self.piece_validator = PieceValidator(self.torrent_data.return_full_data()["pieces hash"])

    def download(self, ip, port, pieces):
        print(f"\n=== Starting download from {ip}:{port} ===")
        connection = self.connection_manager.connect_to_peer(ip, port)

        with connection:
            print(f"\nConnect to {ip}")

            handshake_msg_response = self.handshake_handler.perform_handshake(connection.sock)
            if self.handshake_validator.validate_and_log(handshake_msg_response, f"{ip}:{port}"):
                self.peerPieces.bitfield(connection.sock)
                self.wait_for_unchoke(connection.sock)

                file = self.download_pieces(connection, pieces)

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
        piece_downloader = PieceDownloader(message, self.data_receiver)

        total_length = self.torrent_data.return_full_data()["length"]
        standard_piece_length = self.torrent_data.return_full_data()["piece length"]
        block_size = 16384

        full_file = b""
        for piece_index in available_pieces:
            if not piece_index in self.already_downloaded_pieces:

                # Calculate piece size
                piece_size = piece_downloader.calculate_piece_size(piece_index, total_length, standard_piece_length)
                # Download piece
                piece_data = piece_downloader.download_piece(soc, piece_index, piece_size)

                # Validate piece
                if self.piece_validator.validate_piece(piece_data, piece_index):
                    full_file += piece_data

                    message.have(piece_index)

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