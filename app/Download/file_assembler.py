import os

class FileAssembler:
    def __init__(self, files_info, base_output_dir="./downloads"):
        self.files_info = files_info
        self.base_output_dir = base_output_dir
        self.piece_data = {}

    def add_piece(self, piece_index, piece_data):
        """Add a piece of the file to the assembler."""
        self.piece_data[piece_index] = piece_data
        print(f"Added piece {piece_index} to assembly ({len(piece_data)} bytes)")

    def assemble_file(self):
        """Assemble the full file data from the pieces."""
        if not self.piece_data:
            raise Exception("No pieces to assemble")

        print("Assembling giant byte stream from downloaded pieces...")
        sorted_pieces = sorted(self.piece_data.items())

        expected_indices = set(range(len(sorted_pieces)))
        actual_indices = set(piece_index for piece_index, _ in sorted_pieces)

        if expected_indices != actual_indices:
            missing = expected_indices - actual_indices
            raise Exception(f"Missing pieces: {missing}")

        full_file_data = b""
        total_size = 0

        for piece_index, piece_data in sorted_pieces:
            full_file_data += piece_data
            total_size += len(piece_data)

        print(f"Giant byte stream assembled: {total_size} bytes")
        return full_file_data

    def save_to_file(self, file_data=None):
        """Save the assembled file data to disk, slicing it according to the provided file info."""
        if file_data is None:
            file_data = self.assemble_file()

        print("Slicing byte stream into individual files...")
        try:
            current_offset = 0

            for file_info in self.files_info:

                relative_path = file_info["path"]
                file_length = file_info["length"]

                full_path = os.path.join(self.base_output_dir, relative_path)

                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                file_chunk = file_data[current_offset: current_offset + file_length]

                with open(full_path, "wb") as f:
                    f.write(file_chunk)

                print(f"Saved: {full_path} ({file_length} bytes)")

                current_offset += file_length

            return True

        except Exception as e:
            print(f"Failed to save files: {e}")
            return False

    def get_assembly_status(self):
        """Return the current status of the assembly process."""
        return {
            'pieces_count': len(self.piece_data),
            'total_bytes': sum(len(data) for data in self.piece_data.values()),
            'ready_to_assemble': len(self.piece_data) > 0
        }