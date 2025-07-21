import sys
from app.torrentFile import TorrentRead
from app.hashGen import Hash
from app.peers import Peers
from app.handshakeMsg import HandshakeMsg
from app.download import Download

def main():
    command = sys.argv[1]
    torrent_file = sys.argv[2]

    torrent_read = TorrentRead(torrent_file)
    hash = Hash()
    peers = Peers()
    handshake_msg = HandshakeMsg()
    download = Download()

    if command == "read":
        torrent_data = torrent_read.get_data()
        print(torrent_data)

        hash_data = hash.get_data()
        print(hash_data)

    elif command == "download":
        download.handshake_connection()


if __name__ == "__main__":
    main()
