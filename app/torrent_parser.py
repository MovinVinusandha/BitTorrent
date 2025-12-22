import bencodepy
import hashlib

from app.utils import Utils

class TorrentParser:
    def __init__(self, torrent_file):
        self.torrent_file = torrent_file
        self.raw_data = self.read_torrent()
        self.decoded_data = Utils.decode_bencode(self.raw_data)
        self.info_dict = self.decoded_data[b"info"]

    def _safe_decode(self, byte_str, default=""):
        """Safely decode byte strings. Falls back if not valid UTF-8."""
        if byte_str is None:
            return default
        try:
            return byte_str.decode('utf-8')
        except UnicodeDecodeError:
            return byte_str.decode('latin-1', errors='replace')

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
    
    def get_trackers(self):
        """Get all trackers, handling both standard 'announce' and 'announce-list'."""
        trackers = []
        
        if b"announce-list" in self.decoded_data:
            for tier in self.decoded_data[b"announce-list"]:
                for tracker in tier:
                    trackers.append(self._safe_decode(tracker))
                    
        elif b"announce" in self.decoded_data:
            trackers.append(self._safe_decode(self.decoded_data[b"announce"]))
            
        return trackers
    
    def get_files(self):
        """
        Determine if it's a single or multi-file torrent and return a standard format:
        List of dictionaries with 'path' and 'length'.
        """
        files = []
        base_name = self._safe_decode(self.info_dict.get(b"name", b"Unknown"))

        if b"files" in self.info_dict:
            for f in self.info_dict[b"files"]:
                path_parts = [self._safe_decode(p) for p in f[b"path"]]
                full_path = "/".join([base_name] + path_parts)
                files.append({
                    "path": full_path,
                    "length": f[b"length"]
                })
        else:
            files.append({
                "path": base_name,
                "length": self.info_dict.get(b"length", 0)
            })
            
        return files

    
    def get_total_length(self):
        """Sum the lengths of all files."""
        return sum(f["length"] for f in self.get_files())

    def return_full_data(self):
        """Return a standardized dictionary of the torrent data."""
        
        return{
            "tracker url": self.get_trackers()[0] if self.get_trackers() else "",
            "all trackers": self.get_trackers(),
            "created by": self.decoded_data[b"created by"].decode(),
            "comment": self._safe_decode(self.decoded_data.get(b"comment")),
            "info": self.info_dict,
            "name": self._safe_decode(self.info_dict.get(b"name", b"Unknown")),
            "piece length": self.info_dict[b"piece length"],
            "info hash": self.calculate_info_hash(self.decoded_data).hexdigest(),
            "pieces hash": self.calculate_pieces_hash(self.decoded_data),
            "length": self.get_total_length(),
            "files": self.get_files(),
        }