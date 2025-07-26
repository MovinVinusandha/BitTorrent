import hashlib
import struct
import sys
import bencodepy

from app.peers import Peers
from app.torrentRead import TorrentRead

PROTOCOL_STR = b"BitTorrent protocol"

class HandshakeMsg:
    def __init__(self):
        torrent_file = sys.argv[2]
        self.torrent_data = TorrentRead(torrent_file)
        self.peers = Peers()

        info = self.torrent_data.bytes_to_str_dict(self.torrent_data.bytes_to_str_dict(self.torrent_data.decode_bencode())["info"])
        self.info_hash = hashlib.sha1(bencodepy.encode(info)).digest()


    def handshake_msg(self):
        """Return byte object of handshake message"""
        protocol_str_len = len(PROTOCOL_STR)
        reserved_bytes = bytes(8)
        peer_id = self.peers.my_id

        handshake_params = struct.pack(
            f'b{protocol_str_len}s8s20s20s',
            protocol_str_len,
            PROTOCOL_STR,
            reserved_bytes,
            self.info_hash,
            peer_id
        )

        return handshake_params

    def handshake_msg_unpack(self, socket):
        handshake_reply = socket.recv(68)

        protocol_str_len, protocol_str, reserved_bytes, info_hash, peer_id = struct.unpack(
            f'b{len(PROTOCOL_STR)}s8s20s20s',
            handshake_reply
        )

        return {
            "protocol_str_len": protocol_str_len,
            "protocol_str": protocol_str,
            "reserved_bytes": reserved_bytes,
            "info_hash": info_hash,
            "peer_id": peer_id,
        }