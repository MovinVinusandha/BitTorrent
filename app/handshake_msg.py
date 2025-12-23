import hashlib
import struct
import bencodepy

from app.tracker_manager import TrackerManager
from app.utils import Utils

PROTOCOL_STR = b"BitTorrent protocol"

class HandshakeMsg:
    def __init__(self, torrent_read_class):
        self.torrent_data = torrent_read_class

        info = Utils.decode_bencode(self.torrent_data.read_torrent())[b"info"]
        self.info_hash = hashlib.sha1(bencodepy.encode(info)).digest()


    def handshake_msg(self):
        """Return byte object of handshake message"""
        protocol_str_len = len(PROTOCOL_STR)
        reserved_bytes = bytes(8)
        peer_id = Utils.peer_id_gen()

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