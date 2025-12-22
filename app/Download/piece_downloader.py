class PieceDownloader:
    """
    Single Responsibility: Download individual pieces only
    - Request piece blocks from peers
    - Assemble blocks into pieces
    - Handle block-level communication
    """

    def __init__(self, message_handler, data_receiver, block_size=16384):
        self.message_handler = message_handler
        self.data_receiver = data_receiver
        self.block_size = block_size

    def download_piece(self, connection, piece_index, piece_size):
        """Download a complete piece from peer"""
        print(f"Downloading piece {piece_index} (size: {piece_size} bytes)")

        piece_data = b""

        # Download piece in blocks
        for begin in range(0, piece_size, self.block_size):
            block_length = min(self.block_size, piece_size - begin)

            # Request block
            self.message_handler.request(piece_index, begin, block_length)

            # Receive block data
            block_data = self.data_receiver.receive_block(connection, block_length)

            if not block_data:
                raise Exception(f"Failed to receive block for piece {piece_index}")

            piece_data += block_data

            # Progress feedback
            progress = (len(piece_data) / piece_size) * 100
            print(f"Piece {piece_index}: {progress:.1f}% complete")

        return piece_data

    def calculate_piece_size(self, piece_index, total_length, standard_piece_length):
        """Calculate the size of a specific piece"""
        total_pieces = (total_length + standard_piece_length - 1) // standard_piece_length

        if piece_index == total_pieces - 1:
            # Last piece might be smaller
            remainder = total_length % standard_piece_length
            return remainder if remainder != 0 else standard_piece_length
        else:
            return standard_piece_length