import bencodepy

class TorrentRead:
    def __init__(self, torrent_file):
        self.torrent_file = torrent_file

    def read_torrent(self):
        """Return byte string containing the contents of the torrent file"""
        with open(self.torrent_file, "rb") as f:
            return f.read()

    def decode_bencode(self):
        """Return decoded data from torrent file byte string"""
        x = bencodepy.decode(self.read_torrent())
        return x

    def bytes_to_str_dict(self, torrent_decode):
        """Convert dictionary keys from bytes to strings by decoding them"""
        if isinstance(torrent_decode, dict):
            return {key.decode(): value for key, value in torrent_decode.items()}
        else:
            return torrent_decode
