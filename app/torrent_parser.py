import bencodepy
import hashlib

from app.utils import Utils

class TorrentParser:
    def __init__(self, torrent_file):
        self.torrent_file = torrent_file

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
        data_dictionary = {}
        decode_dict = Utils.decode_bencode(self.read_torrent())

        data_dictionary["tracker url"] = decode_dict[b"announce"].decode()

        data_dictionary["created by"] = decode_dict[b"created by"].decode()

        info = decode_dict[b"info"]

        data_dictionary["info"] = info

        data_dictionary["name"] = info[b"name"]
        data_dictionary["piece length"] = info[b"piece length"]
        data_dictionary["info hash"] = self.calculate_info_hash(decode_dict).hexdigest()
        data_dictionary["pieces hash"] = self.calculate_pieces_hash(decode_dict)
        data_dictionary["length"] = info[b"length"]

        return data_dictionary
