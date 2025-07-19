import bencodepy

class TorrentRead:
    def __init__(self, torrent_file):
        self.torrent_file = torrent_file
        self.torrent_byte_str = b""
        self.read_torrent()

    def read_torrent(self):
        with open(self.torrent_file, "rb") as f:
            self.torrent_byte_str = f.read()

    def decode_bencode(self):
        x = bencodepy.decode(self.torrent_byte_str)
        return x
