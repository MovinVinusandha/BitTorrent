import sys
from pprint import pprint

from app.handshake_handler import TorrentHandshakeHandler
from app.download import Download
from app.torrent_parser import TorrentParser
from app.peer_pieces import PeersPieces
from app.tracker_manager import TrackerManager

def main():
    command = sys.argv[1]
    torrent_file = sys.argv[2]

    torrent_data = TorrentParser(torrent_file)

    if command == "read":
        torrent_data = torrent_data.return_full_data()
        torrent_data.pop("info")
        pprint(torrent_data)

    elif command == "download":

        torrent_file_data = torrent_data.return_full_data()
        ip_port_list = TrackerManager(torrent_file_data).get_peers()

        handshake_handler = TorrentHandshakeHandler(torrent_data)

        peer_pieces = PeersPieces(ip_port_list, handshake_handler)
        socket_with_pieces = peer_pieces.get_data()
        download = Download(socket_with_pieces, peer_pieces, torrent_data, handshake_handler)
        download.full_download()

        download.finalize_download_report()

if __name__ == "__main__":
    main()
