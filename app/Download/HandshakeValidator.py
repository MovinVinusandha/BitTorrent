class HandshakeValidator:
    """
    Single Responsibility: Validate handshake responses only
    - Compare info hashes
    - Validate handshake format
    - Return validation results
    """

    def __init__(self, expected_info_hash):
        self.expected_info_hash = expected_info_hash

    def is_valid_handshake(self, handshake_response):
        """Check if handshake response is valid"""
        if not handshake_response:
            return False

        received_info_hash = handshake_response.get("info_hash")
        if not received_info_hash:
            return False

        is_valid = received_info_hash == self.expected_info_hash

        if not is_valid:
            print("Handshake validation failed: info_hash mismatch")

        return is_valid

    def validate_and_log(self, handshake_response, peer_address):
        """Validate handshake and log result"""
        is_valid = self.is_valid_handshake(handshake_response)

        if is_valid:
            print(f"Handshake with {peer_address} successful")
        else:
            print(f"Handshake with {peer_address} failed")

        return is_valid

