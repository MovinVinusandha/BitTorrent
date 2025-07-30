class FullFileDownload:
    def __init__(self, download, socket_with_pieces):
        self.download = download
        self.socket_with_pieces = socket_with_pieces
        self.full_download()

    def full_download(self):

        full_file = b""
        for ip_port, pieces_index in self.socket_with_pieces.items():
            ip, port = ip_port.split(":")
            file = self.download.download(ip, int(port), pieces_index)

            full_file += file

        with open("./downloaded_file.txt", "wb") as f:
            f.write(full_file)