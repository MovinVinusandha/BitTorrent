import sys
from app.torrentFile import TorrentRead

def main():
    command = sys.argv[1]
    torrent_file = sys.argv[2]

    torrent_read = TorrentRead(torrent_file)

    if command == "read":
        data = torrent_read.get_data()
        print(data)



if __name__ == "__main__":
    main()
