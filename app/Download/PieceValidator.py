import hashlib

class PieceValidator:
    """
    Single Responsibility: Validate piece hashes only
    - Calculate SHA1 hashes
    - Compare with expected hashes
    """

    def __init__(self, expected_piece_hashes):
        self.expected_piece_hashes = expected_piece_hashes
        self.validation_results = {}

    def validate_piece(self, piece_data, piece_index):
        """Validate a piece against its expected hash"""
        # Calculate actual hash
        actual_hash = hashlib.sha1(piece_data).hexdigest()
        expected_hash = self.expected_piece_hashes[piece_index]

        is_valid = actual_hash == expected_hash

        # Store result
        self.validation_results[piece_index] = {
            'valid': is_valid,
            'actual_hash': actual_hash,
            'expected_hash': expected_hash
        }

        if is_valid:
            print(f"Piece {piece_index} validation: PASSED")
        else:
            print(f"Piece {piece_index} validation: FAILED")
            print(f"  Expected: {expected_hash}")
            print(f"  Actual:   {actual_hash}")

        return is_valid
