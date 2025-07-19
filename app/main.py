import sys
from app.torrentFile import TorrentRead
from app.hashGen import Hash

def main():
    command = sys.argv[1]
    torrent_file = sys.argv[2]

    torrent_read = TorrentRead(torrent_file)
    hash = Hash()

    if command == "read":
        torrent_data = torrent_read.get_data()
        print(torrent_data)

        hash_data = hash.get_data()
        print(hash_data)



if __name__ == "__main__":
    main()
