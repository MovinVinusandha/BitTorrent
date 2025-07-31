from app.Download.FileAssembler import FileAssembler

class FullFileDownload:
    def __init__(self, download, socket_with_pieces, output_file_path="./downloaded_file.txt"):
        self.download = download
        self.socket_with_pieces = socket_with_pieces
        self.file_assembler = FileAssembler(output_file_path)
        self.full_download()

    def full_download(self):

        for ip_port, pieces_index in self.socket_with_pieces.items():
            ip, port = ip_port.split(":")
            file = self.download.download(ip, int(port), pieces_index)

            self.file_assembler.save_to_file(file)


