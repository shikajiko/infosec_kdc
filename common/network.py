import socket
import struct

HEADER = struct.Struct("!I")

def create_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    return server


def connect_to(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock


def send_message(sock, data):
    sock.sendall(HEADER.pack(len(data)) + data)


def _receive_exact(sock, size):
    chunks = []
    while size > 0:
        chunk = sock.recv(size)
        if not chunk:
            raise ConnectionError("connection closed")
        chunks.append(chunk)
        size -= len(chunk)
    return b"".join(chunks)


def receive_message(sock):
    (length,) = HEADER.unpack(_receive_exact(sock, HEADER.size))
    return _receive_exact(sock, length)