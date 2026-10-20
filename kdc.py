import argparse

from common.network import create_server, receive_message
from common.protocol import parse_request


def handle_request(conn, addr):
    data = receive_message(conn)
    id_a, id_b, n1 = parse_request(data)
    print(f"[{addr[0]}:{addr[1]}] request from {id_a} for {id_b}, N1 = {n1}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    server = create_server(args.host, args.port)
    print(f"KDC listening on {args.host}:{args.port}")
    while True:
        conn, addr = server.accept()
        with conn:
            try:
                handle_request(conn, addr)
            except (ConnectionError, ValueError) as err:
                print(f"bad request from {addr[0]}: {err}")


if __name__ == "__main__":
    main()