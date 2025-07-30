class FullFileDownload:
    def __init__(self, download):
        self.download = download
        self.full_download()

    def full_download(self):
        socket_with_pieces = self.download.pieces_with_socket()

        full_file = b""
        for ip_port, pieces_index in socket_with_pieces.items():
            ip, port = ip_port.split(":")
            file = self.download.download(ip, int(port), pieces_index)

            full_file += file

        with open("./downloaded_file.txt", "wb") as f:
            f.write(full_file)