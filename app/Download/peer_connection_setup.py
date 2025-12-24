import struct

class PeerConnectionSetup:
    def __init__(self, data_receiver):
        self.data_receiver = data_receiver

    def setup_peer_connection(self, connection, peer_pieces_handler):
        """Complete peer setup sequence"""
        print("Setting up peer connection...")

        available_pieces = self._exchange_bitfield(connection, peer_pieces_handler)
        self._send_interested(connection)
        self._wait_for_unchoke(connection)

        return available_pieces

    def _exchange_bitfield(self, connection, peer_pieces_handler):
        """Handle bitfield exchange"""
        print("Exchanging bitfield...")
        return peer_pieces_handler.bitfield(connection.sock)

    def _send_interested(self, connection):
        """Send interested message to peer"""
        print("Sending interested message...")
        interested_msg = struct.pack(">Ib", 1, 2)
        connection.sock.sendall(interested_msg)

    def _wait_for_unchoke(self, connection):
        """Wait for peer to unchoke us, safely skipping other messages"""
        print("Waiting for unchoke...")

        while True:
            length_bytes = self.data_receiver._recv_exact(connection.sock, 4)
            msg_length = struct.unpack(">I", length_bytes)[0]

            if msg_length == 0:
                continue

            payload = self.data_receiver._recv_exact(connection.sock, msg_length)
            msg_id = payload[0]

            if msg_id == 1:
                print("Peer has unchoked us - ready to download!")
                break
            else:
                print(f"Received message ID {msg_id} while waiting for unchoke. Ignoring.")
