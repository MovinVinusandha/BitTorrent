from app.handshake_msg import HandshakeMsg


class TorrentHandshakeHandler:
    def __init__(self, torrent_data):
        self.handshake_msg = HandshakeMsg(torrent_data)

    def perform_handshake(self, socket):
        socket.send(self.handshake_msg.handshake_msg())
        return self.handshake_msg.handshake_msg_unpack(socket)

    def get_expected_info_hash(self):
        return self.handshake_msg.info_hash