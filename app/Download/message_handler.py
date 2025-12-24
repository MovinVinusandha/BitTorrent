import struct

class MessageHandler:
    def __init__(self, soc):
        self.socket = soc

    def _recv_exact(self, total_length):
        """Helper to safely receive exact byte amounts"""
        data = b''
        while len(data) < total_length:
            chunk = self.socket.recv(total_length - len(data))
            if not chunk:
                raise Exception("Connection closed unexpectedly")
            data += chunk
        return data

    def get_bitfield(self):
        """Read the incoming stream until we get the Bitfield message."""
        while True:
            length_bytes = self._recv_exact(4)
            msg_length = struct.unpack(">I", length_bytes)[0]
            
            if msg_length == 0:
                continue
                
            payload = self._recv_exact(msg_length)
            msg_id = payload[0]
            
            if msg_id == 5:
                return payload[1:] 
            elif msg_id == 20:
                continue
            else:
                return None

    def request(self, piece_index, begin, block_len):
        msg = struct.pack(">IbIII", 13, 6, piece_index, begin, block_len)
        self.socket.sendall(msg)

    def have(self, piece_index):
        have_msg = struct.pack(">IbI", 5, 4, piece_index)
        self.socket.sendall(have_msg)