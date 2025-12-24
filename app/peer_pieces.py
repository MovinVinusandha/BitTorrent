from app.Download.message_handler import MessageHandler
from app.socket import Socket

class PeersPieces:
    def __init__(self, ip_port_list, handshake_handler):
        self.ip_port_list = ip_port_list
        self.handshake_handler = handshake_handler

    def pieces_with_socket(self):
        """Return dict of peer ip:port as key and dict of available pieces and socket connection as value"""
        socket_and_pieces = {}

        total_peers = len(self.ip_port_list)

        for i in range(total_peers):
            ip, port = self.ip_port_list[i].rsplit(":", 1)
            print(f"[{i + 1}/{total_peers}] Probing peer {ip}:{port}...")

            peer_con = Socket(ip, int(port))
            try:
                peer_con.connect()
                peer_con.sock.settimeout(10.0)
                
                handshake_response = self.handshake_handler.perform_handshake(peer_con.sock)
                expected_hash = self.handshake_handler.get_expected_info_hash()

                if handshake_response["info_hash"] == expected_hash:
                    avalable_pieces = self.bitfield(peer_con.sock)

                    socket_and_pieces[self.ip_port_list[i]] = {
                        "pieces": avalable_pieces,
                        "connection": peer_con 
                    }
                    
                    print(f"--> Success! Handshake valid.")
                else:
                    print(f"--> Handshake validate failed.")
                    peer_con.close()

            except Exception as e:
                print(f"--> Failed to connect or handshake: {e.__class__.__name__}. Trying next...")
                peer_con.close()
                continue

        return socket_and_pieces

    def bitfield(self, soc):
        """Return list of available piece indexes extracted from bitfield"""
        message = MessageHandler(soc)
        
        bitfield_payload = message.get_bitfield()
        if not bitfield_payload:
            return []

        bitfield_str = self.decode_bitfield(bitfield_payload)
        return [i for i, bit in enumerate(bitfield_str) if bit == '1']

    def decode_bitfield(self, data):
        """Return decoded bitfield as a string"""
        return ''.join(f'{byte:08b}' for byte in data)

    def get_data(self):
        """Return the dictionary of peers with their available pieces and socket connections"""
        return self.pieces_with_socket()