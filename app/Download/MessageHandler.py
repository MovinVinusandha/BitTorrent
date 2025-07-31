import struct

class MessageHandler:
    def __init__(self, soc):
        self.socket = soc

    def interested(self):
        msg = struct.pack("Ib", 1, 2)
        self.socket.send(msg)
        return self.socket.recv(68)

    def request(self, piece_index, begin, block_len):
        msg = struct.pack(">IbIII", 13, 6, piece_index, begin, block_len)
        self.socket.sock.sendall(msg)

    def have(self, piece_index):
        have_msg = struct.pack(">IbI", 5, 4, piece_index)
        self.socket.sock.sendall(have_msg)
