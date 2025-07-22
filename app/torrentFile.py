import bencodepy

class TorrentRead:
    def __init__(self, torrent_file):
        self.torrent_file = torrent_file
        self.torrent_byte_str = b"" # save torrent as a byte string --> b"d8:announce55:http://bittorrent-t..."
        self.read_torrent()
        self.torrent_decode = self.decode_bencode() # decode bencoded torrent --> {b'announce': b'http://bittorrent-t... ,b'pieces': b'\xe8v\xf6z*\x88\x8...x17'}}
        self.traker_url = self.bytes_to_str_dict(self.torrent_decode)["announce"] # get traker url as a byte string--> b'http://bittorrent-test-tracker.codecrafters.io/announce'
        self.created_by = self.bytes_to_str_dict(self.torrent_decode)["created by"]
        self.info = self.bytes_to_str_dict(self.bytes_to_str_dict(self.torrent_decode)["info"]) # get info --> {'length': 92063, 'name': b'sample.txt',... 'pieces': b'\xe8v\x...}

    # --> b"d8:announce55:http://bitt..."
    def read_torrent(self):
        with open(self.torrent_file, "rb") as f:
            self.torrent_byte_str = f.read()

    # --> {b'announce': b'http://bitt...
    def decode_bencode(self):
        x = bencodepy.decode(self.torrent_byte_str)
        return x

    # decode dictionary keys for data access using keys --> {'announce': b'http://bitte', 'created by': b'mktorrent...
    def bytes_to_str_dict(self, torrent_decode):
        if isinstance(torrent_decode, dict):
            return {key.decode(): value for key, value in torrent_decode.items()}
        else:
            return torrent_decode

    def get_data(self):
        data_dict = {"tracker url": self.traker_url.decode(),
                     "created by": self.created_by.decode(),
                     "length": self.info["length"],
                     "piece length": self.info["piece length"],
                     "name": self.info["name"].decode(),
                     }

        return data_dict

