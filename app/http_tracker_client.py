import requests
import bencodepy

class HttpTrackerClient:
    def __init__(self, url, params):
        self.url = url
        self.params = params

    def _parse_response(self, raw_response):
        """Parse the raw tracker response and return a list of (ip, port) tuples"""
        decoded_response = bencodepy.decode(raw_response)
        
        if b"failure reason" in decoded_response:
            error_msg = decoded_response[b"failure reason"].decode('utf-8', 'replace')
            raise Exception(f"Tracker returned error: {error_msg}")

        peers_data = decoded_response.get(b"peers", [])
        peers_list = []

        if isinstance(peers_data, bytes):
            for i in range(0, len(peers_data), 6):
                if i + 6 > len(peers_data):
                    break
                ip = f"{peers_data[i]}.{peers_data[i+1]}.{peers_data[i+2]}.{peers_data[i+3]}"
                port = int.from_bytes(peers_data[i+4:i+6], byteorder='big')
                peers_list.append(f"{ip}:{port}")
                
        elif isinstance(peers_data, list):
            for peer in peers_data:
                ip = peer[b"ip"].decode("utf-8", "replace")
                port = peer[b"port"]
                peers_list.append(f"{ip}:{port}")

        return peers_list
    
    def request_peers(self):
        """Return a list of (ip, port) strings containing peer data from tracker response"""
        response = requests.get(self.url, params=self.params, timeout=10)
        response.raise_for_status()# Add a timeout so HTTP trackers don't hang infinitely either
        
        raw_data = response.content
        parsed_peers_list = self._parse_response(raw_data)

        return parsed_peers_list
    
    def request_peers_data(self):
        """Return a dictionary containing decoded peer information from the tracker response"""
        response = requests.get(self.url, params=self.params, timeout=10)
        raw_data = response.content
        tracker_response_decode = bencodepy.decode(raw_data)

        return {
            "complete": tracker_response_decode.get(b"complete", 0),
            "incomplete": tracker_response_decode.get(b"incomplete", 0),
            "interval": tracker_response_decode.get(b"interval", 0),
            "min interval": tracker_response_decode.get(b"min interval", 0),
        }