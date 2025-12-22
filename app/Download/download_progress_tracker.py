class DownloadProgressTracker:
    """
    Single Responsibility: Track download progress only
    - Track completed pieces
    - Calculate progress percentages
    - Provide progress reports
    """

    def __init__(self, total_pieces):
        self.total_pieces = total_pieces
        self.downloaded_pieces = set()
        self.piece_sizes = {}
        self.failed_pieces = set()
        self.start_time = None
        self.completion_times = {}

    def mark_piece_started(self, piece_index):
        """Mark when piece download starts"""
        import time
        if self.start_time is None:
            self.start_time = time.time()

    def mark_piece_completed(self, piece_index, piece_size):
        """Mark piece as successfully downloaded"""
        import time
        self.downloaded_pieces.add(piece_index)
        self.piece_sizes[piece_index] = piece_size
        self.completion_times[piece_index] = time.time()

        # Remove from failed if it was there
        self.failed_pieces.discard(piece_index)

        print(f"Progress: {self.get_progress_percentage():.1f}% "
              f"({len(self.downloaded_pieces)}/{self.total_pieces} pieces)")

    def mark_piece_failed(self, piece_index):
        """Mark piece as failed"""
        self.failed_pieces.add(piece_index)
        # Remove from downloaded if it was there
        self.downloaded_pieces.discard(piece_index)

    def get_progress_percentage(self):
        """Get download progress as percentage"""
        if self.total_pieces == 0:
            return 100.0
        return (len(self.downloaded_pieces) / self.total_pieces) * 100

    def get_remaining_pieces(self, available_pieces):
        """Get list of pieces that still need downloading"""
        return [p for p in available_pieces
                if p not in self.downloaded_pieces and p not in self.failed_pieces]

    def get_progress_report(self):
        """Get detailed progress report"""
        import time

        current_time = time.time()
        elapsed_time = current_time - self.start_time if self.start_time else 0

        total_bytes = sum(self.piece_sizes.values())
        avg_speed = total_bytes / elapsed_time if elapsed_time > 0 else 0

        return {
            'total_pieces': self.total_pieces,
            'downloaded_pieces': len(self.downloaded_pieces),
            'failed_pieces': len(self.failed_pieces),
            'progress_percentage': self.get_progress_percentage(),
            'total_bytes_downloaded': total_bytes,
            'elapsed_time_seconds': elapsed_time,
            'average_speed_bytes_per_second': avg_speed,
            'is_complete': len(self.downloaded_pieces) == self.total_pieces
        }