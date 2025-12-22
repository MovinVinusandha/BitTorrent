class DataReceiver:
    """Helper class to receive data from connections"""

    def receive_block(self, connection, block_length):
        """Receive a piece block from peer"""

        # Receive message header + block data
        response = self._recv_exact(connection.sock, 13 + block_length)

        # Extract just the block data (skip 13-byte header)
        block_data = response[13:]

        return block_data

    def _recv_exact(self, socket, total_length):
        """Receive exactly total_length bytes"""
        data = b''
        while len(data) < total_length:
            chunk = socket.recv(total_length - len(data))
            if not chunk:
                raise Exception("Connection closed unexpectedly")
            data += chunk
        return data
