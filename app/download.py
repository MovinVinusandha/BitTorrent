from app.Download.handshake_validator import HandshakeValidator
from app.Download.peer_connection_setup import PeerConnectionSetup
from app.handshake_msg import HandshakeMsg
from app.Download.message_handler import MessageHandler
from app.Download.network_connection_manager import NetworkConnectionManager
from app.Download.piece_downloader import PieceDownloader
from app.Download.data_receiver import DataReceiver
from app.Download.piece_validator import PieceValidator
from app.Download.download_progress_tracker import DownloadProgressTracker
from app.Download.file_assembler import FileAssembler

class Download:
    def __init__(self, socket_with_pieces, peers_pieces, torrent_read_class, handshake_handler):
        self.socket_with_pieces = socket_with_pieces
        self.torrent_data = torrent_read_class

        self.handshake_handler = handshake_handler
        self.peerPieces = peers_pieces

        full_data = self.torrent_data.return_full_data()
        total_length = full_data["length"]
        piece_length = full_data["piece length"]
        total_pieces = (total_length + piece_length - 1) // piece_length

        self.handshake = HandshakeMsg(torrent_read_class)
        self.handshake_validator = HandshakeValidator(handshake_handler.get_expected_info_hash())
        self.connection_manager = NetworkConnectionManager()
        self.data_receiver = DataReceiver()
        self.piece_validator = PieceValidator(full_data["pieces hash"])
        self.progress_tracker = DownloadProgressTracker(total_pieces)

        # FIX: Pass the file list and set a default downloads directory
        files_info = full_data["files"]
        self.file_assembler = FileAssembler(files_info, base_output_dir="./downloads")

        self.peer_setup = PeerConnectionSetup(self.data_receiver)

    def full_download(self):
        """Main method to manage the full download process"""
        for ip_port, data in self.socket_with_pieces.items():
            ip, port = ip_port.rsplit(":", 1)
            pieces_index = data["pieces"]
            active_connection = data["connection"]
            
            self.download(ip, port, pieces_index, active_connection)

    def download(self, ip, port, pieces, connection):
        """Manage the download process for a single peer connection"""
        remaining_pieces = self.progress_tracker.get_remaining_pieces(pieces)
        if set(remaining_pieces) & set(pieces):
            print(f"\n=== Resuming download pipeline with {ip}:{port} ===\n")
            
            try:
                connection.sock.settimeout(20.0)

                self.peer_setup._send_interested(connection)
                self.peer_setup._wait_for_unchoke(connection)
                self.download_pieces(connection, pieces)
                
                return self.file_assembler.assemble_file()
                
            except Exception as e:
                print(f"Download pipeline failed for {ip}:{port}: {e}")
                return None
            
            finally:
                connection.close()
        else:
            connection.close()
            return None

    def download_pieces(self, connection, available_pieces):
        """Return byte string containing downloaded piece data"""
        message = MessageHandler(connection.sock) 
        piece_downloader = PieceDownloader(message, self.data_receiver)

        total_length = self.torrent_data.return_full_data()["length"]
        standard_piece_length = self.torrent_data.return_full_data()["piece length"]

        remaining_pieces = self.progress_tracker.get_remaining_pieces(available_pieces)

        for piece_index in remaining_pieces:
            self.progress_tracker.mark_piece_started(piece_index)

            piece_size = piece_downloader.calculate_piece_size(piece_index, total_length, standard_piece_length)
            piece_data = piece_downloader.download_piece(connection, piece_index, piece_size)

            if self.piece_validator.validate_piece(piece_data, piece_index):
                self.file_assembler.add_piece(piece_index, piece_data)

                self.progress_tracker.mark_piece_completed(piece_index, piece_size)
                message.have(piece_index)

            else:
                self.progress_tracker.mark_piece_failed(piece_index)
                print(f"Piece {piece_index} hash validation failed!")

    def finalize_download_report(self):
        """Complete the download process"""
        print("\n=== Finalizing download ===\n")

        report = self.progress_tracker.get_progress_report()
        print(f"Download completed: {report['progress_percentage']:.1f}%")
        print(f"Total pieces: {report['downloaded_pieces']}/{report['total_pieces']}")

        if report['is_complete']:
            success = self.file_assembler.save_to_file()

            if success:
                print("Download completed successfully!")
                return True
            else:
                print("Failed to save final file")
                return False
        else:
            print("Download incomplete - some pieces missing")
            return False

    def get_last_piece_length(self, total_length, piece_length):
        """Return integer representing the length of the last piece"""
        remainder = total_length % piece_length
        return remainder if remainder != 0 else piece_length
