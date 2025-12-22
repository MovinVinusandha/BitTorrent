from app.Download.message_handler import MessageHandler
from app.socket import Socket

class PeersPieces:
    def __init__(self, ip_port_list, handshake_handler):
        self.ip_port_list = ip_port_list
        self.handshake_handler = handshake_handler

    def pieces_with_socket(self):
        socket_and_pieces = {}

        for i in range(len(self.ip_port_list)):
            ip, port = self.ip_port_list[i].split(":")

            with Socket(ip, int(port)) as peer_con:
                handshake_response = self.handshake_handler.perform_handshake(peer_con.sock)
                expected_hash = self.handshake_handler.get_expected_info_hash()

                if handshake_response["info_hash"] == expected_hash:
                    avalable_pieces = self.bitfield(peer_con.sock)
                    socket_and_pieces[self.ip_port_list[i]] = avalable_pieces

                else:
                    print("Handshake validate failed")
        return socket_and_pieces

    def bitfield(self, soc):
        """Return list of available piece indexes extracted from bitfield"""
        message = MessageHandler(soc)
        bitfield = message.interested()

        bitfield_str = self.decode_bitfield(bitfield)
        return [i for i, bit in enumerate(bitfield_str) if bit == '1']

    def decode_bitfield(self, data):
        """Return decoded bitfield as a string"""
        bitfield_bytes = data[5:]
        return ''.join(f'{byte:08b}' for byte in bitfield_bytes)

    def get_data(self):
        return self.pieces_with_socket()