import struct

class DataReceiver:
    def receive_block(self, connection, block_length):
        """Receive a piece block from peer, safely ignoring other network messages"""
        while True:
            length_bytes = self._recv_exact(connection.sock, 4)
            msg_length = struct.unpack(">I", length_bytes)[0]

            if msg_length == 0:
                continue  # Ignore Keep-Alive messages

            payload = self._recv_exact(connection.sock, msg_length)
            msg_id = payload[0]

            if msg_id == 7:
                block_data = payload[9:]
                return block_data
            else:
                pass

    def _recv_exact(self, socket, total_length):
        """Receive exactly total_length bytes"""
        data = b''
        while len(data) < total_length:
            chunk = socket.recv(total_length - len(data))
            if not chunk:
                raise Exception("Connection closed unexpectedly")
            data += chunk
        return data
