import bencodepy
import hashlib
import datetime

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

    def calculate_info_hash(self, decoded_dictionary):
        """Calculate the info hash (SHA-1 of the bencoded 'info' dictionary)"""
        info_dic = self.bytes_to_str_dict(decoded_dictionary["info"])
        bencode_info_dic = bencodepy.encode(info_dic)

        m = hashlib.sha1()
        m.update(bencode_info_dic)
        return m

    def calculate_pieces_hash(self, decoded_dictionary):
        """Split the 'pieces' field from the 'info' dictionary into 20-byte SHA-1 hashes (one per piece)"""
        pieces_bytes_str = self.bytes_to_str_dict(decoded_dictionary["info"])["pieces"]
        pieces_bytes_str_length = len(pieces_bytes_str)

        item_index = 0
        piece_hashes_list = []
        while item_index < pieces_bytes_str_length:
            piece_hashes_list.append(pieces_bytes_str[item_index: item_index + 20].hex())
            item_index += 20

        return piece_hashes_list

    def return_full_data(self):
        data_dictionary = {}
        decode_dict = self.bytes_to_str_dict(self.decode_bencode())

        data_dictionary["tracker url"] = decode_dict["announce"].decode()

        if "announce-list" in decode_dict:
            data_dictionary["announce list"] = decode_dict["announce-list"]
        if "comment" in decode_dict:
            data_dictionary["comment"] = decode_dict["comment"]
        if "created by" in decode_dict:
            data_dictionary["created by"] = decode_dict["created by"].decode()
        if "creation date" in decode_dict:
            dt_object_local = datetime.datetime.fromtimestamp(decode_dict["creation date"])
            data_dictionary["creation date"] = dt_object_local


        if "info" in decode_dict:
            info = self.bytes_to_str_dict(decode_dict["info"])

            data_dictionary["name"] = info["name"]
            data_dictionary["piece length"] = info["piece length"]
            data_dictionary["info hash"] = self.calculate_info_hash(decode_dict).hexdigest()
            data_dictionary["pieces hash"] = self.calculate_pieces_hash(decode_dict)
            if "private" in info:
                data_dictionary["private"] = info["private"]
            if "length" in info:
                data_dictionary["length"] = info["length"]
            else:
                data_dictionary["files"] = info["files"]

        return data_dictionary
