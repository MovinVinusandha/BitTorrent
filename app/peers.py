import hashlib
import string
import sys
import random
import bencodepy
import requests

from app.torrentData import Torrent
from app.torrentRead import TorrentRead

class Peers:
    def __init__(self):
        torrent_file = sys.argv[2]
        self.torrent_data = Torrent(torrent_file)
        self.torrent_read = TorrentRead(torrent_file)
        self.my_id = self.peer_id_gen()

    def peer_id_gen(self):
        """Generate a 20-byte Azureus-style peer ID (e.g. -PC0001-<random>)"""
        return f"-MV0001-{''.join(random.choices(string.ascii_letters + string.digits, k=12))}".encode("utf-8")

    def url_params(self):
        """Return dictionary of URL parameters used to make a tracker request"""
        url = self.torrent_data.return_full_data()["tracker url"]

        info_hash = hashlib.sha1(bencodepy.encode(self.torrent_data.info)).digest()
        peer_id = self.peer_id_gen()
        port = 6881
        uploaded = 0
        downloaded = 0
        left = self.torrent_data.return_full_data()["length"]
        compact = 1

        params = {"info_hash": info_hash,
                  "peer_id": peer_id,
                  "port": port,
                  "uploaded": uploaded,
                  "downloaded": downloaded,
                  "left": left,
                  "compact": compact,
                  }

        return {"url": url, "params": params}

    def get_peers_data(self):
        """Return raw byte string containing peers data from tracker response"""
        response = requests.get(self.url_params()["url"], self.url_params()["params"])
        return response.content

    def gen_peers_ip(self):
        """Return a list of peer IPs extracted from decoded tracker peer data"""
        tracker_response_decode = bencodepy.decode(self.get_peers_data())
        string_dict = self.torrent_read.bytes_to_str_dict(tracker_response_decode)
        peers_value_list = list(string_dict["peers"])

        all_ip_port_bytes_list = []
        for i in range(0, len(peers_value_list), 6):
            all_ip_port_bytes_list += [[item for item in peers_value_list[i: i + 6]]]

        complete_ip_list = []
        for ip_port_bytes_list in all_ip_port_bytes_list:
            complete_ip = ""
            for i in range(0, 4):
                complete_ip += f"{ip_port_bytes_list[i]}."
                if i == 3:
                    complete_ip += str(int.from_bytes(ip_port_bytes_list[4:6], byteorder='big', signed=False))
            complete_ip_list.append(complete_ip)

        return [f"{ip_port[:-6:]}:{ip_port.split(".")[-1]}" for ip_port in complete_ip_list]

    def gen_peer_data(self):
        """Return a dictionary containing decoded peer information from the tracker response"""
        tracker_response_decode = bencodepy.decode(self.get_peers_data())
        string_dict = self.torrent_read.bytes_to_str_dict(tracker_response_decode)

        complete = string_dict["complete"]
        incomplete = string_dict["incomplete"]
        interval = string_dict["interval"]
        min_interval = string_dict["min interval"]

        return {"complete": complete,
                "incomplete": incomplete,
                "interval": interval,
                "min interval": min_interval,
                }

    def get_data(self):
        peers_ip = self.gen_peers_ip()
        peers_data = self.gen_peer_data()

        return {"data": peers_data,
                "ip": peers_ip
                }
