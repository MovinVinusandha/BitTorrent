import bencodepy
import hashlib

from app.http_tracker_client import HttpTrackerClient
from app.udp_tracker_client import UdpTrackerClient
from app.utils import Utils

class TrackerManager:
    def __init__(self, torrent_data):
        self.torrent_data = torrent_data

    def _build_params(self):
        """Build the parameters for the tracker request"""
        info_hash = hashlib.sha1(bencodepy.encode(self.torrent_data["info"])).digest()
        peer_id = Utils.peer_id_gen()
        port = 6881
        uploaded = 0
        downloaded = 0
        left = self.torrent_data["length"]
        compact = 1

        params = {
            "info_hash": info_hash,
            "peer_id": peer_id,
            "port": port,
            "uploaded": uploaded,
            "downloaded": downloaded,
            "left": left,
            "compact": compact,
        }

        return params
    
    def get_peers(self):
        """Iterate through all trackers and return the list of peers from the first successful response"""
        for tracker in self.torrent_data["all trackers"]:
            if tracker.startswith("http") or tracker.startswith("https"):
                http_client = HttpTrackerClient(tracker, self._build_params())
                return http_client.request_peers()
            
            else:
                print(f"Unknown tracker protocol for {tracker}, skipping.")

        return []