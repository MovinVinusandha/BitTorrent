import sys
from app.torrentFile import TorrentRead
from app.hashGen import Hash
from app.peers import Peers
from app.handshakeMsg import Handshake

def main():
    command = sys.argv[1]
    torrent_file = sys.argv[2]

    torrent_read = TorrentRead(torrent_file)
    hash = Hash()
    peers = Peers()
    handshake = Handshake()

    if command == "read":
        torrent_data = torrent_read.get_data()
        print(torrent_data)

        hash_data = hash.get_data()
        print(hash_data)

    elif command == "download":
        handshake_msg = handshake.handshake_msg()
        print(handshake_msg)


if __name__ == "__main__":
    main()
