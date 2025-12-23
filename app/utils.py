import bencodepy
import random
import string

class Utils:

    @staticmethod
    def decode_bencode(readed_torrent):
        """Return decoded data from torrent file byte string"""
        x = bencodepy.decode(readed_torrent)
        return x

    @staticmethod
    def peer_id_gen():
        """Generate a 20-byte Azureus-style peer ID."""
        return f"-MV0001-{''.join(random.choices(string.ascii_letters + string.digits, k=12))}".encode("utf-8")
