import sys

from app.fullFileDownload import FullFileDownload
from app.torrentRead import TorrentRead

def main():
    command = sys.argv[1]
    torrent_file = sys.argv[2]

    torrent_data = TorrentRead(torrent_file)
    full_download = FullFileDownload()

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
        full_download.full_download()

if __name__ == "__main__":
    main()
