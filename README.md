# BitTorrent Client (v0.1.0)

A robust, modular, and BEP-compliant BitTorrent client built entirely from scratch in Python. 

This client was engineered with a strict adherence to the Single Responsibility Principle (SRP) and is designed to handle real-world network anomalies, complex multi-file directory structures, and modern tracker protocols gracefully.

---

## Core Features

* **Dual-Protocol Tracker Support:** Communicates seamlessly with both legacy HTTP/HTTPS trackers and modern binary UDP trackers (BEP 15) to maximize peer discovery.
* **Resilient TCP Stream Parsing:** Implements dynamic, length-prefixed stream reading. The client safely processes unexpected network chatter (e.g., out-of-order `Keep-Alive`, `Have`, or `Choke` messages) without buffer overflows or data corruption.
* **Multi-File Assembly:** Automatically parses complex directory trees from torrent metadata, slices continuous byte streams, and recreates the exact original folder structures on disk.
* **Modern Networking:** Fully supports routing traffic to both IPv4 and IPv6 seeders.
* **Cryptographic Integrity:** Performs strict SHA-1 hash validation on every downloaded 16KB block-assembly to guarantee file authenticity.

---

## Prerequisites

To run this application, you will need
* **Python** `>= 3.14`
* **[uv](https://docs.astral.sh/uv/)** (Python package and project manager)

---

## Installation

###  1. Clone the repository to your local machine
   ```bash
   git clone https://github.com/MovinVinusandha/BitTorrent
   cd bittorrent-client
   ```

### 2. Sync the dependencies using uv
```bash
uv sync
   ```

## Usage

The client currently operates via a simple Command Line Interface (CLI).

* Read Torrent Metadata
To parse a .torrent file and output its metadata (trackers, file structure, hashes, and piece lengths) to the console
```bash
uv run main.py read <path/to/file.torrent>
```

* Download a Torrent
To connect to trackers, discover peers, perform handshakes, and download the files
```bash
uv run main.py download <path/to/file.torrent>
```
Note: Downloaded files and their respective directories will be automatically saved to a ./downloads folder in the project root.

## 🐳 Docker Deployment

If you prefer to run the client in an isolated environment without managing Python dependencies, you can use the provided `Dockerfile`.

### 1. Build the Image
Build the Docker image from the project root
```bash
docker build -t bittorrent-client .
```

### 2. Run the Container
To run the container and map your local ./downloads folder so that files persist on your host machine, use the following command

```bash
docker run --rm \
  -v "$(pwd):/app" \
  -v "$(pwd)/downloads:/app/downloads" \
  bittorrent-client download <your-torrent-file.torrent>
```

Explanation of the flags:

* ```-v "$(pwd):/app"``` : Mounts your current directory to the container so it can access your .torrent file.
* ```-v "$(pwd)/downloads:/app/downloads"``` : Maps your local downloads/ folder to the container's output directory, ensuring downloaded files are saved directly to your computer.