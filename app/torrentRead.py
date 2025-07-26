import bencodepy
import hashlib

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
        decode_dict = self.bytes_to_str_dict(self.decode_bencode())

        traker_url = decode_dict["announce"]
        created_by = decode_dict["created by"]
        info = self.bytes_to_str_dict(decode_dict["info"])

        info_hash = self.calculate_info_hash(decode_dict).hexdigest()
        piece_hash_list = self.calculate_pieces_hash(decode_dict)

        data_dictionary = {
            "tracker url": traker_url.decode(),
            "created by": created_by.decode(),
            "length": info["length"],
            "piece length": info["piece length"],
            "name": info["name"].decode(),
            "info hash": info_hash,
            "pieces hash": piece_hash_list,
        }

        return data_dictionary

