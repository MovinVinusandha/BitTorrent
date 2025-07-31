import struct

from app.Download.HandshakeValidator import HandshakeValidator
from app.handshakeMsg import HandshakeMsg
from app.Download.MessageHandler import MessageHandler
from app.Download.NetworkConnectionManager import NetworkConnectionManager
from app.Download.PieceDownloader import PieceDownloader
from app.Download.DataReceiver import DataReceiver
from app.Download.PieceValidator import PieceValidator
from app.Download.DownloadProgressTracker import DownloadProgressTracker
from app.Download.FileAssembler import FileAssembler

class Download:
    def __init__(self, socket_with_pieces, peers_pieces, torrent_read_class, handshake_handler, output_file_path="./downloaded_file.txt"):
        self.torrent_data = torrent_read_class
        self.socket_with_pieces = socket_with_pieces
        self.handshake = HandshakeMsg(torrent_read_class)
        self.peerPieces = peers_pieces
        self.handshake_handler = handshake_handler
        self.handshake_validator = HandshakeValidator(handshake_handler.get_expected_info_hash())
        self.connection_manager = NetworkConnectionManager()

        # Get torrent information
        full_data = self.torrent_data.return_full_data()
        total_length = full_data["length"]
        piece_length = full_data["piece length"]
        total_pieces = (total_length + piece_length - 1) // piece_length

        self.data_receiver = DataReceiver()
        self.piece_validator = PieceValidator(full_data["pieces hash"])
        self.progress_tracker = DownloadProgressTracker(total_pieces)
        self.file_assembler = FileAssembler(output_file_path)

        self.full_download()

    def full_download(self):

        for ip_port, pieces_index in self.socket_with_pieces.items():
            ip, port = ip_port.split(":")
            file = self.download(ip, int(port), pieces_index)

            self.file_assembler.save_to_file(file)

    def download(self, ip, port, pieces):
        print(f"\n=== Starting download from {ip}:{port} ===")
        connection = self.connection_manager.connect_to_peer(ip, port)

        with connection:

            handshake_msg_response = self.handshake_handler.perform_handshake(connection.sock)
            if self.handshake_validator.validate_and_log(handshake_msg_response, f"{ip}:{port}"):
                self.peerPieces.bitfield(connection.sock)
                self.wait_for_unchoke(connection.sock)

                self.download_pieces(connection, pieces)

                return self.file_assembler.assemble_file()
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
        message = MessageHandler(soc)
        piece_downloader = PieceDownloader(message, self.data_receiver)

        total_length = self.torrent_data.return_full_data()["length"]
        standard_piece_length = self.torrent_data.return_full_data()["piece length"]

        # Get pieces that still need downloading
        remaining_pieces = self.progress_tracker.get_remaining_pieces(available_pieces)

        for piece_index in remaining_pieces:
            # Track piece start
            self.progress_tracker.mark_piece_started(piece_index)

            # Calculate piece size
            piece_size = piece_downloader.calculate_piece_size(piece_index, total_length, standard_piece_length)
            # Download piece
            piece_data = piece_downloader.download_piece(soc, piece_index, piece_size)

            # Validate piece
            if self.piece_validator.validate_piece(piece_data, piece_index):
                # Add to assembler
                self.file_assembler.add_piece(piece_index, piece_data)

                # Update progress
                self.progress_tracker.mark_piece_completed(piece_index, piece_size)
                message.have(piece_index)

            else:
                self.progress_tracker.mark_piece_failed(piece_index)
                print(f"Piece {piece_index} hash validation failed!")

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