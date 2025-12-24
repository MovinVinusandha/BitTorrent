import socket
import struct
import random
from urllib.parse import urlparse

class UdpTrackerClient:
    def __init__(self, url, params):
        self.url = url
        self.params = params

    def _execute_udp_announce(self):
        """Helper method to handle the UDP connection and announce protocol. Returns the raw response buffer."""
        parsed = urlparse(self.url)
        tracker_host = parsed.hostname
        tracker_port = parsed.port

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5.0)

        try:
            tracker_address = (socket.gethostbyname(tracker_host), tracker_port)
        except socket.gaierror:
            print(f"Could not resolve tracker: {tracker_host}")
            return None

        connection_id = 0x41727101980
        action = 0  # 0 = Connect
        transaction_id = random.randint(0, int(2 ** 32 - 1))

        req_buffer = struct.pack(">QII", connection_id, action, transaction_id)

        try:
            sock.sendto(req_buffer, tracker_address)
            res_buffer, _ = sock.recvfrom(2048)
        except socket.timeout:
            return None

        res_action, res_transaction_id, new_connection_id = struct.unpack(">IIQ", res_buffer)

        if res_action != 0 or res_transaction_id != transaction_id:
            return None

        action = 1  # 1 = Announce
        transaction_id = random.randint(0, int(2 ** 32 - 1))
        info_hash = self.params["info_hash"]
        peer_id = self.params["peer_id"]

        announce_req = struct.pack(
            ">QII20s20sQQQIIIiH",
            new_connection_id,
            action,
            transaction_id,
            info_hash,
            peer_id,
            self.params["downloaded"],
            self.params["left"],
            self.params["uploaded"],
            0,  # event
            0,  # ip
            random.randint(0, int(2 ** 32 - 1)),  # key
            -1,  # num_want
            self.params["port"]
        )

        try:
            sock.sendto(announce_req, tracker_address)
            announce_res, _ = sock.recvfrom(2048)
            return (announce_res, transaction_id)
        except socket.timeout:
            return None

    def request_peers(self):
        """Public method to get a list of (ip, port) strings from the UDP tracker"""
        result = self._execute_udp_announce()
        if not result:
            return []

        announce_res, transaction_id = result

        if len(announce_res) < 20:
            return []

        res_action, res_transaction_id, interval, leechers, seeders = struct.unpack(">IIIII", announce_res[:20])

        if res_action != 1 or res_transaction_id != transaction_id:
            return []


        peers_bytes = announce_res[20:]
        peers_list = []

        for i in range(0, len(peers_bytes), 6):
            if i + 6 > len(peers_bytes):
                break
            ip_bytes, peer_port = struct.unpack(">4sH", peers_bytes[i:i + 6])
            peer_ip = socket.inet_ntoa(ip_bytes)
            peers_list.append(f"{peer_ip}:{peer_port}")

        return peers_list

    def request_peers_data(self):
        """Return a dictionary containing decoded peer information from the tracker response"""
        result = self._execute_udp_announce()

        empty_data = {
            "complete": 0,
            "incomplete": 0,
            "interval": 0,
            "min interval": 0
        }

        if not result:
            return empty_data

        announce_res, transaction_id = result

        if len(announce_res) < 20:
            return empty_data

        res_action, res_transaction_id, interval, leechers, seeders = struct.unpack(">IIIII", announce_res[:20])

        if res_action != 1 or res_transaction_id != transaction_id:
            return empty_data

        return {
            "complete": seeders,
            "incomplete": leechers,
            "interval": interval,
            "min interval": interval
        }
