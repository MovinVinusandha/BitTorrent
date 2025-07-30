import bencodepy

class UtilityClass:

    @staticmethod
    def decode_bencode(readed_torrent):
        """Return decoded data from torrent file byte string"""
        x = bencodepy.decode(readed_torrent)
        return x
