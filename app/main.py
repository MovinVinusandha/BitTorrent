import sys

from app.download import Download
from app.fullFileDownload import FullFileDownload
from app.torrentRead import TorrentRead
from app.peers import Peers

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

        download = Download(ip_port_list)
        FullFileDownload(download)

if __name__ == "__main__":
    main()
