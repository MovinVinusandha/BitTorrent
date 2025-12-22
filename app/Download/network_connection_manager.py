from app.socket import Socket

class NetworkConnectionManager:
    """
    Single Responsibility: Manage socket connections only
    - Connect to peers
    """

    def __init__(self, socket_factory=None):
        self.socket_factory = socket_factory or Socket
        self.active_connections = {}

    def connect_to_peer(self, ip, port):
        """Establish connection to a peer"""
        try:
            connection = self.socket_factory(ip, port)
            connection_key = f"{ip}:{port}"
            self.active_connections[connection_key] = connection
            print(f"Connected to {ip}:{port}")
            return connection
        except Exception as e:
            print(f"Failed to connect to {ip}:{port}: {e}")
            return None