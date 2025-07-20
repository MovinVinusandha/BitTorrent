import hashlib
import struct
import sys
import bencodepy

from app.hashGen import Hash
from app.peers import Peers
from app.torrentFile import TorrentRead

class Handshake:
    def __init__(self):
        torrent_file = sys.argv[2]
        self.torrent_read = TorrentRead(torrent_file)
        self.hash = Hash()
        self.peers = Peers()

        self.info_hash = hashlib.sha1(bencodepy.encode(self.torrent_read.info)).digest()

        self.protocol_str = b"BitTorrent protocol"
        self.protocol_str_len = len(self.protocol_str)
        self.reserved_bytes = bytes(8)
        self.peer_id = self.peers.peer_id_gen()

    def handshake_msg(self):
        handshake_params = struct.pack(
            f'b{self.protocol_str_len}s8s20s20s',
            self.protocol_str_len,
            self.protocol_str,
            self.reserved_bytes,
            self.info_hash,
            self.peer_id
        )

        return handshake_params