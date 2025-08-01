import struct

class PeerConnectionSetup:
    """
    Single Responsibility: Handle BitTorrent peer connection setup
    - Exchange bitfield information
    - Send interested message
    - Wait for unchoke
    - Manage peer state transitions
    """

    def __init__(self, data_receiver):
        self.data_receiver = data_receiver

    def setup_peer_connection(self, connection, peer_pieces_handler):
        """Complete peer setup sequence"""
        print("Setting up peer connection...")

        # Step 1: Exchange bitfield
        available_pieces = self._exchange_bitfield(connection, peer_pieces_handler)

        # Step 2: Send interested message
        self._send_interested(connection)

        # Step 3: Wait for unchoke
        self._wait_for_unchoke(connection)

        return available_pieces

    def _exchange_bitfield(self, connection, peer_pieces_handler):
        """Handle bitfield exchange"""
        print("Exchanging bitfield...")
        return peer_pieces_handler.bitfield(connection.sock)

    def _send_interested(self, connection):
        """Send interested message to peer"""
        print("Sending interested message...")
        interested_msg = struct.pack(">Ib", 1, 2)  # Length=1, ID=2
        connection.sock.sendall(interested_msg)

    def _wait_for_unchoke(self, connection):
        """Wait for peer to unchoke us"""
        print("Waiting for unchoke...")

        # Receive unchoke message (5 bytes total)
        msg = self.data_receiver._recv_exact(connection.sock, 5)

        # Parse message
        length, msg_id = struct.unpack(">IB", msg)

        if msg_id != 1:  # 1 = unchoke message ID
            raise Exception(f"Expected unchoke (ID=1), got message ID={msg_id}")

        print("Peer has unchoked us - ready to download!")
