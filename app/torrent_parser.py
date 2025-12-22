import bencodepy
import hashlib

from app.utils import Utils

class TorrentParser:
    def __init__(self, torrent_file):
        self.torrent_file = torrent_file
        self.raw_data = self.read_torrent()
        self.decoded_data = Utils.decode_bencode(self.raw_data)

    def read_torrent(self):
        """Return byte string containing the contents of the torrent file"""
        with open(self.torrent_file, "rb") as f:
            return f.read()

    def calculate_info_hash(self, decoded_dictionary):
        """Calculate the info hash (SHA-1 of the bencoded 'info' dictionary)"""
        info_dic = decoded_dictionary[b"info"]
        bencode_info_dic = bencodepy.encode(info_dic)

        m = hashlib.sha1()
        m.update(bencode_info_dic)
        return m

    def calculate_pieces_hash(self, decoded_dictionary):
        """Split the 'pieces' field from the 'info' dictionary into 20-byte SHA-1 hashes (one per piece)"""
        pieces_bytes_str = decoded_dictionary[b"info"][b"pieces"]
        pieces_bytes_str_length = len(pieces_bytes_str)

        item_index = 0
        piece_hashes_list = []
        while item_index < pieces_bytes_str_length:
            piece_hashes_list.append(pieces_bytes_str[item_index: item_index + 20].hex())
            item_index += 20

        return piece_hashes_list

    def return_full_data(self):
        """Return a standardized dictionary of the torrent data."""
        return{
            "tracker url": self.decoded_data[b"announce"].decode(),
            "created by": self.decoded_data[b"created by"].decode(),
            "info": self.decoded_data[b"info"],
            "name": self.decoded_data[b"info"][b"name"],
            "piece length": self.decoded_data[b"info"][b"piece length"],
            "info hash": self.calculate_info_hash(self.decoded_data).hexdigest(),
            "pieces hash": self.calculate_pieces_hash(self.decoded_data),
            "length": self.decoded_data[b"info"][b"length"]
        }