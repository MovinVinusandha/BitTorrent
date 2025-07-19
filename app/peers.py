import hashlib
import string
import sys
import random
import bencodepy
import requests

from app.hashGen import Hash
from app.torrentFile import TorrentRead

class Peers:
    def __init__(self):
        torrent_file = sys.argv[2]
        self.torrent_read = TorrentRead(torrent_file)
        self.hash = Hash()

        self.url = self.torrent_read.get_data()["tracker url"]

        self.info_hash = hashlib.sha1(bencodepy.encode(self.torrent_read.info)).digest()
        self.peer_id = self.peer_id_gen()
        self.port = 6881
        self.uploaded = 0
        self.downloaded = 0
        self.left = self.torrent_read.get_data()["length"]
        self.compact = 1

    def peer_id_gen(self):
        return f"-MV0001-{''.join(random.choices(string.ascii_letters + string.digits, k=12))}".encode("utf-8")

    def url_params(self):
        url = self.url

        params = {"info_hash": self.info_hash,
                  "peer_id": self.peer_id,
                  "port": self.port,
                  "uploaded": self.uploaded,
                  "downloaded": self.downloaded,
                  "left": self.left,
                  "compact": self.compact,
                  }

        return {"url": url, "params": params}

    def get_peers_data(self):
        response = requests.get(self.url_params()["url"], self.url_params()["params"])
        return response.content
