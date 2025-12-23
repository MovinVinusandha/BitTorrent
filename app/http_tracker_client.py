import requests
import bencodepy

class HttpTrackerClient:
    def __init__(self, url, params):
        self.url = url
        self.params = params

    def _parse_response(self, raw_response):
        """Parse the raw tracker response and return a list of (ip, port) tuples"""
        decoded_response = bencodepy.decode(raw_response)
        peers_data_list = list(decoded_response[b"peers"])

        all_ip_port_bytes_list = []
        for i in range(0, len(peers_data_list), 6):
            all_ip_port_bytes_list += [[item for item in peers_data_list[i: i + 6]]]

        complete_ip_list = []
        for ip_port_bytes_list in all_ip_port_bytes_list:
            complete_ip = ""
            for i in range(0, 4):
                complete_ip += f"{ip_port_bytes_list[i]}."
                if i == 3:
                    complete_ip += str(int.from_bytes(ip_port_bytes_list[4:6], byteorder='big', signed=False))
            complete_ip_list.append(complete_ip)

        return [f"{ip_port[:-6:]}:{ip_port.split(".")[-1]}" for ip_port in complete_ip_list]
    
    def request_peers(self):
        """Return a list of (ip, port) tuples containing peer data from tracker response"""
        response = requests.get(self.url, params=self.params)
        raw_data = response.content
        parsed_peers_list = self._parse_response(raw_data)

        return parsed_peers_list
    
    def request_peers_data(self):
        """Return a dictionary containing decoded peer information from the tracker response"""
        response = requests.get(self.url, params=self.params)
        raw_data = response.content
        tracker_response_decode = bencodepy.decode(raw_data)

        return {
            "complete": tracker_response_decode[b"complete"],
            "incomplete": tracker_response_decode[b"incomplete"],
            "interval": tracker_response_decode[b"interval"],
            "min interval": tracker_response_decode[b"min interval"],
        }