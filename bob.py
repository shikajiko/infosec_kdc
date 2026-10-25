import argparse
from getpass import getpass

from common.crypto import decrypt
from common.network import create_server, receive_message
from common.protocol import parse_ticket
from common.utils import KEY_LENGTH


def handle_session(conn, addr, kb):
    ticket = receive_message(conn).decode("ascii")
    print(f"[{addr[0]}:{addr[1]}] received ticket: {ticket}")
    ks, id_a = parse_ticket(decrypt(kb, ticket))
    print(f"ticket valid: session with {id_a}, Ks = {ks}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    kb = getpass(f"Bob master key ({KEY_LENGTH} chars): ")
    server = create_server(args.host, args.port)
    print(f"Bob listening on {args.host}:{args.port}")
    while True:
        conn, addr = server.accept()
        with conn:
            try:
                handle_session(conn, addr, kb)
            except (ConnectionError, ValueError) as err:
                print(f"bad ticket from {addr[0]}: {err}")


if __name__ == "__main__":
    main()