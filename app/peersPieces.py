from app.download import Download
from app.messages import Messages
from app.socket import Socket
from app.handshakeMsg import HandshakeMsg

class PeersPieces:
    def __init__(self, ip_port_list):
        self.ip_port_list = ip_port_list

    def pieces_with_socket(self):
        socket_and_pieces = {}

        for i in range(len(self.ip_port_list)):
            ip, port = self.ip_port_list[i].split(":")

            with Socket(ip, int(port)) as peer_con:
                handshake_msg_response = Download(self).handshake_connection(peer_con.sock)
                if handshake_msg_response["info_hash"] == HandshakeMsg().info_hash:
                    avalable_pieces = self.bitfield(peer_con.sock)
                    socket_and_pieces[self.ip_port_list[i]] = avalable_pieces

                else:
                    print("Handshake validate failed")
        return socket_and_pieces

    def bitfield(self, soc):
        """Return list of available piece indexes extracted from bitfield"""
        message = Messages(soc)
        bitfield = message.interested()

        bitfield_str = self.decode_bitfield(bitfield)
        return [i for i, bit in enumerate(bitfield_str) if bit == '1']

    def decode_bitfield(self, data):
        """Return decoded bitfield as a string"""
        bitfield_bytes = data[5:]
        return ''.join(f'{byte:08b}' for byte in bitfield_bytes)

    def get_data(self):
        return self.pieces_with_socket()