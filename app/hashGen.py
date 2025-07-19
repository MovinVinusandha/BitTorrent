import hashlib
import sys
import bencodepy
from app.torrentFile import TorrentRead

class Hash:
    def __init__(self):
        torrent_file = sys.argv[2]
        self.torrent_read = TorrentRead(torrent_file)

        self.decode_dict = self.torrent_read.bytes_to_str_dict(self.torrent_read.torrent_decode)
        self.info_hash = self.calculate_info_hash(self.decode_dict).hexdigest()
        self.piece_hash_list = self.calculate_pieces_hash(self.decode_dict)

    def calculate_info_hash(self, decoded_dictionary):
        info_dic = self.torrent_read.bytes_to_str_dict(decoded_dictionary["info"])
        bencode_info_dic = bencodepy.encode(info_dic)

        m = hashlib.sha1()
        m.update(bencode_info_dic)
        return m

    def calculate_pieces_hash(self, decoded_dictionary):
        pieces_bytes_str = self.torrent_read.bytes_to_str_dict(decoded_dictionary["info"])["pieces"]
        pieces_bytes_str_length = len(pieces_bytes_str)

        item_index = 0
        piece_hashes_list = []
        while item_index < pieces_bytes_str_length:
            piece_hashes_list.append(pieces_bytes_str[item_index: item_index + 20].hex())
            item_index += 20

        return piece_hashes_list

    def get_data(self):
        data_dict = {"info hash": self.info_hash,
                     "pieces hash": self.piece_hash_list,
                     }

        return data_dict
