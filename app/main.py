import sys

from app.TorrentHandshakeHandler import TorrentHandshakeHandler
from app.download import Download
from app.torrentRead import TorrentRead
from app.peers import Peers
from app.peersPieces import PeersPieces

def main():
    command = sys.argv[1]
    torrent_file = sys.argv[2]

    torrent_data = TorrentRead(torrent_file)

    if command == "read":
        torrent_data = torrent_data.return_full_data()

        print("Tracker URL :", torrent_data["tracker url"])
        print("Created by :", torrent_data["created by"])
        print("File length :", torrent_data["length"])
        print("Piece length :", torrent_data["piece length"])
        print("File Name :", torrent_data["name"])
        print("Info hash :", torrent_data["info hash"])
        print("Pieces hash :", torrent_data["pieces hash"])

    elif command == "download":

        torrent_file_data = torrent_data.return_full_data()
        ip_port_list = Peers(torrent_file_data).get_data()["ip"]

        handshake_handler = TorrentHandshakeHandler(torrent_data)

        peer_pieces = PeersPieces(ip_port_list, handshake_handler)
        socket_with_pieces = peer_pieces.get_data()
        download = Download(socket_with_pieces, peer_pieces, torrent_data, handshake_handler)

        download.finalize_download_report()

if __name__ == "__main__":
    main()
