from app.torrentRead import TorrentRead
from app.hashGen import Hash

class Torrent:
    def __init__(self, torrent_file):
        self.torrent_read = TorrentRead(torrent_file)
        self.hash_gen = Hash(self.torrent_read)

        self.decode_dict = self.torrent_read.bytes_to_str_dict(self.torrent_read.decode_bencode())

        self.traker_url = self.decode_dict["announce"]
        self.created_by = self.decode_dict["created by"]
        self.info = self.torrent_read.bytes_to_str_dict(self.decode_dict["info"])

        self.info_hash = self.hash_gen.calculate_info_hash(self.decode_dict).hexdigest()
        self.piece_hash_list = self.hash_gen.calculate_pieces_hash(self.decode_dict)


    def return_full_data(self):
        data_dictionary = {
            "tracker url": self.traker_url.decode(),
            "created by": self.created_by.decode(),
            "length": self.info["length"],
            "piece length": self.info["piece length"],
            "name": self.info["name"].decode(),
            "info hash": self.info_hash,
            "pieces hash": self.piece_hash_list,
        }

        return data_dictionary
