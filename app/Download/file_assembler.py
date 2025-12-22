class FileAssembler:
    """
    Single Responsibility: Assemble pieces into final file only
    - Combine downloaded pieces in correct order
    - Handle file writing
    - Manage output file path
    """

    def __init__(self, output_file_path):
        self.output_file_path = output_file_path
        self.piece_data = {}

    def add_piece(self, piece_index, piece_data):
        """Add a validated piece to the assembly"""
        self.piece_data[piece_index] = piece_data
        print(f"Added piece {piece_index} to assembly ({len(piece_data)} bytes)")

    def assemble_file(self):
        """Assemble all pieces into final file"""
        if not self.piece_data:
            raise Exception("No pieces to assemble")

        print("Assembling file from downloaded pieces...")

        # Sort pieces by index to ensure correct order
        sorted_pieces = sorted(self.piece_data.items())

        # Check for missing pieces
        expected_indices = set(range(len(sorted_pieces)))
        actual_indices = set(piece_index for piece_index, _ in sorted_pieces)

        if expected_indices != actual_indices:
            missing = expected_indices - actual_indices
            raise Exception(f"Missing pieces: {missing}")

        # Assemble file data
        full_file_data = b""
        total_size = 0

        for piece_index, piece_data in sorted_pieces:
            full_file_data += piece_data
            total_size += len(piece_data)

            progress = (total_size / sum(len(data) for _, data in sorted_pieces)) * 100
            print(f"Assembly progress: {progress:.1f}%")

        print(f"Final file assembled: {total_size} bytes")
        return full_file_data

    def save_to_file(self, file_data=None):
        """Save assembled file to disk"""
        if file_data is None:
            file_data = self.assemble_file()

        try:
            with open(self.output_file_path, "wb") as f:
                f.write(file_data)

            print(f"File saved successfully: {self.output_file_path}")
            print(f"File size: {len(file_data)} bytes")

            return True

        except Exception as e:
            print(f"Failed to save file: {e}")
            return False

    def get_assembly_status(self):
        """Get current assembly status"""
        return {
            'pieces_count': len(self.piece_data),
            'total_bytes': sum(len(data) for data in self.piece_data.values()),
            'output_path': self.output_file_path,
            'ready_to_assemble': len(self.piece_data) > 0
        }