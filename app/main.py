import sys
from app.torrentFile import TorrentRead
from app.hashGen import Hash
from app.peers import Peers

def main():
    command = sys.argv[1]
    torrent_file = sys.argv[2]

    torrent_read = TorrentRead(torrent_file)
    hash = Hash()
    peers = Peers()

    if command == "read":
        torrent_data = torrent_read.get_data()
        print(torrent_data)

        hash_data = hash.get_data()
        print(hash_data)

    elif command == "download":
        peers_data = peers.get_peers_data()
        print(peers_data)


if __name__ == "__main__":
    main()
