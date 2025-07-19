import sys
from app.torrentFile import TorrentRead

def main():
    command = sys.argv[1]
    torrent_file = sys.argv[2]

    torrent_read = TorrentRead(torrent_file)

    if command == "read":
        print("torrent dict :", torrent_read.decode_bencode())

if __name__ == "__main__":
    main()
